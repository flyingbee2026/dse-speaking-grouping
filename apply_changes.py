#!/usr/bin/env python3
# Applies the requested changes to the grouping page:
#  1. English only (no Chinese anywhere)
#  2. two group cards per row on wide screens
#  3. A B C D laid out horizontally in one row (flex, not a grid)
#  4. "Candidate 12" on a single line inside each chip
import io, sys

PATH = '/root/dse-grouping/index.html'
src = io.open(PATH, encoding='utf-8').read()

pairs = []

def sub(old, new, label):
    pairs.append((old, new, label))

# ---------- 1. English-only copy ----------
sub('<title>DSE Speaking Practice \u00b7 Random Grouping \u96a8\u6a5f\u5206\u7d44</title>',
    '<title>DSE Speaking Practice \u00b7 Random Grouping</title>', 'title')

sub('    <h1>DSE Speaking Practice<br><span class="hl">\u96a8\u6a5f\u5206\u7d44</span></h1>',
    '    <h1>DSE Speaking Practice<br><span class="hl">Random Grouping</span></h1>', 'h1')

sub('    <p class="sub">Paper 4 Group Discussion &mdash; Random Grouping</p>',
    '    <p class="sub">Paper 4 Group Discussion &mdash; Class-Number Shuffler</p>', 'subtitle')

sub('<span class="flabel" id="lb-range">Class number \u73ed\u865f</span>',
    '<span class="flabel" id="lb-range">Class number</span>', 'label range')

sub('<span class="flabel" id="lb-groups">Number of groups \u7d44\u6578</span>',
    '<span class="flabel" id="lb-groups">Number of groups</span>', 'label groups')

sub('<span class="to">to \u81f3</span>', '<span class="to">to</span>', 'to separator')

sub('&#127922; Shuffle \u62bd\u7c64\u5206\u7d44</button>', '&#127922; Shuffle</button>', 'shuffle button')

sub('&#128256; Shuffle again \u91cd\u65b0\u5206\u7d44</button>', '&#128256; Shuffle again</button>', 'shuffle again')
sub('&#128203; Copy \u8907\u88fd\u540d\u55ae</button>', '&#128203; Copy list</button>', 'copy button')
sub('&#128424; Print \u5217\u5370</button>', '&#128424; Print</button>', 'print button')

sub('>Tap two candidates to swap them \u9ede\u9078\u5169\u4f4d\u8003\u751f\u5373\u53ef\u5c0d\u8abf</p>',
    '>Tap two candidates to swap them</p>', 'hint line')

sub('like the real DSE Paper 4 group discussion.<br>\u6bcf\u7d44\u6700\u591a 4 \u4f4d\u8003\u751f\uff0c\u4ee5 A&ndash;D \u6a19\u793a\u5ea7\u4f4d\u6b21\u5e8f\u3002</p>',
    'like the real DSE Paper 4 group discussion.</p>', 'footer')

sub('This page needs JavaScript. \u9019\u500b\u7db2\u9801\u9700\u8981\u958b\u555f JavaScript\u3002',
    'This page needs JavaScript.', 'noscript')

sub("No groups yet \u9084\u6c92\u6709\u5206\u7d44<br>Press &#127922; Shuffle \u62bd\u7c64\u5206\u7d44 \u958b\u59cb",
    "No groups yet<br>Press &#127922; Shuffle to start", 'empty state')

sub("var DEFAULT_HINT = 'Tap two candidates to swap them \u9ede\u9078\u5169\u4f4d\u8003\u751f\u5373\u53ef\u5c0d\u8abf';",
    "var DEFAULT_HINT = 'Tap two candidates to swap them';", 'default hint')

sub("showMsg('Please enter the class-number range, e.g. 1 to 15.<br>\u8acb\u8f38\u5165\u73ed\u865f\u7bc4\u570d\uff0c\u4f8b\u5982 1 \u81f3 15\u3002', 'err');",
    "showMsg('Please enter the class-number range, e.g. 1 to 15.', 'err');", 'err range')

sub("showMsg('Please enter the number of groups.<br>\u8acb\u8f38\u5165\u7d44\u6578\u3002', 'err');",
    "showMsg('Please enter the number of groups.', 'err');", 'err groups')

