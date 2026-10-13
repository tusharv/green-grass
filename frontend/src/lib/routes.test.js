import test from 'node:test';
import assert from 'node:assert/strict';
import { matchRoute } from './routes.js';

test('visitors can reach the landing page without signing in', () => {
  assert.deepEqual(matchRoute('/'), { name: 'home', auth: false });
});

test('sample profiles and evaluations are public and limited to known samples', () => {
  assert.deepEqual(matchRoute('/samples/ready/profile'), { name: 'sample-profile', auth: false, sample: 'ready' });
  assert.deepEqual(matchRoute('/samples/gaps/evaluation'), { name: 'sample-evaluation', auth: false, sample: 'gaps' });
  assert.deepEqual(matchRoute('/samples/unknown/profile'), { name: 'missing', auth: false });
});

test('privacy and terms are public pages', () => {
  assert.deepEqual(matchRoute('/privacy'), { name: 'privacy', auth: false });
  assert.deepEqual(matchRoute('/terms'), { name: 'terms', auth: false });
});

test('private CV and application pages still require sign-in', () => {
  for (const path of ['/cvs/new', '/cvs/1', '/apply?cv=1', '/applications/1']) {
    assert.equal(matchRoute(path).auth, true, path);
  }
});
