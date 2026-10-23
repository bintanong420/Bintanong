"""Master 15.3 boundary checks for the private-context package (tested boundary only, not every threat)."""
import ast
import io
import tempfile
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from backend.bintanong_private_context.grades import extract_grade_rows
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_private_context.uploads import UploadRejected, validate_upload
from test_private_context_grades import CATALOG

PACKAGE = Path(__file__).resolve().parents[1] / 'backend' / 'bintanong_private_context'
SECRET = 'ZZSECRET-TOKEN-91'


def pdf_with(text):
    out = io.BytesIO()
    c = canvas.Canvas(out)
    c.drawString(60, 760, 'CC 5/L ' + text + ' 1.75 3')
    c.showPage()
    c.save()
    return out.getvalue()


def test_upload_extract_and_confirm_write_no_temporary_files():
    before = set(Path(tempfile.gettempdir()).iterdir())
    store = SessionStore()
    issued = store.issue()
    result = extract_grade_rows(validate_upload(pdf_with(SECRET)), CATALOG, program_id='bscs', curriculum_id='bscs-2018')
    store.set_pending(issued.credential, result)
    store.confirm_pending(issued.credential, {result.rows[0].row_id: ('cc-105', 'passed')})
    assert set(Path(tempfile.gettempdir()).iterdir()) == before


def test_private_package_has_no_path_to_institutional_storage_retrieval_or_ingestion():
    forbidden = ('bintanong_storage', 'bintanong_retrieval', 'bintanong_embedding', 'bintanong_tools',
                 'bintanong_orchestration', 'supabase', 'asyncpg', 'httpx')
    for source in PACKAGE.glob('*.py'):
        tree = ast.parse(source.read_text(encoding='utf-8'))
        modules = [n.module or '' for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        modules += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        assert not [m for m in modules if any(f in m for f in forbidden)], source.name


def test_private_package_never_logs_prints_or_opens_files():
    for source in PACKAGE.glob('*.py'):
        tree = ast.parse(source.read_text(encoding='utf-8'))
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        modules = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        assert not names & {'print', 'open'}, source.name
        assert not attrs & {'write_text', 'write_bytes', 'save', 'debug', 'info', 'warning', 'exception'}, source.name
        assert 'logging' not in modules, source.name


@pytest.mark.parametrize('data', [b'%PDF-1.7\n' + SECRET.encode(), SECRET.encode(), b'\x89PNG\r\n\x1a\n' + SECRET.encode()])
def test_rejection_reasons_are_fixed_codes_that_never_echo_file_content(data):
    with pytest.raises(UploadRejected) as error:
        validate_upload(data)
    assert SECRET not in str(error.value) and SECRET not in repr(error.value)