sub("showMsg('Invalid class-number range \u73ed\u865f\u7bc4\u570d\u4e0d\u6b63\u78ba (1&ndash;99\uff0c\u8d77\u9ede\u4e0d\u53ef\u5927\u65bc\u7d42\u9ede)\u3002', 'err');",
    "showMsg('Invalid class-number range (1&ndash;99, start must not be larger than end).', 'err');", 'err invalid range')

sub("showMsg('Number of groups must be 1&ndash;40 \u7d44\u6578\u5fc5\u9808\u70ba 1&ndash;40\u3002', 'err');",
    "showMsg('Number of groups must be 1&ndash;40.', 'err');", 'err group range')

sub(").<br>\u7d44\u6578\u4e0d\u53ef\u591a\u65bc\u8003\u751f\u4eba\u6578 (' + nums.length + ')\u3002', 'err');",
    ").', 'err');", 'err too many groups')

sub("showMsg('\u6bcf\u7d44\u7d04 ' + maxSize + ' \u4eba &mdash; DSE \u5c0f\u7d44\u8a0e\u8ad6\u901a\u5e38 3&ndash;4 \u4eba\uff0c\u53ef\u8003\u616e\u5206\u6210 ' + Math.ceil(nums.length / 4) + ' \u7d44\u3002<br>About '",
    "showMsg('About ", 'warn opening')

sub("showMsg('&#9989; \u5206\u7d44\u5b8c\u6210 &middot; '", "showMsg('&#9989; Groups ready &middot; '", 'ok message')

sub("el.innerHTML = n + ' students \u4f4d\u8003\u751f &middot; ' + g + ' groups \u7d44<br>' +\n                   '<span class=\"gsizes\">\u6bcf\u7d44\u4eba\u6578 Group sizes: '",
    "el.innerHTML = n + ' students &middot; ' + g + ' groups<br>' +\n                   '<span class=\"gsizes\">Group sizes: '", 'stat line')

sub("el.innerHTML = 'Too many groups \u7d44\u6578\u592a\u591a';",
    "el.innerHTML = 'Too many groups';", 'stat too many')

sub("setHint('\u5df2\u9078 Candidate ' + LETTERS[i] + '\uff08' + state.data[g][i] + '\uff09&mdash; \u518d\u9ede\u53e6\u4e00\u4f4d\u8003\u751f\u5373\u53ef\u5c0d\u8abf<br>Selected &mdash; now tap the candidate you want to swap with');",
    "setHint('Selected Candidate ' + LETTERS[i] + ' (' + state.data[g][i] + ') &mdash; now tap the candidate to swap with');", 'selected hint')

sub("setHint('Swapped \u5df2\u5c0d\u8abf &#9989; &mdash; ' + DEFAULT_HINT);",
    "setHint('Swapped &#9989; &mdash; ' + DEFAULT_HINT);", 'swapped hint')

sub("var lines = ['DSE Speaking Practice \u2014 \u5206\u7d44\u540d\u55ae Random Grouping', ''];",
    "var lines = ['DSE Speaking Practice \u2014 Grouping list', ''];", 'copy header')

sub("lines.push('', 'A\u2013D = seating order in the group \u5ea7\u4f4d\u6b21\u5e8f');",
    "lines.push('', 'A\u2013D = seating order in the group');", 'copy footer')

sub("'<p class=\"tip\">\u9577\u6309\u6587\u5b57\u5168\u9078\u8907\u88fd &middot; long-press the text to select and copy</p>'",
    "'<p class=\"tip\">Long-press the text to select and copy</p>'", 'copy tip')

# ---------- 2. two cards per row on wide screens ----------
sub(".wrap{ max-width:1040px; margin:0 auto; }", ".wrap{ max-width:1200px; margin:0 auto; }", 'wrap width')

sub("""#output{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(292px,1fr));
  gap:clamp(12px,3vw,18px);
  align-items:start;
}""",
"""#output{
  display:grid;
  grid-template-columns:1fr;
  gap:clamp(12px,2vw,18px);
  align-items:start;
}
/* two group cards per row, but only when a card is wide enough to keep
   A B C D on one line (below that, full-width single column) */
@media (min-width:1160px){
  #output{ grid-template-columns:repeat(2,minmax(0,1fr)); }
}""", 'output columns')

