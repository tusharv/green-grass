import test from 'node:test';
import assert from 'node:assert/strict';
import { learningPlan, hasLearningDetails } from './learning.js';

test('renders server learning content without substituting preset advice', () => {
  const gap = {skill:'A new skill', severity:'major', learn:['A tailored first step'], practice:'A tailored exercise', project:'A tailored project', verify:'A tailored check', resources:[{title:'Selected by AI',url:'https://example.com/learning'}]};
  assert.deepEqual(learningPlan({gaps:[gap]}), [gap]);
  assert.deepEqual(learningPlan(), []);
});

test('old saved plans stay readable without invented learning steps or links', () => {
  const [plan] = learningPlan({gaps:[{skill:'Rust',practice:'Saved exercise',project:'Saved project'}]});
  assert.equal(plan.practice, 'Saved exercise');
  assert.deepEqual(plan.learn, []);
  assert.deepEqual(plan.resources, []);
});

test('unsafe resource links cannot be rendered even in old saved data', () => {
  const resources = ['javascript:alert(1)','https://user:pass@example.com','bad url','http://example.com','https://example.com/course'].map(url => ({title:'Resource',url}));
  assert.deepEqual(learningPlan({gaps:[{resources} ]})[0].resources, [{title:'Resource',url:'https://example.com/course'}]);
});


test('incomplete AI output remains eligible for retry', () => {
  assert.equal(hasLearningDetails({gaps:[]}), false);
  assert.equal(hasLearningDetails({gaps:[{learn:['Step'],verify:'Check',resources:[]}]}), false);
  assert.equal(hasLearningDetails({gaps:[{learn:['Step'],verify:'Check',resources:[{url:'https://example.com'}]}]}), true);
});
