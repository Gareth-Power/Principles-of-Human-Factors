import sys, re, json, html, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")
d=sys.argv[1]
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
MC='{http://schemas.openxmlformats.org/markup-compatibility/2006}'
WPS='{http://schemas.microsoft.com/office/word/2010/wordprocessingShape}'
rels={r.get('Id'):(r.get('Target'),r.get('TargetMode')) for r in ET.parse(d+'/word/_rels/document.xml.rels').getroot()}
# numbering: numId -> ilvl -> numFmt
num=ET.parse(d+'/word/numbering.xml').getroot()
absf={}
for a in num.findall(W+'abstractNum'):
    absf[a.get(W+'abstractNumId')]={l.get(W+'ilvl'):(l.find(W+'numFmt').get(W+'val') if l.find(W+'numFmt') is not None else '?') for l in a.findall(W+'lvl')}
numfmt={n.get(W+'numId'):absf.get(n.find(W+'abstractNumId').get(W+'val'),{}) for n in num.findall(W+'num')}
styles=ET.parse(d+'/word/styles.xml').getroot()
body=ET.parse(d+'/word/document.xml').getroot().find(W+'body')
def on(rpr,tag):
    if rpr is None: return False
    e=rpr.find(W+tag)
    return e is not None and e.get(W+'val') not in ('0','false')
def runs(p, skip_textboxes=True):
    """yield (text, bold, italic, href) and images, in order; ignores mc:Fallback and text inside drawings (text boxes)"""
    out=[]
    def walk(el, href=None):
        for c in el:
            if c.tag==MC+'AlternateContent':
                ch=c.find(MC+'Choice')
                if ch is not None: walk(ch, href)
                continue
            if c.tag==W+'hyperlink':
                rid=c.get(R+'id'); h=rels.get(rid,(None,))[0] if rid else None
                walk(c, h); continue
            if c.tag==W+'r':
                rpr=c.find(W+'rPr'); b=on(rpr,'b'); i=on(rpr,'i')
                va=rpr.find(W+'vertAlign').get(W+'val') if rpr is not None and rpr.find(W+'vertAlign') is not None else None
                for e in c:
                    if e.tag==W+'t': out.append(('t',e.text or '',b,i,href,va))
                    elif e.tag==W+'tab': out.append(('t','\t',b,i,href,va))
                    elif e.tag==W+'br': out.append(('br',))
                    elif e.tag==W+'drawing' or e.tag==MC+'AlternateContent':
                        WP='{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
                        ext=e.find('.//'+WP+'extent'); dp=e.find('.//'+WP+'docPr')
                        for bl in e.iter(A+'blip'): out.append(('img',rels[bl.get(R+'embed')][0],int(ext.get('cx')) if ext is not None else 0,(dp.get('descr') or dp.get('title') or '') if dp is not None else ''))
                        for tb in e.iter(WPS+'txbx'):
                            t=''.join(x.text or '' for x in tb.iter(W+'t'))
                            out.append(('tb',t))
                        if any(x.tag.endswith('}relIds') for x in e.iter()): out.append(('smartart',))
                continue
            if c.tag in (W+'smartTag',W+'sdt',W+'sdtContent',W+'ins',W+'fldSimple'): walk(c,href); continue
    walk(p)
    return out
def inline(rs):
    h=[];
    for r in rs:
        if r[0]!='t': 
            if r[0]=='br': h.append('<br>')
            continue
        _,t,b,i,href,va=r
        s=html.escape(t,quote=False)
        if va=='superscript': s='<sup>'+s+'</sup>'
        if va=='subscript': s='<sub>'+s+'</sub>'
        if i: s='<i>'+s+'</i>'
        if b: s='<b>'+s+'</b>'
        if href: s='<a href="%s">%s</a>'%(html.escape(href),s)
        h.append(s)
    s=''.join(h)
    for tag in ('b','i'):
        s=re.sub(r'</%s>(\s*)<%s>'%(tag,tag),r'\1',s)
    return s
blocks=[]
for idx,el in enumerate(body):
    if el.tag!=W+'p': 
        if el.tag==W+'tbl': blocks.append({'i':idx,'k':'TABLE'})
        continue
    ppr=el.find(W+'pPr')
    st=ppr.find(W+'pStyle').get(W+'val') if ppr is not None and ppr.find(W+'pStyle') is not None else ''
    np=ppr.find(W+'numPr') if ppr is not None else None
    lst=None
    if np is not None and np.find(W+'numId') is not None:
        nid=np.find(W+'numId').get(W+'val'); lv=np.find(W+'ilvl').get(W+'val') if np.find(W+'ilvl') is not None else '0'
        if nid!='0': lst=(numfmt.get(nid,{}).get(lv,'?'),int(lv),nid)
    rs=runs(el)
    txt=''.join(r[1] for r in rs if r[0]=='t')
    imgs=[{'src':r[1],'cx':r[2],'alt':r[3]} for r in rs if r[0]=='img']
    tbs=[r[1] for r in rs if r[0]=='tb']
    sa=any(r[0]=='smartart' for r in rs)
    tr=[r for r in rs if r[0]=='t' and r[1].strip()]
    allb=bool(tr) and all(r[2] for r in tr)
    if not txt.strip() and not imgs and not sa: continue
    blocks.append({'i':idx,'st':st,'list':lst,'bold':allb,'html':inline(rs).strip(),'text':txt,'imgs':imgs,'tbs':tbs,'smartart':sa})
json.dump(blocks,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=0)
for b in blocks:
    if b.get('k'): print(b); continue
    print(b['i'],b['st'] or '-', b['list'] or '', 'B' if b['bold'] else '', '|', b['html'][:110], b['imgs'] or '', b['tbs'] or '', 'SMARTART' if b['smartart'] else '') if b['imgs'] else None
