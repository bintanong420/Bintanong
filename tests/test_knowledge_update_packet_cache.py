"""Read-only views reuse a fully checked packet until its files change; saves keep the full check (owner 13 Nov: review is too slow)."""
import pytest

from backend.bintanong_tools.knowledge_update import prepare as prepare_mod
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from test_knowledge_update_review import answer, packet  # noqa: F401  (packet is a fixture)


@pytest.fixture
def counted(monkeypatch):
    calls = []
    real = prepare_mod._checked_bundle

    def counting(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)
    monkeypatch.setattr(prepare_mod, '_checked_bundle', counting)
    prepare_mod._verified.clear()
    yield calls
    prepare_mod._verified.clear()


def test_repeated_state_reads_do_not_recheck_an_unchanged_packet(packet, counted):
    root, _ = packet
    with ReviewSession(root, 'Synthetic researcher') as review:
        before = len(counted)
        for _ in range(3):
            review.state()
        assert len(counted) == before


def test_a_changed_artifact_is_checked_again_and_refused(packet, counted):
    root, value = packet
    with ReviewSession(root, 'Synthetic researcher') as review:
        review.state()
        name = next(iter(value['artifacts']))
        path = root / name
        path.write_bytes(path.read_bytes() + b' ')
        with pytest.raises(ValueError, match='digest mismatch'):
            review.state()


def test_saving_a_decision_keeps_the_full_check(packet, counted):
    root, value = packet
    with ReviewSession(root, 'Synthetic researcher') as review:
        review.state()
        before = len(counted)
        review.save(answer(value))
        assert len(counted) > before


def test_cached_reads_return_an_independent_copy(packet, counted):
    root, _ = packet
    first = prepare_mod.load_packet(root, reuse_checked=True)
    first['items'].clear()
    assert prepare_mod.load_packet(root, reuse_checked=True)['items']
