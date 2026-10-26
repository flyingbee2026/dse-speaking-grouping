#!/usr/bin/env python3
# Two group cards per row from 1024px (iPad landscape and up), with a
# compact chip tier so A B C D still sit on one line in half-width cards.
import io, sys

P = '/root/dse-grouping/index.html'
s = io.open(P, encoding='utf-8').read()

old = """@media (min-width:1360px){
  #output{ grid-template-columns:repeat(2,minmax(0,1fr)); }
}"""
new = """@media (min-width:1024px){
  #output{ grid-template-columns:repeat(2,minmax(0,1fr)); }
  /* half-width cards: compact chips keep A B C D on one row */
  .seat{ gap:4px; padding:6px 6px; min-height:48px; }
  .letter{ flex:0 0 28px; width:28px; height:28px; font-size:16px; }
  .c-label{ font-size:10.5px; }
  .c-no{ font-size:17px; margin-left:.2em; }
}
@media (min-width:1360px){
  /* wide cards: roomier chip again */
  .seat{ gap:5px; padding:6px 8px; min-height:50px; }
  .letter{ flex:0 0 32px; width:32px; height:32px; font-size:17px; }
  .c-label{ font-size:11.5px; }
  .c-no{ font-size:18px; margin-left:.25em; }
}"""

if s.count(old) != 1:
    print('ABORTED: breakpoint block not found as expected')
    sys.exit(1)
s = s.replace(old, new, 1)
io.open(P, 'w', encoding='utf-8').write(s)

C = '/root/dse-grouping/checks/test_grouping.js'
c = io.open(C, encoding='utf-8').read()
c = c.replace("(min-width:1360px)\\{\\s*#output", "(min-width:1024px)\\{\\s*#output")
c = c.replace("'expected a 2-column output grid at >=1360px'", "'expected a 2-column output grid at >=1024px'")
c = c.replace("assert.ok(/#output\\{\\s*display:grid;\\s*grid-template-columns:1fr;/.test(html), 'one card per row below that');",
              "assert.ok(/#output\\{\\s*display:grid;\\s*grid-template-columns:1fr;/.test(html), 'one card per row below that');\n    assert.ok(/@media \\(min-width:1360px\\)\\{[\\s\\S]{0,200}?\\.seat\\{ gap:5px/.test(html), 'roomier chip tier on wide cards');")
io.open(C, 'w', encoding='utf-8').write(c)
print('applied; checks synced')
