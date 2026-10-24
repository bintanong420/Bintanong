"""Bintanong takes English, Filipino and Taglish only (owner, 25 Oct 2026).

The router labels Cebuano as Filipino, so a Cebuano question is recognised here from words Tagalog does not use.
Two different markers are required, so a single word such as an exclaimed "nako" never turns away a Taglish question.
"""
import re

_CEBUANO = re.compile(r"\b(unsaon|unsa|pila ka|maayong (?:buntag|hapon|gabii|udto)|kanus-a|ngano|dili|nimo|nako|"
                      r"karon|kini|kana|mahimo|diin|adtong|ug)\b", re.I)


def unsupported_language(text: str) -> bool:
    return len({m.group(1).casefold() for m in _CEBUANO.finditer(text)}) >= 2
