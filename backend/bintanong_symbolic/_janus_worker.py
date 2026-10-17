"""One bounded synthetic request per process, never an arbitrary Prolog goal."""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

GOAL = 'call_with_time_limit(Limit, bintanong_curriculum:run(Bundle, Curriculum, Course, Facts, Result))'


def main():
    try:
        data = sys.stdin.buffer.read(1_048_577)
        if len(data) > 1_048_576:
            raise ValueError('input byte limit')
        payload = json.loads(data)
        if payload['bundle']['synthetic'] is not True or payload['facts']['synthetic'] is not True:
            raise ValueError('synthetic execution only')
        import janus_swi as janus
        engine = Path(__file__).with_name('curriculum_runtime.pl')
        engine_bytes = engine.read_bytes()
        if hashlib.sha256(engine_bytes).hexdigest() != payload['engine_sha256']:
            raise ValueError('engine changed after bundle preparation')
        janus.consult(str(engine), data=engine_bytes.decode('utf-8'))
        reply = janus.query_once(GOAL, {'Limit':payload['time_limit'],
            'Bundle':json.dumps(payload['bundle']), 'Curriculum':payload['curriculum_id'],
            'Course':payload['course_id'], 'Facts':json.dumps(payload['facts'])})
        if reply.get('truth') is not True:
            raise ValueError('reasoning failed operationally')
        result = json.loads(reply['Result'])
        if sum(len(result[k]) for k in ('satisfied','violated','unknown','conflicts')) > payload['max_conditions']:
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
