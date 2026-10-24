"""Supabase verifies tokens; only a verified PSU Google identity enters student routes."""
import re
from uuid import UUID
from urllib.parse import urlsplit

import httpx
from fastapi import Request

from .session import ApiError


class SupabaseAuth:
    def __init__(self, url, key, *, client=None):
        parsed = urlsplit(url)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
                or parsed.query or parsed.fragment or parsed.path not in ('', '/') or not key):
            raise ValueError('invalid_auth_configuration')
        self.url, self.key, self.client = url.rstrip('/'), key, client

    async def verify(self, token):
        if not isinstance(token, str) or not re.fullmatch(r'[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', token) or len(token) > 8192:
            raise ApiError(401, 'sign_in_required')
        try:
            async def request(client):
                async with client.stream('GET', self.url + '/auth/v1/user', headers={
                        'apikey': self.key, 'Authorization': 'Bearer ' + token}, timeout=10) as response:
                    if response.status_code in (401, 403):
                        raise ApiError(401, 'sign_in_required')
                    if response.status_code != 200:
                        raise ApiError(503, 'auth_unavailable')
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > 65536:
                            raise ApiError(503, 'auth_unavailable')
                    import json
                    return json.loads(body)
            if self.client is not None:
                data = await request(self.client)
            else:
                async with httpx.AsyncClient(follow_redirects=False) as client:
                    data = await request(client)
        except (httpx.HTTPError, ValueError):
            raise ApiError(503, 'auth_unavailable') from None
        try:
            email = data['email'].lower()
            account = str(UUID(data['id']))
            identities = data.get('identities', [])
            google = any(identity.get('provider') == 'google' and
                identity.get('identity_data', {}).get('email', '').lower() == email and
                identity.get('identity_data', {}).get('email_verified') is True for identity in identities)
            if (not data.get('email_confirmed_at') or data.get('deleted_at') or
                    email.count('@') != 1 or email.split('@')[1] != 'psu.palawan.edu.ph' or not google):
                raise ValueError('wrong_identity')
        except (KeyError, ValueError, TypeError, AttributeError):
            raise ApiError(403, 'psu_account_required') from None
        return account


async def authorize(request: Request):
    if request.url.path in ('/health/live', '/health/ready') or not request.app.state.settings.require_auth:
        return
    value = request.headers.get('authorization', '')
    if not value.startswith('Bearer ') or request.app.state.services.auth is None:
        raise ApiError(401, 'sign_in_required')
    request.state.account_id = await request.app.state.services.auth.verify(value[7:])
