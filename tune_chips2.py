#!/usr/bin/env python3
# Final layout tuning: 2 columns only where half-width cards really keep
# A B C D on one row, and compact chips on narrow screens.
import io, sys

P = '/root/dse-grouping/index.html'
s = io.open(P, encoding='utf-8').read()

pairs = [
    (".wrap{ max-width:1320px; margin:0 auto; }",
     ".wrap{ max-width:1440px; margin:0 auto; }", 'container width'),

    ("@media (min-width:1300px){", "@media (min-width:1360px){", 'two column breakpoint'),

    ("""@media (max-width:639px){
  .c-label{ display:none; }
  .seat{ min-height:48px; padding:6px 8px; justify-content:center; gap:6px; }
  .letter{ flex:0 0 30px; width:30px; height:30px; font-size:17px; }
  .c-no{ font-size:19px; margin-left:0; }
}
@media (max-width:380px){
  .gcount{ display:none; }
}""",
     """@media (max-width:719px){
  .c-label{ display:none; }
  .seat{ flex:1 1 0; min-width:0; min-height:46px; padding:6px 5px; justify-content:center; gap:4px; }
  .letter{ flex:0 0 28px; width:28px; height:28px; font-size:16px; }
  .c-no{ font-size:18px; margin-left:0; }
}
@media (max-width:380px){
  .gcount{ display:none; }
  .seat{ padding:4px 3px; }
  .letter{ flex:0 0 26px; width:26px; height:26px; font-size:15px; }
  .c-no{ font-size:17px; }
}""", 'narrow screen chips'),
]

problems = [l for o, n, l in pairs if s.count(o) != 1]
if problems:
    print('ABORTED - no changes written: ' + ', '.join(problems))
    sys.exit(1)

for o, n, l in pairs:
    s = s.replace(o, n, 1)

# keep the checks in sync with the new breakpoint
C = '/root/dse-grouping/checks/test_grouping.js'
c = io.open(C, encoding='utf-8').read()
c = c.replace("(min-width:1300px)", "(min-width:1360px)").replace("at >=1300px", "at >=1360px")
c = c.replace("assert.ok(/\\.seats\\{\\s*display:flex;\\s*flex-wrap:wrap/.test(html), '.seats must be a flex row');",
              "assert.ok(/\\.seats\\{\\s*display:flex;\\s*flex-wrap:wrap/.test(html), '.seats must be a flex row');\n    assert.ok(/@media \\(max-width:719px\\)\\{[\\s\\S]{0,200}?\\.seat\\{ flex:1 1 0/.test(html), 'narrow screens must pin four chips to one row');")
io.open(C, 'w', encoding='utf-8').write(c)

io.open(P, 'w', encoding='utf-8').write(s)
print('applied %d layout tweaks; checks synced' % len(pairs))
