import test from 'node:test';
import assert from 'node:assert/strict';
import {moveItem, editText, companyKey, changedSections} from './editor.js';

test('moving entries preserves their data and leaves the source untouched', () => {
  const original = [{employer:'A',bullets:['One']},{employer:'B',bullets:['Two']}];
  assert.deepEqual(moveItem(original,0,1), [original[1], original[0]]);
  assert.equal(original[0].employer, 'A');
  assert.equal(moveItem(original,0,-1), original);
});
test('canvas accepts only existing textual fields, never arbitrary object paths', () => {
  const source = {summary:'Old',experience:[{bullets:['First']}],skills:[]};
  assert.equal(editText(source,'experience.0.bullets.0','Edited').experience[0].bullets[0], 'Edited');
  assert.equal(source.experience[0].bullets[0], 'First');
  for (const path of ['__proto__.polluted','years_experience','experience.4.bullets.0','skills.4']) {
    assert.equal(editText(source,path,'Injected'),source);
  }
});
test('company logos follow employer identity, not position', () => {
  assert.equal(companyKey('  Analytical   Engines '),'analytical engines');
});
test('review identifies factual changes without layout noise', () => {
  assert.deepEqual(changedSections({summary:'A',skills:[]},{summary:'B',skills:[]}), ['Summary']);
});

import {rememberDraft, recallDraft, forgetDraft, clearEditorDrafts} from './editorDrafts.js';
test('private editor drafts survive navigation but cannot cross user accounts', () => {
  clearEditorDrafts();
  const draft = {profile:{summary:'Unsaved'},version:'original'};
  rememberDraft(1,7,draft);
  draft.profile.summary = 'Changed object';
  assert.equal(recallDraft(1,7).profile.summary,'Unsaved');
  assert.equal(recallDraft(1,8),null);
  assert.equal(recallDraft(2,7),null);
  assert.equal(recallDraft(1,7),null);
  rememberDraft(1,7,draft);
  forgetDraft(1,7);
  assert.equal(recallDraft(1,7),null);
});
