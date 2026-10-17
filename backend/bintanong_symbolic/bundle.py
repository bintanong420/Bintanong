"""Reproducible runtime data artifacts; hashes bind content, never authorize use."""
import hashlib
from collections.abc import Mapping
from pathlib import Path

from .compiler import _digest, _json, compile_curriculum_review_bundle

_ENGINE = Path(__file__).with_name('curriculum_runtime.pl')
_MAX_PAYLOAD_BYTES = 524_288


def prepare_runtime_bundle(ledger) -> dict:
    """Prepare an inactive artifact without consulting Prolog or changing source states."""
    compiled = compile_curriculum_review_bundle(ledger)
    if compiled['status'] == 'blocked':
        raise ValueError('compiler holds prevent runtime preparation')
    checked = compiled['ledger']

    def expression(node):
        result = {k:v for k,v in node.items() if k not in ('source_spans','items')}
        if 'items' in node:
            result['items'] = [expression(x) for x in node['items']]
        return result

    coverage = {c['course_id']:c for c in compiled['coverage']}
    payload = {'synthetic':checked['synthetic'], 'curriculum_id':checked['scope']['curriculum_id'],
        'courses':[
            {'id':c['course_id'], 'reviewed':c['review_state']=='reviewed',
             'rule':expression(c['prerequisites']) if coverage[c['course_id']]['direct_rule']=='reviewed'
                    else {'kind':'unresolved'}} for c in checked['courses']]}
    encoded = _json(payload)
    if len(encoded.encode()) > _MAX_PAYLOAD_BYTES:
        raise ValueError('runtime bundle exceeds byte limit')
    engine_sha = hashlib.sha256(_ENGINE.read_bytes()).hexdigest()
    prefix = 'synthetic-runtime-v1-' if checked['synthetic'] else 'inactive-runtime-v1-'
    result = {'schema_version':'curriculum-runtime-bundle-v1',
        'review_bundle_sha256':compiled['content_sha256'], 'ledger':checked,
        'engine_sha256':engine_sha, 'payload':payload, 'payload_sha256':_digest(encoded),
        'runtime_version':prefix+_digest(_json([compiled,engine_sha])),
        'coverage':compiled['coverage'], 'release_holds':compiled['release_holds'],
        'runtime_ready':False, 'activation_allowed':False, 'eligibility_executable':False,
        'approval_id':None}
    result['content_sha256'] = _digest(_json(result))
    return result


def validate_runtime_bundle(bundle) -> dict:
    """Rebuild every field against the current compiler/engine; return detached data."""
    if not isinstance(bundle, Mapping) or 'ledger' not in bundle:
        raise ValueError('complete runtime bundle required')
    rebuilt = prepare_runtime_bundle(bundle['ledger'])
    if _json(bundle) != _json(rebuilt):
        raise ValueError('runtime bundle differs from rebuilt ledger, coverage, payload or engine')
    return rebuilt
