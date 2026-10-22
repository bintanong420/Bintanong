"""One bounded synthetic request per process, never an arbitrary Prolog goal."""
from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path

GOAL = 'call_with_time_limit(Limit, bintanong_curriculum:run(Bundle, Curriculum, Course, Facts, Result))'
DEPENDENCIES = 'call_with_time_limit(Limit, bintanong_curriculum:dependencies(Bundle, Curriculum, Course, Result))'


def main():
    try:
        data = sys.stdin.buffer.read(1_048_577)
        if len(data) > 1_048_576:
            raise ValueError('input byte limit')
        payload = json.loads(data)
        expected = {'check_prerequisite_eligibility':'eligibility','list_missing_prerequisites':'eligibility',
                    'list_affected_courses':'dependencies'}.get(payload.get('predicate'))
        if expected is None or payload.get('operation')!=expected:
            raise ValueError('operation does not match fixed predicate')
        if payload['facts']['synthetic'] is not True:
            raise ValueError('synthetic completion facts only')
        research = payload.get('research')
        if payload['bundle']['synthetic'] is False:
            keys = {'mode','institutional_use_allowed','student_facts_synthetic',
                    'generated_output_review','authorization','release_holds','payload_sha256'}
            if not isinstance(research,dict) or set(research)!=keys:
                raise ValueError('explicit offline research context required')
            if len(json.dumps(research,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()) > 8192:
                raise ValueError('research context byte limit')
            auth = research['authorization']
            if not isinstance(auth,dict) or set(auth)!={'purpose','authorization_ref','bundle_sha256','operations'}:
                raise ValueError('closed research authorization required')
            operations = auth['operations']
            if (research['mode']!='offline_research' or research['institutional_use_allowed'] is not False
                    or research['student_facts_synthetic'] is not True or research['generated_output_review']!='pending'
                    or auth['purpose']!='offline_curriculum_acceptance'
                    or not re.fullmatch(r'research-[A-Za-z0-9_-]{1,119}',auth['authorization_ref'])
                    or not re.fullmatch(r'[0-9a-f]{64}',auth['bundle_sha256'])
                    or not isinstance(operations,list) or not operations or len(set(operations))!=len(operations)
                    or not set(operations)<={'check_prerequisite_eligibility','list_missing_prerequisites','list_affected_courses'}
                    or payload['predicate'] not in operations or not research['release_holds']
                    or hashlib.sha256(json.dumps(payload['bundle'],sort_keys=True,ensure_ascii=True,
                        separators=(',',':'),allow_nan=False).encode()).hexdigest()!=research['payload_sha256']):
                raise ValueError('research scope or payload binding differs')
        elif payload['bundle']['synthetic'] is not True or research is not None:
            raise ValueError('invalid execution context')
        import janus_swi as janus
        engine = Path(__file__).resolve().parents[1]/'algorithms/curriculum_runtime.pl'
        engine_bytes = engine.read_bytes()
        if hashlib.sha256(engine_bytes).hexdigest() != payload['engine_sha256']:
            raise ValueError('engine changed after bundle preparation')
        janus.consult(str(engine), data=engine_bytes.decode('utf-8'))
        dependency_query = payload.get('operation')=='dependencies'
        reply = janus.query_once(DEPENDENCIES if dependency_query else GOAL, {'Limit':payload['time_limit'],
            'Bundle':json.dumps(payload['bundle']), 'Curriculum':payload['curriculum_id'],
            'Course':payload['course_id'], 'Facts':json.dumps(payload['facts'])})
        if reply.get('truth') is not True:
            raise ValueError('reasoning failed operationally')
        result = json.loads(reply['Result'])
        fields = ('course_ids','unknown_conditions') if dependency_query else ('satisfied','violated','unknown','conflicts')
        if sum(len(result[k]) for k in fields) > payload['max_conditions']:
            print(json.dumps({'error':'runtime_result_limit'}))
        else:
            out = json.dumps({'result':result})
            print(out if len(out.encode()) <= 65_536 else json.dumps({'error':'runtime_result_limit'}))
    except ImportError:
        print(json.dumps({'error':'runtime_unavailable'}))
    except Exception as exc:
        code = 'runtime_timeout' if 'time_limit_exceeded' in str(exc) else 'runtime_worker_failed'
        print(json.dumps({'error':code}))


if __name__ == '__main__':
    main()
