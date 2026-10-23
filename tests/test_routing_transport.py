import asyncio
import importlib
import json

import httpx
import pytest


def api():
    return importlib.import_module('backend.bintanong_routing.transport')


def handler_for(*, n_ctx=2048, token_count=10, content='{}', status=200):
    calls = []
    def handler(request):
        data = json.loads(request.content) if request.content else {}
        calls.append((request.url.path, data))
        if request.url.path == '/props':
            return httpx.Response(200, json=dict(default_generation_settings=dict(n_ctx=n_ctx),
                chat_template='actual-model-template', model_path='/models/existing.gguf', build_info='test-build'))
        if request.url.path == '/apply-template':
            return httpx.Response(200, json=dict(prompt='<bos>complete messages<assistant>'))
        if request.url.path == '/tokenize':
            return httpx.Response(200, json=dict(tokens=list(range(token_count))))
        return httpx.Response(status, json=dict(choices=[dict(finish_reason='stop', message=dict(content=content))]))
    return handler, calls


def test_model_template_tokenization_and_schema_constrained_payload():
    async def run():
        handler, calls = handler_for()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client)
            assert await transport.infer([dict(role='user', content='hello')], {'type':'object'}) == '{}'
            assert [p for p, _ in calls] == ['/props','/apply-template','/tokenize','/tokenize','/tokenize','/v1/chat/completions']
            assert calls[2][1]['add_special'] is False and calls[2][1]['parse_special'] is True
            await transport.infer([dict(role='user', content='again')], {'type':'object'})
            assert [p for p, _ in calls][6:] == ['/props','/apply-template','/tokenize','/v1/chat/completions']  # cached
            payload = calls[-1][1]
            assert calls[1][1]['reasoning_effort'] == payload['reasoning_effort']
            assert payload['response_format'] == {'type':'json_object', 'schema':{'type':'object'}}
            assert payload['temperature'] == 0 and payload['max_tokens'] == 768
            assert transport.metadata['build'] == 'test-build'
            assert transport.metadata['model_file'] == 'existing.gguf'
            assert len(transport.metadata['chat_template_sha256']) == 64
    asyncio.run(run())


@pytest.mark.parametrize('constrained', [True, False])
def test_explicit_evaluation_profile_records_sampling_defaults_without_prompt_text(constrained):
    async def run():
        original, calls = handler_for()
        def handler(request):
            response = original(request)
            if request.url.path == '/props':
                data = json.loads(response.content)
                data['default_generation_settings']['params'] = dict(
                    temperature=0.8, seed=4294967295, top_k=40, top_p=0.95,
                    min_p=0.05, repeat_penalty=1.0, samplers=['top_k', 'temperature'],
                    grammar='private grade data', stop=['private grade data'],
                    unexpected='private grade data')
                data['default_generation_settings']['prompt'] = 'private grade data'
                return httpx.Response(200, json=data)
            return response
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client, constrained=constrained)
            assert await transport.infer([], {}) == '{}'
            payload = calls[-1][1]
            assert payload['cache_prompt'] is False
            assert payload['temperature'] == 0 and payload['seed'] == 0
            assert payload['reasoning_effort'] == calls[1][1]['reasoning_effort'] == 'none'
            assert transport.metadata['inference_profile'] == 'p07-greedy-no-prefix-cache-v1'
            assert transport.metadata['cache_prompt'] is False
            assert transport.metadata['reasoning_effort'] == 'none'
            defaults = transport.metadata['server_sampling_defaults']
            assert defaults['temperature'] == 0.8 and defaults['seed'] == 4294967295
            assert defaults['top_k'] == 40 and defaults['min_p'] == 0.05
            assert defaults['samplers'] == ['top_k', 'temperature']
            assert 'private grade data' not in json.dumps(transport.metadata)
    asyncio.run(run())


def test_absent_sampling_defaults_are_not_fabricated():
    async def run():
        handler, _ = handler_for()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client)
            assert await transport.infer([], {}) == '{}'
            assert transport.metadata['server_sampling_defaults'] == {}
    asyncio.run(run())


@pytest.mark.parametrize('params', [None, [], True, 'private grade data'])
def test_malformed_sampling_defaults_stop_before_generation(params):
    async def run():
        original, calls = handler_for()
        def handler(request):
            response = original(request)
            if request.url.path == '/props':
                data = json.loads(response.content)
                data['default_generation_settings']['params'] = params
                return httpx.Response(200, json=data)
            return response
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(api().RuntimeFailure, match='^invalid_server_response$'):
                await api().LlamaTransport('http://localhost', client=client).infer([], {})
        assert [path for path, _ in calls] == ['/props']
    asyncio.run(run())


