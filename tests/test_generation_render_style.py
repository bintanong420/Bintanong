"""Owner-approved everyday Filipino wording for host-rendered text (21 October 2026)."""
import pytest

from backend.bintanong_generation import render


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_incomplete_retrieval_does_not_claim_the_policy_is_absent_from_reviewed_sources(language):
    from dataclasses import replace
    from backend.bintanong_generation.evidence import prepare
    from test_generation_evidence import integrated
    pack = replace(prepare(integrated('RAG', response_style=language)),
                   status='no_evidence', reason='retrieval_coverage')
    text = render.render_text(pack, (), 'insufficient_evidence')
    assert "not in Bintanong's reviewed sources" not in text
    assert 'Wala pa ito' not in text
    assert ('complete answer' if language == 'en' else 'kumpletong sagot') in text

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
    # Owner E1 (24 Oct) and simple-question priority (25 Oct): evidence that does not answer the question gets the
    # same honest referral as missing evidence, in every language.
    assert render._UNCOVERED == {lang: render._WORDS[lang]['insufficient_evidence'] for lang in ('en', 'fil', 'taglish')}


def test_filipino_scope_label_uses_everyday_wording():
    import inspect
    source = inspect.getsource(render)
    assert "'fil':'Sakop ng check'" in source and 'Saklaw ng pagsusuri' not in source


def test_approved_filipino_check_status_lines():
    words = render._WORDS['fil']
    assert words['unsupported'] == 'Hindi supported ang check na ito.'
    assert words['error'] == 'Hindi natapos ang check.'
    assert words['temporarily_unavailable'] == 'Hindi muna magawa ang check ngayon. Subukan ulit mamaya.'
