"""Owner-approved everyday Filipino wording for host-rendered text (21 October 2026)."""
import pytest

from backend.bintanong_generation import render

DEEP = ('natugunan', 'nakasaad', 'kwalipikado', 'nakabalangkas', 'mapatunayan', 'matiyak', 'pagsusuri')


def filipino_texts():
    yield from render._WORDS['fil'].values()
    yield render._WITHHELD['fil']
    yield render._UNCOVERED['fil']


@pytest.mark.parametrize('word', DEEP)
def test_filipino_host_text_avoids_deep_tagalog(word):
    assert not any(word in text.lower() for text in filipino_texts())


def test_approved_filipino_decision_lines():
    words = render._WORDS['fil']
    assert words['eligible'] == 'Ayon sa prerequisite check: kumpleto ang mga kondisyon.'
    assert words['ineligible'] == 'Ayon sa prerequisite check: may kondisyon na kulang pa.'
    assert words['unknown'] == ('Hindi pa masabi kung pwede ka, dahil kulang ang impormasyon '
                                'o hindi ito sakop ng rules.')
    assert words['abstained'] == 'Hindi makumpirma ang sagot mula sa ibinigay na ebidensya.'
    assert render._WITHHELD['fil'] == ('Hindi pa masagot nang sigurado gamit lang ang nakuhang text. '
        'Wala pang verified na prerequisite check, kaya wala pang desisyon.')
    assert render._UNCOVERED['fil'] == 'Hindi makumpirma na nasasagot ng available na ebidensya ang tanong mo.'


def test_filipino_scope_label_uses_everyday_wording():
    import inspect
    source = inspect.getsource(render)
    assert "'fil':'Sakop ng check'" in source and 'Saklaw ng pagsusuri' not in source


def test_approved_filipino_check_status_lines():
    words = render._WORDS['fil']
    assert words['unsupported'] == 'Hindi supported ang check na ito.'
    assert words['error'] == 'Hindi natapos ang check.'
    assert words['temporarily_unavailable'] == 'Hindi muna magawa ang check ngayon. Subukan ulit mamaya.'
