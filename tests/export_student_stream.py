"""Synthetic Python emitter fixture consumed by the installed SDK's parser test."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_api_presentation import answer_for
from backend.bintanong_api.stream import DONE, answer_parts, encode

answer = answer_for('Hybrid')
if len(sys.argv) > 1:
    case = sys.argv[1]
    answer = answer.model_copy(update={
        'status': case, 'language': 'taglish', 'decision': None,
        'missing_facts': ('program_id', 'curriculum_id') if case == 'clarification_needed' else (),
    })

sys.stdout.buffer.write(encode({'type': 'start', 'messageId': 'msg-synthetic'}))
sys.stdout.buffer.write(encode({'type': 'data-status', 'data': {'stage': 'waiting'}, 'transient': True}))
for part in answer_parts(answer, 'msg-synthetic'):
    sys.stdout.buffer.write(encode(part))
sys.stdout.buffer.write(DONE)
