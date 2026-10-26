/* DSE Speaking Practice — grouping tool checks
   1) syntax check every inline <script>
   2) ES5 token scan of the main script (old-Android safety)
   3) jsdom end-to-end: generate / shuffle / swap / validation / copy / persistence
*/
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const { execFileSync } = require('child_process');
const { JSDOM } = require('jsdom');

const FILE = '/root/dse-grouping/index.html';
const html = fs.readFileSync(FILE, 'utf8');
let pass = 0;
const fails = [];
function check(name, fn){
  try { fn(); pass++; console.log('  ok   ' + name); }
  catch (e) { fails.push(name + ' :: ' + e.message); console.log('  FAIL ' + name + ' -> ' + e.message); }
}
async function acheck(name, fn){
  try { await fn(); pass++; console.log('  ok   ' + name); }
  catch (e) { fails.push(name + ' :: ' + e.message); console.log('  FAIL ' + name + ' -> ' + e.message); }
}

/* ---------- 1. syntax ---------- */
const blocks = html.match(/<script[\s\S]*?<\/script>/g).map(b => b.replace(/^<script[^>]*>/, '').replace(/<\/script>$/, ''));
console.log('script blocks: ' + blocks.length);
blocks.forEach((src, i) => {
  check('syntax: script block ' + i + ' parses', () => {
    const f = '/tmp/blk' + i + '.js';
    fs.writeFileSync(f, src);
    execFileSync('node', ['--check', f]);
  });
});

