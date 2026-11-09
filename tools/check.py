# Every paragraph of the Word file must appear, word for word, in the app.
import sys, json, re, html
sys.stdout.reconfigure(encoding='utf-8')
blocks=[b for b in json.load(open(sys.argv[1],encoding='utf-8')) if 'text' in b]
js=open(sys.argv[2],encoding='utf-8').read()
data=json.loads(js[js.index('{'):js.rstrip().rindex(';')])
def text(h):
  h=re.sub(r'<(li|p|dt|dd|h\d|div|blockquote|span class="bt[^"]*")[^>]*>',' ',h)
  return html.unescape(re.sub(r'<[^>]+>','',h))
def n(s): return re.sub(r'\s+',' ',s.replace('\u00a0',' ')).strip()
allt=n(' '.join(text(p['title'])+' '+text(p['html']) for p in data['pages']))
bad=0; words_doc=0
for b in blocks:
  t=n(re.sub(r'\s*—\s*',' - ',b['text']))  # em dashes are spaced hyphens in the app
  t2=re.sub(r'^- ','',t); t3=re.sub(r'^(NOTE|TOOL|CASE|Note):\s*',r'\1 ',t); t4=t.replace(' - ',' ',1)
  words_doc+=len(t.split())
  if t and not any(x in allt for x in (t,t2,t3,t4)):
    bad+=1; print('MISSING', b['i'], repr(t[:120]))
  for tb in b.get('tbs',[]):
    if tb not in allt.replace(' ','') : print('TEXTBOX MISSING', b['i'], tb)
# no extra words: rendered words that aren't in the doc
doc=n(' '.join(b['text'] for b in blocks)+' '+' '.join(' '.join(b.get('tbs',[])) for b in blocks))
dw=set(re.findall(r"[\w’']+",doc)); rw=set(re.findall(r"[\w’']+",allt))
print('paragraphs missing:',bad,'| doc words:',words_doc,'| words in app not in doc:',sorted(rw-dw)[:40])
