#!/usr/bin/env python3
# BUG: the responsive chip tiers were declared BEFORE the base .seat/.letter/
# .c-label/.c-no rules, so with equal specificity the later base rules won and
# the tiers never applied (chips stayed 135px wide -> wrapped at iPad widths).
# Fix: move both tiers below the base chip rules.
import io, sys

P = '/root/dse-grouping/index.html'
s = io.open(P, encoding='utf-8').read()

tier1024 = """@media (min-width:1024px){
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
"""
tier1360 = """@media (min-width:1360px){
  /* wide cards: the full "Candidate 12" chip fits on one row again */
  .seat{ gap:5px; padding:6px 8px; min-height:50px; }
  .letter{ flex:0 0 32px; width:32px; height:32px; font-size:17px; }
  .c-label{ display:inline; font-size:11.5px; }
  .c-no{ font-size:18px; margin-left:.25em; }
}
"""

for block, name in ((tier1024, 'tier 1024'), (tier1360, 'tier 1360')):
    if s.count(block) != 1:
        print('ABORTED: %s not found exactly once' % name)
        sys.exit(1)
    s = s.replace(block, '', 1)

# the 1024 tier also carried the grid rule; keep that where it was, minus the chip rules
anchor = """/* two group cards per row, but only when a card is wide enough to keep
   A B C D on one line (below that, full-width single column) */
@media (min-width:1024px){
  #output{ grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (min-width:1360px){
}
"""
if s.count(anchor) != 1:
    # tolerate whitespace differences by rebuilding from the two known fragments
    old = """/* two group cards per row, but only when a card is wide enough to keep
   A B C D on one line (below that, full-width single column) */
"""
    if s.count(old) != 1:
        print('ABORTED: grid-rule comment not found')
        sys.exit(1)
    s = s.replace(old, old + """@media (min-width:1024px){
  #output{ grid-template-columns:repeat(2,minmax(0,1fr)); }
}
""", 1)
    # drop the leftover empty 1360 block if the replace above produced one
    s = s.replace("@media (min-width:1360px){\n}\n", "", 1)
else:
    s = s.replace(anchor, """/* two group cards per row, but only when a card is wide enough to keep
   A B C D on one line (below that, full-width single column) */
@media (min-width:1024px){
  #output{ grid-template-columns:repeat(2,minmax(0,1fr)); }
}
""", 1)

# re-insert both tiers AFTER the base chip rules so they actually win
marker = "/* per-group pastel themes */"
if s.count(marker) != 1:
    print('ABORTED: pastel-theme marker not found')
    sys.exit(1)
s = s.replace(marker, tier1024 + tier1360 + "\n" + marker, 1)

base = s.index(".c-no{")
tier_start = s.index('@media (min-width:1024px){\n  #output', 0, len(s))
# the tier block (not the early grid-rule block) must come after the base chip rules
tier_block = s.index('Four chips carrying the word')
grid_block = s.index('#output{ grid-template-columns:repeat(2,minmax(0,1fr)); }')
assert base < tier_block, 'tier still declared before the base chip rules'
assert grid_block < base, 'the grid rule must stay above the base rules (it only needs the base #output rule)'
assert s.count('.c-label{ display:none; }') == 2, 'expected the small-screen and iPad tiers to hide the label'
assert s.count('@media (min-width:1024px){') == 2, 'expected the grid block plus the late tier block'

io.open(P, 'w', encoding='utf-8').write(s)
print('moved chip tiers after the base rules (base at %d, tier at %d)' % (base, tier_block))
