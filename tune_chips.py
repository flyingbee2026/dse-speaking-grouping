#!/usr/bin/env python3
# Tighten the candidate chips so four always fit on ONE row inside a
# half-width card, and move the 2-column breakpoint to where that holds.
import io, sys

P = '/root/dse-grouping/index.html'
s = io.open(P, encoding='utf-8').read()

pairs = [
    (".wrap{ max-width:1200px; margin:0 auto; }",
     ".wrap{ max-width:1320px; margin:0 auto; }", 'container width'),

    ("""/* two group cards per row, but only when a card is wide enough to keep
   A B C D on one line (below that, full-width single column) */
@media (min-width:1160px){""",
     """/* two group cards per row, but only when a card is wide enough to keep
   A B C D on one line (below that, full-width single column) */
@media (min-width:1300px){""", 'two column breakpoint'),

    (".seats{ display:flex; flex-wrap:wrap; gap:8px; }",
     ".seats{ display:flex; flex-wrap:wrap; gap:6px; }", 'seats gap'),

    ("""  display:flex; align-items:center; gap:8px;
  flex:1 1 auto; min-height:56px;
  padding:8px 12px;""",
     """  display:flex; align-items:center; gap:5px;
  flex:1 1 auto; min-height:50px;
  padding:6px 8px;""", 'seat metrics'),

    ("""  flex:0 0 40px; width:40px; height:40px;
  display:flex; align-items:center; justify-content:center;
  border-radius:50%;
  font-family:'Baloo 2','Nunito',sans-serif;
  font-weight:800; font-size:21px; color:#fff;""",
     """  flex:0 0 32px; width:32px; height:32px;
  display:flex; align-items:center; justify-content:center;
  border-radius:50%;
  font-family:'Baloo 2','Nunito',sans-serif;
  font-weight:800; font-size:17px; color:#fff;""", 'letter badge'),

    (""".c-label{
  font-size:clamp(11px,1.05vw,14px); font-weight:800;
  color:#5f7488; line-height:1;
}""",
     """.c-label{
  font-size:11.5px; font-weight:800; color:#5f7488; line-height:1;
}""", 'candidate label size'),

    (""".c-no{
  font-size:clamp(19px,1.7vw,23px); font-weight:900;
  line-height:1; color:#22374a; font-variant-numeric:tabular-nums;
  margin-left:.3em;
}""",
     """.c-no{
  font-size:18px; font-weight:900;
  line-height:1; color:#22374a; font-variant-numeric:tabular-nums;
  margin-left:.25em;
}""", 'number size'),

    ("@media (max-width:619px){", "@media (max-width:639px){", 'small-screen breakpoint'),
]

problems = [l for o, n, l in pairs if s.count(o) != 1]
if problems:
    print('ABORTED - no changes written: ' + ', '.join(problems))
    sys.exit(1)

for o, n, l in pairs:
    s = s.replace(o, n, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('applied %d layout tweaks' % len(pairs))
