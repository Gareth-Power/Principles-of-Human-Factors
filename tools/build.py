# Builds js/content.js for the field guide from blocks.json (convert.py's output).
# Every word comes from the Word document; this script only decides each
# paragraph's role (heading, list, callout, figure) and which page it's on.
import sys, re, json, html
sys.stdout.reconfigure(encoding="utf-8")
blocks_path, out_path, img_dir = sys.argv[1:4]
B = {b['i']: b for b in json.load(open(blocks_path, encoding='utf-8')) if 'html' in b}

# id, index label, group, first block, end (exclusive), title block
PAGES = [
  ('welcome',       'Welcome',                               'start',       0,   29,  0),
  ('how-to-use',    'How to use this guide',                 'start',       29,  42,  29),
  ('aims',          'Aims, objectives and outcomes',         'start',       42,  51,  42),
  ('performance',   'Human performance',                     'foundations', 51,  65,  51),
  ('operator',      'Operator condition',                    'foundations', 65,  124, 65),
  ('startle',       'Startle syndrome',                      'foundations', 124, 187, 124),
  ('culture',       'Culture',                               'foundations', 187, 264, 187),
  ('systems',       'Health systems',                        'foundations', 264, 280, 264),
  ('crises',        'Threats, errors, harm and crises',      'foundations', 280, 335, 280),
  ('human-factors', 'Human factors',                         'foundations', 335, 398, 335),
  ('technology',    'Technology',                            'technical',   398, 443, 398),
  ('knowledge',     'Knowledge, skill and experience',       'technical',   443, 481, 443),
  ('workload',      'Workload management',                   'cognitive',   481, 535, 481),
  ('awareness',     'Situational awareness',                 'cognitive',   535, 586, 535),
  ('decisions',     'Decision making and problem solving',   'cognitive',   586, 630, 586),
  ('leadership',    'Leadership, followership and teamwork', 'behavioural', 630, 692, 630),
  ('communication', 'Communication',                         'behavioural', 692, 750, 692),
  ('professional',  'Professional standards',                'behavioural', 750, 780, 750),
  ('summary',       'Summary',                               'reference',   780, 822, 780),
  ('glossary',      'Glossary',                              'reference',   839, 872, 839),
  ('references',    'References and acknowledgement',        'reference',   822, 839, 822),
]
GROUPS = [
  ('start', 'Start here'), ('foundations', 'Foundations'),
  ('technical', 'Technical skills'), ('cognitive', 'Cognitive skills'),
  ('behavioural', 'Behavioural skills'), ('reference', 'Reference'),
]

# Callouts: first block, last block (inclusive), kind. Kinds follow the
# document's own labels (NOTE / TOOL / CASE).
CALLOUTS = [
  (39, 40, 'note'), (73, 75, 'case'), (77, 80, 'case'), (116, 117, 'note'),
  (119, 122, 'tool'), (131, 131, 'note'), (148, 182, 'tool'), (184, 184, 'note'),
  (219, 220, 'case'), (222, 224, 'case'), (239, 240, 'note'), (242, 261, 'tool'),
  (312, 312, 'note'), (414, 421, 'tool'), (423, 424, 'case'), (437, 439, 'note'),
  (468, 472, 'tool'), (474, 477, 'note'), (505, 506, 'tool'), (509, 517, 'tool'),
  (519, 519, 'note'), (521, 525, 'tool'), (527, 531, 'tool'), (557, 562, 'tool'),
  (565, 566, 'case'), (568, 582, 'tool'), (607, 608, 'tool'), (616, 617, 'tool'),
  (626, 628, 'note'), (681, 689, 'tool'), (720, 726, 'tool'), (728, 733, 'tool'),
  (735, 747, 'tool'), (760, 764, 'tool'), (774, 776, 'note'), (823, 827, 'note'),
]
# Paragraphs whose own role isn't obvious from Word's styles.
ROLE = {
  1: 'subtitle', 19: 'pull', 20: 'p', 21: 'quote', 33: 'lead', 30: 'kicker',
  44: 'h2', 53: 'h2', 66: 'h3', 74: 'stat', 189: 'lead', 190: 'lead', 191: 'lead',
  196: 'p', 197: 'p', 198: 'p', 247: 'lead', 249: 'lead', 300: 'ref', 332: 'ref',
  314: 'h3', 351: 'lead', 358: 'pull', 362: 'h2', 390: 'lead', 400: 'h2',
  444: 'lead', 483: 'h2', 535: 'h2', 586: 'h2', 632: 'h2', 692: 'h2', 750: 'h2',
  635: 'quote', 636: 'cite', 638: 'quote', 639: 'cite', 640: 'pull', 754: 'quote',
  755: 'cite', 782: 'lead', 783: 'lead', 342: 'pull', 340: 'p', 565: 'h3',
  767: 'h4', 594: 'h3', 610: 'h3', 619: 'h3', 613: 'h4',
  322: 'h4', 160: 'h4', 166: 'h4', 173: 'h4', 178: 'h4', 150: 'h4', 157: 'h4',
  736: 'h4', 740: 'h4', 743: 'h4', 751: 'h3', 766: 'h3', 794: 'h3',
  280: 'title', 443: 'title', 25: 'p', 279: 'ref', 75: 'ref', 80: 'ref',
  562: 'ref', 642: 'ref', 664: 'ref', 826: 'cite', 827: 'p', 825: 'quote',
  34: 'h3',
}
for i in range(829, 836): ROLE[i] = 'refitem'

