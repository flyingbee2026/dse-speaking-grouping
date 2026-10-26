#!/usr/bin/env python3
# Update the checks for the English-only copy, and add layout / language checks.
import io, sys

P = '/root/dse-grouping/checks/test_grouping.js'
s = io.open(P, encoding='utf-8').read()

pairs = [
    ("assert.ok(/\u5206\u7d44\u5b8c\u6210/.test(msgText()), 'success message missing: ' + msgText());",
     "assert.ok(/Groups ready/.test(msgText()), 'success message missing: ' + msgText());"),
    ("assert.ok(/\u4e0d\u53ef\u591a\u65bc\u8003\u751f\u4eba\u6578/.test(msgText()), 'message: ' + msgText());",
     "assert.ok(/cannot be larger than the class size/.test(msgText()), 'message: ' + msgText());"),
    ("assert.ok(/err/.test(msgClass()) && /\u73ed\u865f\u7bc4\u570d\u4e0d\u6b63\u78ba/.test(msgText()), 'reversed range: ' + msgText());",
     "assert.ok(/err/.test(msgClass()) && /Invalid class-number range/.test(msgText()), 'reversed range: ' + msgText());"),
    ("assert.ok(/\u6bcf\u7d44\u7d04 15 \u4eba/.test(msgText()), 'warning text: ' + msgText());",
     "assert.ok(/About 15 per group/.test(msgText()), 'warning text: ' + msgText());"),
    ("assert.ok(/\u5df2\u9078 Candidate A/.test(doc.getElementById('hint').textContent), 'hint not updated: ' + doc.getElementById('hint').textContent);",
     "assert.ok(/Selected Candidate A/.test(doc.getElementById('hint').textContent), 'hint not updated: ' + doc.getElementById('hint').textContent);"),
]

new_tests = """
  check('T22 no Chinese characters anywhere in the page', () => {
    const cjk = html.match(/[\\u3400-\\u4dbf\\u4e00-\\u9fff\\uf900-\\ufaff]/g);
    assert.strictEqual(cjk, null, 'Chinese text found: ' + (cjk ? cjk.join('') : ''));
  });

  check('T23 candidates sit in a horizontal flex row, not a grid', () => {
    assert.ok(/\\.seats\\{\\s*display:flex;\\s*flex-wrap:wrap/.test(html), '.seats must be a flex row');
    assert.ok(/\\.seat\\{[\\s\\S]{0,120}?flex:1 1 auto/.test(html), 'chips must size to their content');
    assert.ok(!/\\.seats\\{[^}]*grid-template-columns/.test(html), '.seats must not use a grid');
  });

  check('T24 two group cards per row on wide screens only', () => {
    assert.ok(/@media \\(min-width:1160px\\)\\{\\s*#output\\{\\s*grid-template-columns:repeat\\(2/.test(html),
      'expected a 2-column output grid at >=1160px');
    assert.ok(/#output\\{\\s*display:grid;\\s*grid-template-columns:1fr;/.test(html), 'one card per row below that');
  });

  check('T25 "Candidate 12" renders on one line', () => {
    const card = readGroups()[0];
    assert.strictEqual(card.seats[0].label, 'Candidate', 'label text');
    const cand = doc.querySelector('.cand');
    assert.ok(/Candidate \\d+$/.test(cand.textContent.replace(/\\s+/g, ' ').trim()), 'chip text: ' + JSON.stringify(cand.textContent));
    assert.ok(/\\.cand\\{[^}]*white-space:nowrap/.test(html), '.cand must not wrap');
    assert.ok(!/\\.c-label\\{[^}]*display:block/.test(html), '.c-label must not be block (would force a second line)');
    assert.ok(!/\\.c-no\\{[^}]*display:block/.test(html), '.c-no must not be block (would force a second line)');
  });
"""

if 'T22 no Chinese' in s:
    print('already updated')
else:
    for old, new in pairs:
        if s.count(old) != 1:
            print('ABORTED: %d matches for %r' % (s.count(old), old[:60]))
            sys.exit(1)
        s = s.replace(old, new, 1)
    marker = "\n  console.log('\\n--- ' + pass + ' checks passed, ' + fails.length + ' failed ---');"
    assert s.count(marker) == 1
    s = s.replace(marker, new_tests + marker, 1)

    # readGroups() must also expose the chip label so T25 can assert it
    old_map = """      seats: Array.prototype.map.call(c.querySelectorAll('.seat'), s => ({
      letter: s.querySelector('.letter').textContent.trim(),"""
    old_real = """    seats: Array.prototype.map.call(c.querySelectorAll('.seat'), s => ({
      letter: s.querySelector('.letter').textContent.trim(),"""
    new_real = """    seats: Array.prototype.map.call(c.querySelectorAll('.seat'), s => ({
      letter: s.querySelector('.letter').textContent.trim(),
      label: s.querySelector('.c-label').textContent.trim(),"""
    if s.count(old_real) != 1:
        old_real = old_map
    assert s.count(old_real) == 1, 'readGroups marker not found'
    s = s.replace(old_real, new_real, 1)

    io.open(P, 'w', encoding='utf-8').write(s)
    print('checks updated')
