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
            assert [p for p, _ in calls] == ['/props','/apply-template','/tokenize','/v1/chat/completions']
            assert calls[2][1]['add_special'] is False and calls[2][1]['parse_special'] is True
            payload = calls[-1][1]
            assert payload['response_format'] == {'type':'json_object', 'schema':{'type':'object'}}
            assert payload['temperature'] == 0 and payload['max_tokens'] == 768
            assert transport.metadata['build'] == 'test-build'
            assert transport.metadata['model_file'] == 'existing.gguf'
            assert len(transport.metadata['chat_template_sha256']) == 64
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