# ---------- 3. A B C D horizontally, one row ----------
sub(""".seats{ display:grid; grid-template-columns:1fr 1fr; gap:9px; }
.seat{
  display:flex; align-items:center; gap:10px;
  width:100%; min-height:60px;
  padding:8px 10px;""",
""".seats{ display:flex; flex-wrap:wrap; gap:8px; }
.seat{
  display:flex; align-items:center; gap:8px;
  flex:1 1 auto; min-height:56px;
  padding:8px 12px;""", 'seats row')

# ---------- 4. "Candidate 12" on one line ----------
sub(".cand{ min-width:0; }", ".cand{ min-width:0; white-space:nowrap; }", 'cand nowrap')

sub(""".c-label{
  display:block; font-size:12px; font-weight:900; letter-spacing:.08em;
  text-transform:uppercase; color:#5f7488; line-height:1.25;
}""",
""".c-label{
  font-size:clamp(11px,1.05vw,14px); font-weight:800;
  color:#5f7488; line-height:1;
}""", 'candidate label inline')

sub(""".c-no{
  display:block; font-size:clamp(23px,6.6vw,28px); font-weight:900;
  line-height:1.12; color:#22374a; font-variant-numeric:tabular-nums;
}""",
""".c-no{
  font-size:clamp(19px,1.7vw,23px); font-weight:900;
  line-height:1; color:#22374a; font-variant-numeric:tabular-nums;
  margin-left:.3em;
}""", 'number inline')

# small screens: drop the word "Candidate" so A B C D still fit one row
sub("""@media (max-width:380px){
  .seats{ grid-template-columns:1fr; }
  .gcount{ display:none; }
}""",
"""@media (max-width:619px){
  .c-label{ display:none; }
  .seat{ min-height:48px; padding:6px 8px; justify-content:center; gap:6px; }
  .letter{ flex:0 0 30px; width:30px; height:30px; font-size:17px; }
  .c-no{ font-size:19px; margin-left:0; }
}
@media (max-width:380px){
  .gcount{ display:none; }
}""", 'small screen seats')

# ---------- print: keep the word, 2 cards per row, landscape sheet ----------
sub("""@media print{
  .no-print,.jserr,.hero-emoji,.hint{ display:none !important; }""",
"""@page{ size:A4 landscape; margin:10mm; }
@media print{
  .no-print,.jserr,.hero-emoji,.hint{ display:none !important; }""", 'print page size')

sub("""  .seat{ background:#fff; border-width:2px; min-height:44px; }
  .c-no{ font-size:19px; }
  .letter{ width:32px; height:32px; flex-basis:32px; font-size:17px; }""",
"""  .seat{ background:#fff; border-width:2px; min-height:40px; padding:4px 6px; }
  .c-label{ font-size:8.5px; }
  .c-no{ font-size:16px; margin-left:.25em; }
  .letter{ width:24px; height:24px; flex-basis:24px; font-size:15px; }""", 'print seats')

sub("showMsg('\u5df2\u8907\u88fd\u5206\u7d44\u540d\u55ae Copied &#9989;', 'ok')",
    "showMsg('Copied &#9989;', 'ok')", 'copied message')

# ---------- housekeeping ----------
sub("""  function sizesText(){
    var parts = [];
    for(var i = 0; i < state.data.length; i++){ parts.push(state.data[i].length); }
    return parts.join(' \u00b7 ');
  }
""", "", 'drop unused helper')

# ---------- apply ----------
problems = []
for old, new, label in pairs:
    n = src.count(old)
    if n != 1:
        problems.append('%s: expected 1 occurrence, found %d' % (label, n))
if problems:
    print('ABORTED - no changes written:')
    for p in problems:
        print('  ' + p)
    sys.exit(1)

for old, new, label in pairs:
    src = src.replace(old, new, 1)

# no Chinese left anywhere
import re
leftover = re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]', src)
if leftover:
    print('ABORTED - Chinese characters still present: ' + ''.join(sorted(set(leftover))))
    sys.exit(1)

io.open(PATH, 'w', encoding='utf-8').write(src)
print('applied %d edits; %d bytes; no CJK characters remain' % (len(pairs), len(src.encode('utf-8'))))
