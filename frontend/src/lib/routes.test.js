import test from 'node:test';
import assert from 'node:assert/strict';
import { matchRoute } from './routes.js';

test('visitors can reach the landing page without signing in', () => {
  assert.deepEqual(matchRoute('/'), { name: 'home', auth: false });
});

test('private CV and application pages still require sign-in', () => {
  for (const path of ['/cvs/new', '/cvs/1', '/apply?cv=1', '/applications/1']) {
    assert.equal(matchRoute(path).auth, true, path);
  }
});