/* ---------- 2. ES5 scan on the main script ---------- */
const main = blocks.filter(b => b.indexOf('__pageReady') !== -1 && b.indexOf('data-seat') !== -1)[0];
check('main script found (has page marker)', () => assert.ok(main && main.length > 3000, 'main script not found/short'));
const es6 = [
  ['arrow function', /=>/],
  ['const', /\bconst\s/],
  ['let', /\blet\s/],
  ['template literal', /`/],
  ['classList', /classList/],
  ['Array.includes', /\.includes\(/],
  ['Array.find', /\.find\(/],
  ['spread', /\.\.\./],
  ['for..of', /for\s*\([^;]*\sof\s/],
  ['class keyword', /\bclass\s+[A-Z]/],
  ['async/await', /\bawait\s/]
];
es6.forEach(([label, re]) => {
  check('ES5 scan: no ' + label, () => {
    const m = main.match(re);
    assert.ok(!m, 'found ' + JSON.stringify(m && m[0]));
  });
});

/* ---------- 3. jsdom end-to-end ---------- */
const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'https://dse-speaking-grouping.pages.dev/'
});
const win = dom.window, doc = win.document;
const tick = (ms) => new Promise(r => setTimeout(r, ms || 5));
const click = (el) => el.dispatchEvent(new win.MouseEvent('click', { bubbles: true, cancelable: true }));

function readGroups(){
  return Array.prototype.map.call(doc.querySelectorAll('.gcard'), c => ({
    name: c.querySelector('.gname').textContent.trim(),
    seats: Array.prototype.map.call(c.querySelectorAll('.seat'), s => ({
      letter: s.querySelector('.letter').textContent.trim(),
      label: s.querySelector('.c-label').textContent.trim(),
      no: parseInt(s.querySelector('.c-no').textContent.trim(), 10),
      g: parseInt(s.getAttribute('data-g'), 10),
      i: parseInt(s.getAttribute('data-i'), 10),
      sel: (' ' + s.className + ' ').indexOf(' sel ') !== -1,
      flash: (' ' + s.className + ' ').indexOf(' flash ') !== -1
    }))
  }));
}
function seatEl(g, i){ return doc.querySelector('.seat[data-g="' + g + '"][data-i="' + i + '"]'); }
function setInputs(from, to, g, absent){
  doc.getElementById('fromNo').value = String(from);
  doc.getElementById('toNo').value = String(to);
  doc.getElementById('numGroups').value = String(g);
  doc.getElementById('absentNo').value = String(absent || '');
  ['fromNo','toNo','numGroups','absentNo'].forEach(id => doc.getElementById(id).dispatchEvent(new win.Event('input', { bubbles: true })));
}
function msgText(){ return (doc.getElementById('msg').textContent || '').replace(/\s+/g, ' ').trim(); }
function msgClass(){ const b = doc.querySelector('#msg .box'); return b ? b.className : ''; }
function statText(){ return doc.getElementById('stat').textContent.replace(/\s+/g, ' ').trim(); }
function flatNums(){ return readGroups().reduce((a, c) => a.concat(c.seats.map(s => s.no)), []); }
function sizes(){ return readGroups().map(c => c.seats.length); }

(async () => {
  for (let i = 0; i < 60 && !win.__pageReady; i++) { await tick(10); }
  check('page initialised (__pageReady)', () => assert.ok(win.__pageReady, 'init never ran'));

  check('T1 empty state + hidden action bar', () => {
    assert.ok(/No groups yet/.test(doc.getElementById('output').textContent), 'no empty prompt');
    assert.strictEqual(doc.getElementById('actions').style.display, 'none');
    assert.strictEqual(doc.getElementById('hint').style.display, 'none');
  });

  check('T2 live stat for 1-15 / 4 groups', () => {
    setInputs(1, 15, 4);
    const s = statText();
    assert.ok(/15 candidates/.test(s) && /Group sizes: 4 · 4 · 4 · 3/.test(s), 'got: ' + s);
  });

  check('T3 generate 1-15 in 4 groups', () => {
    click(doc.getElementById('btnGo'));
    const g = readGroups();
    assert.strictEqual(g.length, 4, 'group count');
    assert.deepStrictEqual(sizes(), [4, 4, 4, 3], 'sizes: ' + sizes().join(','));
    assert.deepStrictEqual(flatNums().slice().sort((a, b) => a - b), Array.from({ length: 15 }, (_, i) => i + 1), 'numbers must be exactly 1..15');
    g.forEach((card, gi) => {
      assert.strictEqual(card.name, 'Group ' + (gi + 1), 'card title');
      assert.deepStrictEqual(card.seats.map(s => s.letter), ['A','B','C','D'].slice(0, card.seats.length), 'letters in order in ' + card.name);
      card.seats.forEach(s => assert.ok(/^(Candidate)$/i.test(s.letter) === false, 'letter isn\'t a candidate name'));
    });
    assert.ok(/Groups ready/.test(msgText()), 'success message missing: ' + msgText());
    assert.ok(!/\d, \d/.test(msgText()), 'success message must not repeat the size list: ' + msgText());
    assert.strictEqual(doc.getElementById('actions').style.display, 'flex', 'action bar must show');
    assert.notStrictEqual(doc.getElementById('hint').style.display, 'none');
  });

  check('T4 shuffle again keeps the class intact (60 rounds)', () => {
    const seen = {};
    for (let r = 0; r < 60; r++) {
      click(doc.getElementById('btnAgain'));
      const nums = flatNums();
      assert.strictEqual(nums.length, 15, 'lost a student in round ' + r);
      assert.deepStrictEqual(nums.slice().sort((a, b) => a - b), Array.from({ length: 15 }, (_, i) => i + 1), 'round ' + r + ' not a permutation: ' + nums.join(','));
      assert.deepStrictEqual(sizes(), [4, 4, 4, 3], 'round ' + r + ' sizes changed');
      seen[nums.join(',')] = 1;
    }
    assert.ok(Object.keys(seen).length >= 20, 'too little randomness: only ' + Object.keys(seen).length + ' distinct groupings in 60 rounds');
  });

  check('T5 no duplicate students across groups (10 rounds)', () => {
    for (let r = 0; r < 10; r++) {
      click(doc.getElementById('btnAgain'));
      const all = flatNums();
      assert.strictEqual(new Set(all).size, all.length, 'duplicate class number in round ' + r + ': ' + all.join(','));
    }
  });

  check('T6 tap-to-swap select state', () => {
    const el = seatEl(0, 0);
    click(el.querySelector('.letter'));               // click the inner span -> parent walk must work
    const s = readGroups()[0].seats[0];
    assert.ok(s.sel, 'selected class not applied');
    assert.ok(/Selected Candidate A/.test(doc.getElementById('hint').textContent), 'hint not updated: ' + doc.getElementById('hint').textContent);
  });

  check('T7 tapping the same candidate cancels the selection', () => {
    const before = flatNums().join(',');
    click(seatEl(0, 0));
    assert.ok(!readGroups()[0].seats[0].sel, 'selection not cleared');
    assert.strictEqual(flatNums().join(','), before, 'data changed on cancel');
    assert.ok(/Tap two candidates/.test(doc.getElementById('hint').textContent), 'hint not reset');
  });

  check('T8 swap two candidates in different groups', () => {
    const g1 = seatEl(0, 1), g3 = seatEl(2, 1);      // B of group 1 & B of group 3
    const a = readGroups()[0].seats[1].no, b = readGroups()[2].seats[1].no;
    click(g1); click(g3);
    const after = readGroups();
    assert.strictEqual(after[0].seats[1].no, b, 'group1 B should now hold ' + b);
    assert.strictEqual(after[2].seats[1].no, a, 'group3 B should now hold ' + a);
    assert.deepStrictEqual(sizes(), [4, 4, 4, 3], 'sizes changed by swap');
    assert.deepStrictEqual(flatNums().slice().sort((x, y) => x - y), Array.from({ length: 15 }, (_, i) => i + 1), 'swap broke the roster');
    assert.deepStrictEqual(after[0].seats.map(s => s.letter), ['A','B','C','D'], 'letters must stay fixed to the seat');
    assert.ok(!after[0].seats[1].sel && !after[2].seats[1].sel, 'selection must be cleared after swap');
    assert.ok(after[0].seats[1].flash && after[2].seats[1].flash, 'swapped seats should flash');
  });

  check('T9 swap inside one group + no stray selection left', () => {
    const a0 = readGroups()[1].seats[0].no, a2 = readGroups()[1].seats[2].no;
    click(seatEl(1, 0)); click(seatEl(1, 2));
    const card = readGroups()[1];
    assert.strictEqual(card.seats[0].no, a2, 'same-group swap A');
    assert.strictEqual(card.seats[2].no, a0, 'same-group swap C');
    assert.ok(!card.seats.some(s => s.sel), 'a seat is still marked selected');
  });

  check('T10 validation: more groups than active candidates', () => {
    const before = flatNums().join(',');
    setInputs(1, 15, 20, 0);
    click(doc.getElementById('btnGo'));
    assert.ok(/err/.test(msgClass()), 'expected an error box, got: ' + msgClass());
    assert.ok(/cannot be larger than active candidates/.test(msgText()), 'message: ' + msgText());
    assert.strictEqual(flatNums().join(','), before, 'grouping must be untouched after an error');
  });

  check('T11 validation: reversed range, blank field, groups=0', () => {
    setInputs(15, 1, 3); click(doc.getElementById('btnGo'));
    assert.ok(/err/.test(msgClass()) && /Invalid class-number range/.test(msgText()), 'reversed range: ' + msgText());
    setInputs('', 15, 3); click(doc.getElementById('btnGo'));
    assert.ok(/err/.test(msgClass()), 'blank range should error: ' + msgText());
    setInputs(1, 15, 0); click(doc.getElementById('btnGo'));
    assert.ok(/err/.test(msgClass()) && /1–40|1-40/.test(msgText()), 'groups=0: ' + msgText());
  });

  check('T12 odd sizes: 7 students / 2 groups -> 4+3, letters A-D/A-C', () => {
    setInputs(1, 7, 2); click(doc.getElementById('btnGo'));
    assert.deepStrictEqual(sizes(), [4, 3], 'sizes: ' + sizes().join(','));
    const g = readGroups();
    assert.deepStrictEqual(g[0].seats.map(s => s.letter), ['A','B','C','D']);
    assert.deepStrictEqual(g[1].seats.map(s => s.letter), ['A','B','C']);
    assert.deepStrictEqual(flatNums().slice().sort((a, b) => a - b), [1,2,3,4,5,6,7]);
  });

  check('T13 8 students / 2 groups -> 4+4', () => {
    setInputs(1, 8, 2); click(doc.getElementById('btnGo'));
    assert.deepStrictEqual(sizes(), [4, 4]);
  });

  check('T14 9 students / 4 groups -> 3,2,2,2', () => {
    setInputs(1, 9, 4); click(doc.getElementById('btnGo'));
    assert.deepStrictEqual(sizes(), [3, 2, 2, 2], 'sizes: ' + sizes().join(','));
  });

  check('T15 one candidate per group: 5 / 5', () => {
    setInputs(1, 5, 5); click(doc.getElementById('btnGo'));
    const g = readGroups();
    assert.deepStrictEqual(sizes(), [1, 1, 1, 1, 1]);
    g.forEach((c, i) => assert.deepStrictEqual(c.seats.map(s => s.letter), ['A'], 'group ' + (i + 1) + ' letter'));
  });

  check('T16 oversized groups warn (class 30, 2 groups)', () => {
    setInputs(1, 30, 2); click(doc.getElementById('btnGo'));
    assert.ok(/warn/.test(msgClass()), 'expected amber warning, got: ' + msgClass());
    assert.ok(/About 15 per group/.test(msgText()), 'warning text: ' + msgText());
    assert.strictEqual(readGroups().length, 2, 'still generates the 2 requested groups');
  });

  check('T17 real class range 1-22 / 6 groups', () => {
    setInputs(1, 22, 6); click(doc.getElementById('btnGo'));
    assert.strictEqual(readGroups().length, 6);
    assert.deepStrictEqual(sizes(), [4, 4, 4, 4, 3, 3], 'sizes: ' + sizes().join(','));
    assert.deepStrictEqual(flatNums().slice().sort((a, b) => a - b), Array.from({ length: 22 }, (_, i) => i + 1));
  });

  check('T18 copy produces the plain-text list', () => {
    click(doc.getElementById('btnCopy'));
    const box = doc.getElementById('copybox');
    const msgOk = /Copied/.test(msgText());
    if (box) {
      const txt = box.getElementsByTagName('textarea')[0].value;
      assert.ok(/DSE Speaking Practice/.test(txt), 'copy text header missing');
      assert.ok(/Group 1 — A: \d+/.test(txt), 'copy text group line missing: ' + txt.split('\n')[2]);
      assert.ok(txt.split('\n').filter(l => /^Group /.test(l)).length === 6, 'one line per group');
    } else {
      assert.ok(msgOk, 'neither clipboard success nor copy box fallback happened');
    }
  });

  check('T19 settings persist in localStorage', () => {
    const raw = win.localStorage.getItem('dse-speaking-grouping');
    assert.ok(raw, 'nothing saved');
    const s = JSON.parse(raw);
    assert.strictEqual(s.from, '1'); assert.strictEqual(s.to, '22'); assert.strictEqual(s.groups, '6');
    assert.ok(s.absent !== undefined, 'absent field must be saved');
  });

  await acheck('T20 reload restores saved settings', async () => {
    const seed = win.localStorage.getItem('dse-speaking-grouping');
    const injected = html.replace('<head>', '<head><script>try{localStorage.setItem("dse-speaking-grouping", ' + JSON.stringify(seed) + ')}catch(e){}</script>');
    const dom2 = new JSDOM(injected, { runScripts: 'dangerously', url: 'https://dse-speaking-grouping.pages.dev/' });
    const d = dom2.window.document;
    assert.strictEqual(dom2.window.localStorage.getItem('dse-speaking-grouping'), seed, 'seed did not land in storage');
    for (let i = 0; i < 60 && !dom2.window.__pageReady; i++) { await tick(10); }
    assert.ok(dom2.window.__pageReady, 'second page never initialised');
    assert.strictEqual(d.getElementById('fromNo').value, '1', 'saved range start not restored');
    assert.strictEqual(d.getElementById('toNo').value, '22', 'saved range end not restored');
    assert.strictEqual(d.getElementById('numGroups').value, '6', 'saved group count not restored');
    assert.strictEqual(d.getElementById('absentNo').value, '', 'saved absent input not restored');
    assert.ok(/22 candidates/.test(d.getElementById('stat').textContent), 'stat must use the restored values');
  });

  check('T21 print stylesheet hides the controls', () => {
    assert.ok(/@media print\{[\s\S]{0,300}?\.no-print[\s\S]{0,200}?display:none/.test(html), 'print rules must hide .no-print chrome');
    assert.ok(/page-break-inside:avoid/.test(html), 'cards must not split across printed pages');
  });

  check('T22 no Chinese characters anywhere in the page', () => {
    const cjk = html.match(/[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/g);
    assert.strictEqual(cjk, null, 'Chinese text found: ' + (cjk ? cjk.join('') : ''));
  });

  check('T23 candidates sit in a horizontal flex row, not a grid', () => {
    assert.ok(/\.seats\{\s*display:flex;\s*flex-wrap:wrap/.test(html), '.seats must be a flex row');
    assert.ok(/@media \(max-width:719px\)\{[\s\S]{0,200}?\.seat\{ flex:1 1 0/.test(html), 'narrow screens must pin four chips to one row');
    assert.ok(/\.seat\{[\s\S]{0,120}?flex:1 1 auto/.test(html), 'chips must size to their content');
    assert.ok(!/\.seats\{[^}]*grid-template-columns/.test(html), '.seats must not use a grid');
  });

  check('T24 two group cards per row on wide screens only', () => {
    assert.ok(/@media \(min-width:1024px\)\{\s*#output\{\s*grid-template-columns:repeat\(2/.test(html),
      'expected a 2-column output grid at >=1024px');
    assert.ok(/#output\{\s*display:grid;\s*grid-template-columns:1fr;/.test(html), 'one card per row below that');
    assert.ok(/@media \(min-width:1024px\)\{[\s\S]{0,600}?\.c-label\{ display:none/.test(html),
      'iPad tier must drop the chip label so A-D stay on one row');
    assert.ok(/@media \(min-width:1360px\)\{[\s\S]{0,300}?\.c-label\{ display:inline/.test(html),
      'the full Candidate NN chip must return on wide cards');
  });

  check('T25 "Candidate 12" renders on one line', () => {
    const card = readGroups()[0];
    assert.strictEqual(card.seats[0].label, 'Candidate', 'label text');
    const cand = doc.querySelector('.cand');
    assert.ok(/Candidate \d+$/.test(cand.textContent.replace(/\s+/g, ' ').trim()), 'chip text: ' + JSON.stringify(cand.textContent));
    assert.ok(/\.cand\{[^}]*white-space:nowrap/.test(html), '.cand must not wrap');
    assert.ok(!/\.c-label\{[^}]*display:block/.test(html), '.c-label must not be block (would force a second line)');
    assert.ok(!/\.c-no\{[^}]*display:block/.test(html), '.c-no must not be block (would force a second line)');
  });

  check('T26 chip tiers come after the base chip rules (or they are overridden)', () => {
    const baseIdx = html.indexOf('.c-no{');
    const tierIdx = html.indexOf('Four chips carrying the word');
    assert.ok(baseIdx > 0 && tierIdx > baseIdx,
      'a media query adds no specificity - the tier must be declared after the base .c-no rule');
  });

  check('T27 generate with specific absentees (5, 7, 12 out of 15)', () => {
    setInputs(1, 15, 4, '5, 7, 12');
    click(doc.getElementById('btnGo'));
    const g = readGroups();
    assert.strictEqual(g.length, 4, 'group count');
    assert.deepStrictEqual(sizes(), [3, 3, 3, 3], 'sizes: ' + sizes().join(','));
    const active = flatNums();
    assert.strictEqual(active.length, 12, 'active candidates');
    assert.ok(active.indexOf(5) === -1, '5 should be absent');
    assert.ok(active.indexOf(7) === -1, '7 should be absent');
    assert.ok(active.indexOf(12) === -1, '12 should be absent');
    assert.ok(/absent:/.test(msgText()), 'message must list absentees: ' + msgText());
    assert.ok(/absent: 5.*7.*12/.test(msgText()) || /absent:.*12/.test(msgText()), 'message must mention absent numbers: ' + msgText());
  });

  check('T28 all absentees = no groups possible', () => {
    setInputs(1, 5, 2, '1, 2, 3, 4, 5');
    click(doc.getElementById('btnGo'));
    assert.ok(/err/.test(msgClass()), 'expected error when all absent');
    assert.ok(/cannot be larger than active candidates \(0\)/.test(msgText()), 'message: ' + msgText());
  });

  check('T29 copy text includes absent list when absentees > 0', () => {
    setInputs(1, 10, 3, '2, 9');
    click(doc.getElementById('btnGo'));
    click(doc.getElementById('btnCopy'));
    const box = doc.getElementById('copybox');
    if (box) {
      const txt = box.getElementsByTagName('textarea')[0].value;
      assert.ok(/Absent:/.test(txt), 'copy text must list absentees: ' + txt);
      assert.ok(/2.*9/.test(txt) || /9.*2/.test(txt), 'copy text must include the absent numbers: ' + txt);
    }
  });

  check('T30 stat reflects absentees live', () => {
    setInputs(1, 20, 5, '3, 8, 15, 18');
    const s = statText();
    assert.ok(/16 active/.test(s) && /4 absent/.test(s), 'stat must show active+absent breakdown: ' + s);
    assert.ok(/Group sizes:/.test(s), 'stat must still show group sizes: ' + s);
  });

  check('T31 invalid absentee number shows error', () => {
    setInputs(1, 10, 3, '99');
    click(doc.getElementById('btnGo'));
    assert.ok(/err/.test(msgClass()), 'expected error for out-of-range absentee');
    assert.ok(/out of range/.test(msgText()), 'message: ' + msgText());
  });

  console.log('\n--- ' + pass + ' checks passed, ' + fails.length + ' failed ---');
  if (fails.length) { fails.forEach(f => console.log('FAIL ' + f)); process.exit(1); }
})();