ALT = {
  'image1': 'Illustration: staff and a patient talking in a bright hospital waiting area.',
  'image2': 'Diagram: technical, cognitive and behavioural skills pass through operator condition, culture and health systems.',
  'image3': 'Illustration: a tired night-shift worker hurrying down a corridor carrying a stack of paperwork.',
  'image4': 'Illustration: a startled surgeon holding a clipboard in an operating theatre.',
  'image5': 'Illustration: The startled human - fight, flight, freeze and fawn.',
  'image6': 'Illustration: three colleagues walking and talking through a colourful town.',
  'image7': 'Illustration: a health system made of people, places, tools and rules.',
  'image8': 'Diagram: the crisis chain - threats lead to errors, errors to harm, harm to crisis.',
  'image9': 'Diagram: bow-tie - threats lead to an error, which leads to harms; prevention before, recovery after.',
  'image10': 'Illustration: a team caring for a patient in a hospital bed.',
  'image11': 'Illustration: the three pillars of human factors - technical, cognitive and behavioural skills.',
  'image12': 'Diagram: the human factors model - three pillars of three domains each.',
  'image13': 'Illustration: the SHELL model of the socio-technical interface.',
  'image14': 'Illustration: workload management - a nurse surrounded by disruptions, fear, new tasks and uncertainty.',
  'image15': 'Diagram: the Eisenhower decision matrix - do, decide, delegate, delete.',
  'image16': 'Illustration: situational awareness - notice, understand, think ahead.',
  'image17': 'Diagram: the capacity bucket - workload fills cognitive capacity, leaving situational awareness above it.',
  'image18': 'Illustration: the 2-challenge rule - prompt, direct, intervene.',
  'image19': 'Illustration: the T-DODAR cycle.',
  'image20': 'Diagram: T-DODAR steps - time, diagnosis, options, decide, assign and act, review - repeated if it did not work.',
  'image21': 'Illustration: the innovation cycle - problem, idea, prototype, test, fail and learn, adapt or adopt.',
  'image22': 'Illustration: five common cognitive biases in healthcare.',
  'image23': 'Illustration: What is leadership? A leader guiding people along a path from A to B.',
  'image24': 'Illustration: teamwork and followership - lead, follow, work together.',
  'image25': 'Illustration: hierarchy and authority - a steep and a shallow authority gradient.',
  'image26': 'Illustration: what is communication - a sender, a receiver, a message and a channel.',
  'image27': 'Cartoon: a sinking sailor calls "We are sinking!" and the radio operator replies "What are you thinking about?"',
  'image28': 'Illustration: closed-loop communication - instruction, readback, verification.',
}

def strip_tags(s): return html.unescape(re.sub(r'<[^>]+>', '', s))
def role_of(b):
  i = b['i']
  if i in ROLE: return ROLE[i]
  if b['imgs']: return 'img'
  if b['smartart']: return 'smartart'
  st, txt = b['st'], b['text'].strip()
  if st == 'Quote': return 'quote'
  if st == 'Caption': return 'caption'
  if txt.startswith(('Reference:', 'References:')): return 'ref'
  if b['list']: return 'li'
  if st == 'ListParagraph' and re.match(r'-\s', txt): return 'dash'
  if re.match(r'-\s', txt): return 'dash'
  if st in ('Heading1', 'Heading2'): return 'h2'
  if st == 'Heading4': return 'h3' if b['bold'] else 'lead'
  if b['bold']: return 'h3'
  return 'p'

