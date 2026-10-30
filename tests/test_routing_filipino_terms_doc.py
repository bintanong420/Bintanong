"""The reviewed Filipino penalty-row words in docs/evaluation/accepted-input-forms.md equal the code's list."""
from pathlib import Path

from backend.bintanong_routing import filipino_terms

DOC = Path(__file__).resolve().parents[1] / 'docs' / 'evaluation' / 'accepted-input-forms.md'


def documented():
    section = DOC.read_text(encoding='utf-8').split('## Filipino words for printed penalty rows')[1].split('\n## ')[0]
    rows = [line.strip('|').split('|') for line in section.splitlines() if line.startswith('| ') and '---' not in line]
    return {term.strip(): tuple(f.strip() for f in forms.split(',')) for term, forms in rows[1:]}


def test_the_documented_table_is_the_reviewed_list():
    assert documented() == filipino_terms._REVIEWED
