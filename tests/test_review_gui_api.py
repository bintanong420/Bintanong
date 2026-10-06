"""The loopback API. Needs the `review` extra (FastAPI, httpx); skipped where it is not installed."""

import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from backend.bintanong_tools.prospectus_extractor.ledger import read_entries  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.app import CSP, create_app, new_token  # noqa: E402
from backend.bintanong_tools.prospectus_review_gui.session import open_session  # noqa: E402

import review_gui_fixtures as rf  # noqa: E402

PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"


@pytest.fixture
def env(tmp_path):
    ws = rf.workspace(tmp_path, pdf=True)
    session = open_session(ws.candidate, ws.identity, "Nestor", ws.review, pdf_path=ws.pdf)
    token = new_token()
    client = TestClient(create_app(session, token, port=PORT), base_url=BASE)
    yield ws, session, client, token
    session.close()


def post(client, token, path, body, **headers):
    return client.post(path, content=json.dumps(body), headers={"X-Review-Token": token, "Content-Type": "application/json", **headers})


# --- security


def test_foreign_host_header_is_refused_403(env):
    _ws, _s, client, _t = env
    for host in ("evil.example", f"evil.example:{PORT}", "127.0.0.1.evil.example", f"127.0.0.1:{PORT + 1}", ""):
        response = client.get("/api/state", headers={"host": host})
        assert response.status_code == 403, host
        assert "Content-Security-Policy" in response.headers


def test_localhost_and_127_0_0_1_hosts_are_accepted(env):
    _ws, _s, client, _t = env
    for host in (f"127.0.0.1:{PORT}", f"localhost:{PORT}", f"LOCALHOST:{PORT}"):
        assert client.get("/api/state", headers={"host": host}).status_code == 200, host