def test_complete_message_overflow_stops_before_inference():
    async def run():
        handler, calls = handler_for(n_ctx=800, token_count=100)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(api().RuntimeFailure, match='context_overflow'):
                await api().LlamaTransport('http://localhost', client=client).infer([], {})
        assert '/v1/chat/completions' not in [p for p, _ in calls]
    asyncio.run(run())


@pytest.mark.parametrize('kind,code', [('timeout','model_timeout'), ('http','model_http_error'),
                                      ('oversized','server_response_too_large'),
                                      ('malformed','invalid_server_response')])
def test_server_errors_never_expose_query_or_response_text(kind, code):
    async def run():
        def handler(request):
            if kind == 'timeout':
                raise httpx.ReadTimeout('private grade data', request=request)
            if kind == 'oversized':
                return httpx.Response(200, content=b'private grade data' * 100000)
            if kind == 'malformed':
                return httpx.Response(200, text='private grade data')
            return httpx.Response(503, text='private grade data')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(api().RuntimeFailure) as error:
                await api().LlamaTransport('http://localhost', client=client).infer([], {})
        assert str(error.value) == code
        assert 'private' not in str(error.value)
    asyncio.run(run())


@pytest.mark.parametrize('response', [{'choices':['invalid']}, {'choices':[{'message':[]}]},
                                      {'choices':None}, ['invalid']])
def test_malformed_successful_completion_envelopes_become_typed_failures(response):
    async def run():
        original, _ = handler_for()
        def handler(request):
            if request.url.path == '/v1/chat/completions':
                return httpx.Response(200, json=response)
            return original(request)
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(api().RuntimeFailure, match='invalid_server_response'):
                await api().LlamaTransport('http://localhost', client=client).infer([], {})
    asyncio.run(run())


def thought_handler(template):
    calls = []
    def handler(request):
        data = json.loads(request.content) if request.content else {}
        calls.append((request.url.path, data))
        if request.url.path == '/props':
            return httpx.Response(200, json=dict(default_generation_settings=dict(n_ctx=2048),
                chat_template=template, model_path='/models/existing.gguf', build_info='test-build'))
        if request.url.path == '/apply-template':
            return httpx.Response(200, json=dict(prompt='<bos>complete messages<assistant>'))
        if request.url.path == '/tokenize':
            special = {'<|channel>': [100], '\n': [107], '\n\n': [108]}
            return httpx.Response(200, json=dict(tokens=special.get(data['content'], list(range(10)))))
        return httpx.Response(200, json=dict(choices=[dict(finish_reason='stop', message=dict(content='{}'))]))
    return handler, calls


def test_thought_channel_opener_is_banned_when_the_template_defines_it():
    # Observed on real prompts: Gemma spent the whole output budget in a hidden thought channel.
    async def run():
        handler, calls = thought_handler('... <|channel>thought ... <channel|> ...')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client)
            await transport.infer([dict(role='user', content='hello')], {'type': 'object'})
        assert [100, False] in calls[-1][1]['logit_bias']
        assert transport.metadata['banned_reasoning_token'] == 100
    asyncio.run(run())


def test_templates_without_a_thought_channel_are_unchanged():
    async def run():
        handler, calls = thought_handler('actual-model-template')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client)
            await transport.infer([dict(role='user', content='hello')], {'type': 'object'})
        assert all(pair[0] != 100 for pair in calls[-1][1].get('logit_bias', []))
    asyncio.run(run())


def test_constrained_json_output_cannot_spend_tokens_on_line_breaks():
    # Real routing output was ~40% pretty-print whitespace despite the compact-JSON instruction.
    async def run():
        handler, calls = thought_handler('actual-model-template')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client)
            await transport.infer([dict(role='user', content='hello')], {'type': 'object'})
        assert [107, False] in calls[-1][1]['logit_bias'] and [108, False] in calls[-1][1]['logit_bias']
    asyncio.run(run())


def test_unconstrained_output_keeps_line_breaks():
    async def run():
        handler, calls = thought_handler('actual-model-template')
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client, constrained=False)
            await transport.infer([dict(role='user', content='hello')], {'type': 'object'})
        assert 'logit_bias' not in calls[-1][1]
    asyncio.run(run())


def test_prefix_cache_profile_is_explicit_and_recorded():
    # Owner, 23 Oct 2026 (latency): opt-in prompt reuse; the no-cache profile stays the default.
    async def run():
        handler, calls = handler_for()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = api().LlamaTransport('http://localhost', client=client, prefix_cache=True)
            assert await transport.infer([], {}) == '{}'
            assert calls[-1][1]['cache_prompt'] is True
            assert transport.metadata['inference_profile'] == 'p09-greedy-prefix-cache-v1'
            assert transport.metadata['cache_prompt'] is True
    asyncio.run(run())
    with pytest.raises(ValueError):
        api().LlamaTransport('http://localhost', prefix_cache='yes')
