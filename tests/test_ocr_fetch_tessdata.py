import hashlib
import importlib.util
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("fetch_tessdata", REPO / "scripts" / "fetch_tessdata.py")
fetch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fetch)


def _source(tmp_path, payload=b"model bytes"):
    src = tmp_path / "src" / "fil.traineddata"
    src.parent.mkdir(exist_ok=True)
    src.write_bytes(payload)
    return {"fil.traineddata": (src.as_uri(), hashlib.sha256(payload).hexdigest())}


def test_the_pins_are_a_commit_url_and_a_sha256_for_fil_and_eng():
    assert set(fetch.MODELS) == {"fil.traineddata", "eng.traineddata"}
    for url, digest in fetch.MODELS.values():
        assert re.search(r"/tessdata_best/raw/[0-9a-f]{40}/", url)
        assert re.fullmatch(r"[0-9a-f]{64}", digest)


def test_fetch_writes_a_verified_file_then_leaves_it_alone(tmp_path):
    models, dest = _source(tmp_path), tmp_path / "tessdata"
    assert fetch.fetch(dest, models) == {"fil.traineddata": "downloaded"}
    assert (dest / "fil.traineddata").read_bytes() == b"model bytes"
    assert fetch.fetch(dest, models) == {"fil.traineddata": "present"}
    assert not list(dest.glob("*.part"))


def test_a_wrong_hash_is_refused_and_leaves_no_file(tmp_path):
    models = {"fil.traineddata": (_source(tmp_path)["fil.traineddata"][0], "0" * 64)}
    dest = tmp_path / "tessdata"
    with pytest.raises(fetch.HashMismatch):
        fetch.fetch(dest, models)
    assert not list(dest.glob("*"))


def test_a_corrupt_existing_file_is_replaced(tmp_path):
    models, dest = _source(tmp_path), tmp_path / "tessdata"
    dest.mkdir()
    (dest / "fil.traineddata").write_bytes(b"truncated")
    assert fetch.fetch(dest, models) == {"fil.traineddata": "downloaded"}
    assert (dest / "fil.traineddata").read_bytes() == b"model bytes"


def test_check_only_reports_without_downloading(tmp_path):
    models, dest = _source(tmp_path), tmp_path / "tessdata"
    assert fetch.check(dest, models) == {"fil.traineddata": "missing"}
    fetch.fetch(dest, models)
    assert fetch.check(dest, models) == {"fil.traineddata": "ok"}
    (dest / "fil.traineddata").write_bytes(b"x")
    assert fetch.check(dest, models) == {"fil.traineddata": "corrupt"}


def test_the_default_folder_is_outside_the_repository():
    assert REPO not in fetch.default_dest().parents


def test_main_downloads_into_dest_and_prints_the_prefix(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(fetch, "MODELS", _source(tmp_path))
    assert fetch.main(["--dest", str(tmp_path / "t")]) == 0
    assert "TESSDATA_PREFIX" in capsys.readouterr().out
    assert fetch.main(["--dest", str(tmp_path / "t"), "--check"]) == 0
    (tmp_path / "t" / "fil.traineddata").write_bytes(b"bad")
    assert fetch.main(["--dest", str(tmp_path / "t"), "--check"]) == 1
