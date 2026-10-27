"""Owner-approved output policy; input-language recognition remains separate."""

REPLY_POLICY_VERSION = 'english-taglish-20261027-v1'


def reply_language(language):
    """Legacy Filipino reply requests use Taglish;unknown is never guessed."""
    return 'taglish' if language == 'fil' else language