def figure(b):
  out = []
  for im in b['imgs']:
    name = re.sub(r'\..*$', '', im['src'].split('/')[-1])
    alt = ALT[name]
    over = ''
    if name == 'image9' and b['tbs']:
      if 'CRISIS' in b['tbs']:
        over = ('<span class="bt-arrow">Risk<span>x</span></span>'
                '<span class="bt-crisis">' + ''.join('<span>%s</span>' % c for c in 'CRISIS') + '</span>')
        name_cls = 'bowtie bowtie-a'
      else:
        over = ''.join('<span class="bt-bar bt-%s"><span>%s</span></span>' % (k.lower()[:4], k) for k in ['Barriers', 'Traps', 'Mitiagations'])
        name_cls = 'bowtie bowtie-b'
      out.append('<figure class="fig %s" id="b%d"><div class="fig-in"><img src="img/%s.webp" alt="%s" loading="lazy">%s</div></figure>'
                 % (name_cls, b['i'], name, html.escape(alt), over))
      continue
    with Image_size(name) as (w, h):
      cls = 'fig portrait' if h > w * 1.1 else 'fig'
      out.append('<figure class="%s" id="b%d"><button class="fig-in zoom" type="button" aria-label="Enlarge image"><img src="img/%s.webp" alt="%s" width="%d" height="%d" loading="lazy"></button></figure>'
                 % (cls, b['i'], name, html.escape(alt), w, h))
  return ''.join(out)

SIZES = {}
from PIL import Image
import glob, os
for f in glob.glob(img_dir + '/*.webp'):
  SIZES[os.path.basename(f)[:-5]] = Image.open(f).size
from contextlib import contextmanager
@contextmanager
def Image_size(name):
  yield SIZES[name]

