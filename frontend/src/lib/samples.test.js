import test from 'node:test';
import assert from 'node:assert/strict';
import { getSample, sampleScore } from './samples.js';

test('sample role reviews are deterministic and match the published fit rule', () => {
  const ready = getSample('ready');
  const gaps = getSample('gaps');
  assert.equal(sampleScore(ready.review), 100);
  assert.equal(ready.review.suitable, true);
  assert.equal(sampleScore(gaps.review), 55);
  assert.equal(gaps.review.suitable, false);
});

test('sample work evidence is a verbatim excerpt of a fictional work bullet', () => {
  for (const key of ['ready', 'gaps']) {
    const sample = getSample(key);
    const bullets = sample.profile.document.experience.flatMap((role) => role.bullets);
    for (const mark of sample.review.required) {
      if (mark.present && mark.source === 'work') assert.ok(bullets.some((bullet) => bullet.includes(mark.quote)), `${key}: ${mark.name}`);
    }
  }
});

test('unknown sample identifiers do not resolve to a profile', () => {
  assert.equal(getSample('someone-real'), null);
});

test('sample profiles provide fuller fictional details in distinct visual styles', () => {
  const ready = getSample('ready').profile;
  const gaps = getSample('gaps').profile;
  assert.equal(ready.variant, 'ink');
  assert.equal(gaps.variant, 'studio');
  for (const profile of [ready, gaps]) {
    assert.equal(profile.document.experience.length, 3);
    assert.match(profile.document.contact.email, /@example\.com$/);
    assert.ok(profile.document.contact.links.length);
  }
});
