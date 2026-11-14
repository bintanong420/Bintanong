import test from 'node:test';
import assert from 'node:assert/strict';
import { isPSUAccount, siteOrigin } from '../lib/auth-policy.ts';

const user = { email: 'synthetic@psu.palawan.edu.ph', email_confirmed_at: '2026-10-24', identities: [{ provider: 'google', identity_data: { email: 'synthetic@psu.palawan.edu.ph', email_verified: true } }] };
test('only verified PSU Google identity permits the student surface', () => {
  assert.equal(isPSUAccount(user), true);
  assert.equal(isPSUAccount({ ...user, email: 'synthetic@psu.palawan.edu.ph.attacker.example' }), false);
  assert.equal(isPSUAccount({ ...user, email_confirmed_at: null }), false);
  assert.equal(isPSUAccount({ ...user, identities: [] }), false);
});
test('OAuth callback origin is configured, with only loopback fallback', () => {
  assert.equal(siteOrigin('https://attacker.example/auth/login', 'https://bintanong.example'), 'https://bintanong.example');
  assert.equal(siteOrigin('http://127.0.0.1:3215/auth/login'), 'http://127.0.0.1:3215');
  assert.throws(() => siteOrigin('https://attacker.example/auth/login'), /site_origin_required/);
  assert.throws(() => siteOrigin('http://127.0.0.1/auth/login', 'https://user:pass@example.com'), /invalid_site_origin/);
});