def linkify(h):
  # plain-text URLs become links; the visible text is unchanged
  return re.sub(r'(?<!href=")(?<!">)(https?://[^\s<]+)', lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>' % (m.group(1).rstrip('.'), m.group(1)) , h)

def tidy(h):
  # Word's leading/trailing tabs and spaces are layout, not words
  return re.sub(r'^(\s|&nbsp;)+|(\s)+$', '', h.replace('\t', ' ')).replace('<a href=', '<a target="_blank" rel="noopener" href=')

def render_block(b, r):
  h = tidy(b['html'])
  i = b['i']
  if r == 'skip': return ''
  if r == 'img': return figure(b)
  if r == 'smartart':
    steps = ['Problem', 'Idea', 'Prototype', 'Test &amp; Trial', 'Fail &amp; Learn', 'Adapt / Adopt']
    return '<ol class="cycle" id="b%d">%s</ol>' % (i, ''.join('<li>%s</li>' % s for s in steps))
  if r in ('h2', 'h3', 'h4'):
    return '<%s id="b%d">%s</%s>' % (r, i, re.sub(r'</?b>', '', h), r)
  cls = {'lead': 'lead', 'stat': 'stat', 'quote': 'quote', 'cite': 'cite', 'pull': 'pull', 'ref': 'ref',
         'refitem': 'refitem', 'caption': 'caption', 'subtitle': 'subtitle', 'kicker': 'kicker', 'p': ''}.get(r, '')
  if r in ('ref', 'refitem'): h = linkify(h)
  if r == 'quote': return '<blockquote class="quote" id="b%d"><p>%s</p></blockquote>' % (i, h)
  return '<p%s id="b%d">%s</p>' % (' class="%s"' % cls if cls else '', i, h)

def render_range(ids):
  """render blocks in order, grouping consecutive list items into lists"""
  out, k = [], 0
  while k < len(ids):
    b = B[ids[k]]; r = role_of(b)
    if r in ('li', 'dash'):
      items = []
      kind = 'ol' if (r == 'li' and b['list'] and b['list'][0] == 'decimal') else 'ul'
      while k < len(ids):
        bb = B[ids[k]]; rr = role_of(bb)
        if rr != r: break
        if rr == 'li' and bb['list'] and ('ol' if bb['list'][0] == 'decimal' else 'ul') != kind: break
        h = tidy(bb['html'])
        if rr == 'dash': h = re.sub(r'^-\s+', '', h)
        lvl = bb['list'][1] if bb['list'] else 0
        items.append('<li id="b%d"%s>%s</li>' % (bb['i'], ' class="l%d"' % lvl if lvl else '', h))
        k += 1
      out.append('<%s class="%s">%s</%s>' % (kind, 'dash' if r == 'dash' else 'list', ''.join(items), kind))
      continue
    out.append(render_block(b, r)); k += 1
  return ''.join(out)

LABEL = {'note': 'Note', 'tool': 'Tool', 'case': 'Case'}
def split_label(b):
  """'TOOL: Sterile cockpit' -> ('TOOL', 'Sterile cockpit'); keeps every word"""
  t = tidy(b['html'])
  m = re.match(r'^(?:<b>)?(?:<i>)?(NOTE|TOOL|CASE|Note)(?:</i>)?:?(?:</i>)?(?:</b>)?(?:<b>)?:?\s*(.*)$', t, re.S)
  if m:
    rest = m.group(2)
    rest = re.sub(r'^(</?[bi]>|\s|:)+', '', rest)
    rest = re.sub(r'</?b>', '', rest) if re.fullmatch(r'(<b>)?[^<]*(</b>)?', rest) else rest
    return m.group(1), rest
  m = re.match(r'^(?:<b>)?TOOL for (.*?)(</b>)?$', t)
  if m: return 'TOOL', 'for ' + m.group(1)
  return None, t

pages, tools, search = [], [], []
order = [p[0] for p in PAGES]
cbyStart = {c[0]: c for c in CALLOUTS}
used = set()
for pid, label, group, a, z, tix in PAGES:
  ids = sorted(i for i in B if a <= i < z)
  title_html = re.sub(r'</?[bi]>', '', tidy(B[tix]['html'])) if tix is not None else label
  body, k = [], 0
  ids_body = [i for i in ids if i != tix]
  used.update(ids)
  if pid == 'glossary':
    items = []
    for i in ids_body:
      t = tidy(B[i]['html']); term, _, defn = t.partition(' — ')
      items.append('<div class="gl-row" id="b%d"><dt>%s</dt><dd>%s</dd></div>' % (i, term, defn))
      search.append({'p': pid, 'b': 'b%d' % i, 'k': 'glossary', 't': strip_tags(term), 'x': strip_tags(defn)})
    pages.append({'id': pid, 'label': label, 'group': group, 'title': title_html, 'html': '<dl class="glossary">%s</dl>' % ''.join(items)})
    continue
  while k < len(ids_body):
    i = ids_body[k]
    if i in cbyStart:
      s, e, kind = cbyStart[i]
      inner = [j for j in ids_body if s <= j <= e]
      tag, head = split_label(B[s])
      rest = inner[1:]
      if tag is None:
        head_html, rest = '', inner
      else:
        head_html = '<h3 class="co-title">%s</h3>' % head if head else ''
      lead_word = tag if tag else ''
      card = ('<aside class="co co-%s" id="b%d"><div class="co-tag">%s</div>%s<div class="co-body">%s</div></aside>'
              % (kind, s, lead_word or LABEL[kind].upper(), head_html, render_range(rest)))
      body.append(card)
      if kind == 'tool':
        tools.append({'page': pid, 'label': label, 'id': 'b%d' % s, 'title': strip_tags(head) if head else strip_tags(B[s]['html']), 'html': card})
      search.append({'p': pid, 'b': 'b%d' % s, 'k': kind, 't': strip_tags(head) if head else label,
                     'x': ' '.join(B[j]['text'] for j in rest)})
      k += len(inner)
      continue
    # gather a run up to the next callout
    run = []
    while k < len(ids_body) and ids_body[k] not in cbyStart:
      run.append(ids_body[k]); k += 1
    body.append(render_range(run))
    sec = label
    for j in run:
      r = role_of(B[j])
      if r in ('h2', 'h3'): sec = B[j]['text'].strip()
      if B[j]['text'].strip() and r not in ('skip',):
        search.append({'p': pid, 'b': 'b%d' % j, 'k': 'h' if r in ('h2', 'h3', 'h4') else 'text', 't': sec, 'x': B[j]['text'].strip()})
  pages.append({'id': pid, 'label': label, 'group': group, 'title': title_html, 'html': ''.join(body)})
  search.append({'p': pid, 'b': '', 'k': 'page', 't': label, 'x': strip_tags(title_html)})

missing = [i for i in B if i not in used and (B[i]['text'].strip() or B[i]['imgs'])]
for i in missing: print('NOT PLACED:', i, B[i]['text'][:80])
data = {'groups': [{'id': g, 'label': l} for g, l in GROUPS], 'pages': pages, 'tools': tools, 'search': search}
open(out_path, 'w', encoding='utf-8').write(
  '/* Generated from Human-Factors-Field-Guide-for-review 3.docx by build.py - do not edit by hand. */\n'
  # No em dashes anywhere (the user's call, 2026-11-09): each becomes a spaced hyphen.
  'window.GUIDE = ' + re.sub(r'\s*—\s*', ' - ', json.dumps(data, ensure_ascii=False)) + ';\n')
print('pages', len(pages), 'tools', len(tools), 'search', len(search))