def test_post_without_token_is_403(env):
    ws, _s, client, _t = env
    response = client.post("/api/answer", content=json.dumps({"qid": "S3-01", "choice": "yes"}),
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 403
    assert not ws.ledger.exists()


def test_post_with_wrong_token_is_403(env):
    ws, _s, client, token = env
    for wrong in ("x", token[:-1], token + "x", ""):
        assert post(client, wrong, "/api/answer", {"qid": "S3-01", "choice": "yes"}).status_code == 403
    assert not ws.ledger.exists()


def test_post_with_foreign_origin_is_403(env):
    ws, _s, client, token = env
    for origin in ("http://evil.example", f"http://127.0.0.1:{PORT + 1}", "null", f"https://127.0.0.1:{PORT}"):
        response = post(client, token, "/api/answer", {"qid": "S3-01", "choice": "yes"}, Origin=origin)
        assert response.status_code == 403, origin
    assert not ws.ledger.exists()
    assert post(client, token, "/api/answer", {"qid": "S3-01", "choice": "yes"}, Origin=BASE).status_code == 200


def test_get_requests_need_no_token_but_do_need_a_good_host(env):
    _ws, _s, client, _t = env
    for path in ("/", "/api/state", "/api/queue", "/api/question/S3-01", "/api/twin", "/api/page/1.png"):
        assert client.get(path).status_code == 200, path
        assert client.get(path, headers={"host": "evil.example"}).status_code == 403, path


def test_csp_and_no_store_headers_on_every_response(env):
    _ws, _s, client, token = env
    responses = [client.get(p) for p in ("/", "/api/state", "/api/queue", "/api/question/S9-99", "/nope")]
    responses += [post(client, token, "/api/answer", {"qid": "S3-01", "choice": "maybe"}), client.get("/", headers={"host": "x"})]
    for response in responses:
        assert response.headers["Content-Security-Policy"] == CSP
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
    png = client.get("/api/page/1.png")
    assert png.headers["Content-Security-Policy"] == CSP and png.headers["Cache-Control"] == "private, max-age=300"
    assert "default-src 'none'" in CSP and "frame-ancestors 'none'" in CSP and "http" not in CSP


def test_token_differs_between_two_app_instances(env):
    _ws, session, client, token = env
    other = new_token()
    assert other != token and len(token) >= 32
    page = client.get("/").text
    assert f'<meta name="review-token" content="{token}">' in page
    other_client = TestClient(create_app(session, other, port=PORT), base_url=BASE)
    assert other in other_client.get("/").text and token not in other_client.get("/").text
    assert post(other_client, token, "/api/materialise", {}).status_code == 403


# --- behavior


def test_api_answer_returns_updated_state_and_next_question(env):
    ws, _s, client, token = env
    first = client.get("/api/queue").json()["queue"][0]["qid"]
    response = post(client, token, "/api/answer", {"qid": first, "choice": "no", "reason": "cannot read it"})
    assert response.status_code == 200
    body = response.json()
    assert body["written"] == 1 and body["errors"] == []
    assert body["state"]["content_review"]["state"] == "partially_reviewed"
    assert body["next"] not in (None, first)   # a No stays open, but it is not the next question (see the C3 tests)
    assert len(read_entries(ws.ledger)) == 1


def test_api_answer_errors_are_422_and_write_nothing(env):
    ws, _s, client, token = env
    for body in ({"qid": "S3-01", "choice": "other", "edits": {"lecture_units": "3.5"}, "reason": "r"},
                 {"qid": "S3-01", "choice": "maybe"}, {"qid": "S3-01"}, {"qid": 5, "choice": "yes"},
                 {"qid": "S3-01", "choice": "yes", "edits": ["x"]}, {"qid": "S3-01", "choice": "yes", "proposals": [1]}):
        response = post(client, token, "/api/answer", body)
        assert response.status_code == 422, body
        assert response.json()["errors"], body
    bad_json = client.post("/api/answer", content="{not json", headers={"X-Review-Token": token, "Content-Type": "application/json"})
    assert bad_json.status_code == 422
    assert not ws.ledger.exists()


def test_api_question_unknown_qid_is_404(env):
    _ws, _s, client, token = env
    assert client.get("/api/question/S9-99").status_code == 404
    assert post(client, token, "/api/answer", {"qid": "S9-99", "choice": "yes"}).status_code == 404


def test_api_queue_mode(env):
    _ws, _s, client, _t = env
    printed = client.get("/api/queue?mode=print").json()
    assert [q["position"] for q in printed["queue"]] == sorted(q["position"] for q in printed["queue"])
    assert {q["qid"] for q in printed["all"]} >= {q["qid"] for q in printed["queue"]}
    assert client.get("/api/queue?mode=random").status_code == 422


def test_api_page_png_scale_is_bounded_422(env):
    _ws, _s, client, _t = env
    assert client.get("/api/page/1.png?scale=3").status_code == 200
    for scale in ("0", "-1", "10", "3.5", "nan", "big"):
        assert client.get(f"/api/page/1.png?scale={scale}").status_code == 422, scale
    assert client.get("/api/page/9.png").status_code == 404
    response = client.get("/api/page/1.png")
    assert response.headers["content-type"] == "image/png" and response.content[:4] == b"\x89PNG"


def test_api_page_without_pdf_is_404_with_message(tmp_path):
    ws = rf.workspace(tmp_path)
    with open_session(ws.candidate, ws.identity, "Nestor", ws.review) as session:
        client = TestClient(create_app(session, new_token(), port=PORT), base_url=BASE)
        response = client.get("/api/page/1.png")
        assert response.status_code == 404 and "no PDF" in response.json()["error"]


def test_api_question_includes_boxes_and_warnings(env):
    _ws, _s, client, _t = env
    view = client.get("/api/question/S1-01").json()
    assert view["boxes"]["1"]["warning"] is None and view["boxes"]["1"]["boxes"]
    assert all(set(b["fractions"]) == {"left", "top", "width", "height"} for b in view["boxes"]["1"]["boxes"])
    assert view["course"]["course"]["course_code"] == "CS 1" and view["twin_cell_ids"]
    eth = client.get("/api/question/S3-01").json()   # GE-ET is on page 2; the PDF has one page
    assert eth["boxes"]["2"] == {"boxes": [], "warning": "page 2 is not in the PDF"}


def test_api_error_messages_never_include_a_server_path(tmp_path):
    ws = rf.workspace(tmp_path)
    missing = tmp_path / "secret folder" / "gone.pdf"
    with open_session(ws.candidate, ws.identity, "Nestor", ws.review, pdf_path=missing) as session:
        client = TestClient(create_app(session, new_token(), port=PORT), base_url=BASE)
        page = client.get("/api/page/1.png").json()["error"]
        state = client.get("/api/state").text
        question = client.get("/api/question/S1-01").text
    assert "gone.pdf" in page
    for text in (page, state, question):
        assert "secret folder" not in text and str(tmp_path) not in text and str(tmp_path).replace("\\", "\\\\") not in text


def test_api_materialise_writes_the_corrected_candidate(env):
    ws, _s, client, token = env
    post(client, token, "/api/answer", {"qid": "S3-01", "choice": "other", "edits": {"course_title": "Ethics"}, "reason": "PDF"})
    response = post(client, token, "/api/materialise", {})
    assert response.status_code == 200 and response.json()["applied"] == 1 and response.json()["file"] == "corrected_candidate.json"
    assert (ws.review / "corrected_candidate.json").is_file()
    assert str(ws.review) not in response.text


def test_api_twin_without_docling_json_says_unavailable(env):
    _ws, _s, client, _t = env
    twin = client.get("/api/twin").json()
    assert twin["html"] is None and "markup twin unavailable" in twin["reason"]


def test_static_files_are_served_and_others_are_not(env):
    _ws, _s, client, _t = env
    for name in ("review.css", "review.js"):
        assert client.get(f"/static/{name}").status_code == 200
    for bad in ("/static/../session.py", "/static/..%2fsession.py", "/static/..%2f..%2fsession.py", "/static/nope.js",
                "/static/%2e%2e/app.py"):
        assert client.get(bad).status_code == 404, bad


# --- C2 / S5 / S6: a bad answer is a 422 and nothing is written; a huge body is a 413


def test_surrogate_nul_and_newline_in_a_title_are_422_and_write_nothing(env):
    ws, _s, client, token = env
    for bad in ("Bad \ud800 title", "Nul \x00 title", "Line\nbreak"):
        response = post(client, token, "/api/answer", {"qid": "S1-02", "choice": "other", "edits": {"course_title": bad}, "reason": "r"})
        assert response.status_code == 422 and response.json()["errors"], repr(bad)
    response = post(client, token, "/api/answer", {"qid": "S1-02", "choice": "yes", "reason": "two\nlines"})
    assert response.status_code == 422
    response = post(client, token, "/api/answer", {"qid": "S1-0\ud800", "choice": "yes"})
    assert response.status_code in (404, 422)
    assert not ws.ledger.exists() or read_entries(ws.ledger) == []


def test_overlong_reason_is_422_and_oversized_body_is_413(env):
    ws, _s, client, token = env
    response = post(client, token, "/api/answer", {"qid": "S1-02", "choice": "yes", "reason": "x" * 2001})
    assert response.status_code == 422 and "2000" in response.json()["errors"][0]
    big = {"qid": "S1-02", "choice": "yes", "reason": "x", "edits": {"course_title": "y" * 70000}}
    assert post(client, token, "/api/answer", big).status_code == 413
    # a body that understates its length (or is chunked) is cut off while it is read, not after
    liar = client.post("/api/answer", content=b"x" * 70000, headers={"X-Review-Token": token, "Content-Type": "application/json", "Content-Length": "10"})
    assert liar.status_code == 413
    assert not ws.ledger.exists() or read_entries(ws.ledger) == []
    assert post(client, token, "/api/answer", {"qid": "S1-02", "choice": "yes", "reason": "x" * 2000}).status_code == 200


# --- C3: `next` is the question after the answered one in the reviewer's mode, never the answered one


def _queue_ids(client, mode):
    return [q["qid"] for q in client.get(f"/api/queue?mode={mode}").json()["queue"]]


@pytest.mark.parametrize("mode", ["attention", "print"])
def test_next_after_a_no_is_the_following_question_in_that_mode(env, mode):
    _ws, _s, client, token = env
    before = _queue_ids(client, mode)
    assert len(before) >= 3
    body = {"qid": before[0], "choice": "no", "reason": "cannot tell", "mode": mode}
    if before[0].endswith(":confirm"):
        body = {"qid": before[0], "choice": "no", "mode": mode}   # a section No writes nothing and stays open
    result = post(client, token, "/api/answer", body).json()
    assert result["next"] == before[1], (mode, before[:3])
    last = {**body, "qid": before[-1]}
    if before[-1].endswith(":confirm"):
        last.pop("reason", None)
    else:
        last["reason"] = "cannot tell"
    wrapped = post(client, token, "/api/answer", last).json()
    assert wrapped["next"] not in (None, before[-1])


def test_next_is_none_when_the_answered_question_is_the_only_one_left(env):
    _ws, _s, client, token = env
    for qid in _queue_ids(client, "print")[:-1]:
        post(client, token, "/api/answer", {"qid": qid, "choice": "yes", "reason": "ok"})
    left = _queue_ids(client, "print")
    assert len(left) == 1
    result = post(client, token, "/api/answer", {"qid": left[0], "choice": "no", "reason": "cannot tell"}).json()
    assert result["next"] is None
