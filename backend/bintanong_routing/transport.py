"""Bounded llama.cpp HTTP inference; no user text in error messages or logs."""
from __future__ import annotations

import asyncio
import hashlib
import json
import math

import httpx


SAMPLING_SETTING_KEYS = (
    'seed', 'temperature', 'dynatemp_range', 'dynatemp_exponent', 'top_k', 'top_p',
    'min_p', 'top_n_sigma', 'xtc_probability', 'xtc_threshold', 'typical_p',
    'repeat_last_n', 'repeat_penalty', 'presence_penalty', 'frequency_penalty',
    'dry_multiplier', 'dry_base', 'dry_allowed_length', 'dry_penalty_last_n',
    'mirostat', 'mirostat_tau', 'mirostat_eta', 'adaptive_target', 'adaptive_decay',
    'min_keep', 'samplers', 'backend_sampling',
)


THOUGHT_OPENER = '<|channel>'  # Gemma 4 thought-channel opener token

class RuntimeFailure(Exception):
    """Only a fixed, nonsensitive operational code crosses this boundary."""


class LlamaTransport:
    def __init__(self, base_url, *, timeout_seconds=120, max_output_tokens=768,
                 constrained=True, client=None):
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError('invalid_timeout')
        if type(max_output_tokens) is not int or not 1 <= max_output_tokens <= 4096:
            raise ValueError('invalid_output_budget')
        self.base_url = base_url.rstrip('/')
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens
        self.constrained = constrained
        self.client = client
        self.metadata = {}

    async def _json(self, client, method, path, payload=None):
        async with client.stream(method, self.base_url + path, json=payload,
                                 timeout=self.timeout_seconds) as response:
            if response.status_code != 200:
                raise RuntimeFailure('model_http_error')
            body = bytearray()
            async for part in response.aiter_bytes():
                body.extend(part)
                if len(body) > 1_048_576:
                    raise RuntimeFailure('server_response_too_large')
            try:
                return json.loads(body)
            except (ValueError, UnicodeError):
                raise RuntimeFailure('invalid_server_response') from None

    async def infer(self, messages, schema):
        client = self.client or httpx.AsyncClient()
        try:
            async with asyncio.timeout(self.timeout_seconds):
                props = await self._json(client, 'GET', '/props')
                n_ctx = props['default_generation_settings']['n_ctx']
                template = props['chat_template']
                if type(n_ctx) is not int or n_ctx <= 0 or not isinstance(template, str) or not template:
                    raise RuntimeFailure('invalid_server_response')
                defaults = props['default_generation_settings'].get('params', {})
                if not isinstance(defaults, dict):
                    raise RuntimeFailure('invalid_server_response')
                self.metadata = dict(build=props.get('build_info', 'unknown'), n_ctx=n_ctx,
                    model_file=str(props.get('model_path','unknown')).replace('\\','/').rsplit('/',1)[-1],
                    chat_template_sha256=hashlib.sha256(template.encode()).hexdigest(),
                    max_output_tokens=self.max_output_tokens, timeout_seconds=self.timeout_seconds,
                    temperature=0, seed=0,
                    inference_profile='p07-greedy-no-prefix-cache-v1', cache_prompt=False,
                    reasoning_effort='none',
                    server_sampling_defaults={k:defaults[k] for k in SAMPLING_SETTING_KEYS if k in defaults},
                    constrained=self.constrained)
                templated = await self._json(client, 'POST', '/apply-template',
                    {'messages': messages, 'reasoning_effort': 'none'})
                if not isinstance(templated['prompt'], str):
                    raise RuntimeFailure('invalid_server_response')
                counted = await self._json(client, 'POST', '/tokenize', dict(
                    content=templated['prompt'], add_special=False, parse_special=True))
                tokens = counted['tokens']
                if not isinstance(tokens, list) or any(type(t) is not int for t in tokens):
                    raise RuntimeFailure('invalid_server_response')
                if len(tokens) + self.max_output_tokens + 8 > n_ctx:
                    raise RuntimeFailure('context_overflow')
                self.metadata['input_tokens'] = len(tokens)
                # reasoning_effort=none did not stop Gemma's hidden thought channel on long real
                # prompts (it consumed the whole output budget), so ban its opener when defined.
                extra = {}
                if THOUGHT_OPENER in template:
                    opener = (await self._json(client, 'POST', '/tokenize', dict(
                        content=THOUGHT_OPENER, add_special=False, parse_special=True)))['tokens']
                    if len(opener) == 1 and type(opener[0]) is int:
                        extra['logit_bias'] = [[opener[0], False]]
                        self.metadata['banned_reasoning_token'] = opener[0]
                response_format = {'type':'json_object'}
                if self.constrained:
                    response_format['schema'] = schema
                data = await self._json(client, 'POST', '/v1/chat/completions', dict(
                    messages=messages, temperature=0, seed=0, max_tokens=self.max_output_tokens,
                    stream=False, response_format=response_format, reasoning_effort='none', cache_prompt=False,
                    **extra))
                choices = data['choices']
                if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
                    raise RuntimeFailure('invalid_server_response')
                choice = choices[0]
                if choice.get('finish_reason') == 'length':
                    raise RuntimeFailure('truncated_output')
                message = choice['message']
                if not isinstance(message, dict):
                    raise RuntimeFailure('invalid_server_response')
                content = message['content']
                if not isinstance(content, str) or len(content.encode('utf-8')) > 65536:
                    raise RuntimeFailure('invalid_server_response')
                return content
        except (httpx.TimeoutException, TimeoutError):
            raise RuntimeFailure('model_timeout') from None
        except httpx.RequestError:
            raise RuntimeFailure('model_connection_error') from None
        except (KeyError, TypeError, IndexError):
            raise RuntimeFailure('invalid_server_response') from None
        finally:
            if self.client is None:
                await client.aclose()
