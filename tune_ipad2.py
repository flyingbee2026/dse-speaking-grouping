#!/usr/bin/env python3
# iPad tier: 2 cards per row from 1024px. Measured chip need with the word
# "Candidate" is 539px, but a half-width card at 1024-1359px offers only
# 430-508px, so that tier shows badge + number (card header keeps the word)
# and the full "Candidate 12" chip returns at >=1360px.
import io, sys

P = '/root/dse-grouping/index.html'
s = io.open(P, encoding='utf-8').read()

old = """@media (min-width:1024px){
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

new = """@media (min-width:1024px){
  #output{ grid-template-columns:repeat(2,minmax(0,1fr)); }
  /* iPad landscape and up: two group cards per row.
     Four chips carrying the word "Candidate" need ~539px of card interior
     (measured, two-digit numbers), but a half-width card at 1024-1359px has
     only ~430-508px. So this tier shows the A-D badge plus the class number,
     and the card header pill keeps the word ("4 CANDIDATES"). */
  .seat{ gap:6px; padding:6px 10px; min-height:52px; }
  .letter{ flex:0 0 30px; width:30px; height:30px; font-size:17px; }
  .c-label{ display:none; }
  .c-no{ font-size:22px; margin-left:0; }
}
@media (min-width:1360px){
  /* wide cards: the full "Candidate 12" chip fits on one row again */
  .seat{ gap:5px; padding:6px 8px; min-height:50px; }
  .letter{ flex:0 0 32px; width:32px; height:32px; font-size:17px; }
  .c-label{ display:inline; font-size:11.5px; }
  .c-no{ font-size:18px; margin-left:.25em; }
}"""

if s.count(old) != 1:
    print('ABORTED: tier block not found as expected')
    sys.exit(1)
s = s.replace(old, new, 1)
io.open(P, 'w', encoding='utf-8').write(s)

C = '/root/dse-grouping/checks/test_grouping.js'
c = io.open(C, encoding='utf-8').read()
old_t = "assert.ok(/@media \\(min-width:1360px\\)\\{[\\s\\S]{0,200}?\\.seat\\{ gap:5px/.test(html), 'roomier chip tier on wide cards');"
new_t = ("assert.ok(/@media \\(min-width:1024px\\)\\{[\\s\\S]{0,600}?\\.c-label\\{ display:none/.test(html),\n"
         "      'iPad tier must drop the chip label so A-D stay on one row');\n"
         "    assert.ok(/@media \\(min-width:1360px\\)\\{[\\s\\S]{0,300}?\\.c-label\\{ display:inline/.test(html),\n"
         "      'the full Candidate NN chip must return on wide cards');")
if c.count(old_t) != 1:
    print('ABORTED: check line not found')
    sys.exit(1)
c = c.replace(old_t, new_t, 1)
io.open(C, 'w', encoding='utf-8').write(c)
print('applied iPad tier; checks synced')
