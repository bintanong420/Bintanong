"""The review page's key map, driven under node (the page itself needs a browser). Skipped when node is missing."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

KEYS_JS = Path(__file__).resolve().parent.parent / "backend" / "bintanong_tools" / "prospectus_review_gui" / "static" / "keys.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed; check the keys by hand in a browser")

RADIO = {"tag": "input", "type": "radio"}
TEXT = {"tag": "input", "type": "text"}
BODY = {"tag": "body", "type": ""}
BUTTON = {"tag": "button", "type": "submit"}

CASES = [
    # (key, focused element, modifier, expected action)
    ("ArrowDown", RADIO, False, None),      # C4: the arrow keys belong to the focused radio
    ("ArrowUp", RADIO, False, None),
    ("ArrowLeft", RADIO, False, None),
    ("ArrowDown", {"tag": "select", "type": ""}, False, None),
    ("ArrowDown", BODY, False, "next"),
    ("ArrowUp", BODY, False, "previous"),
    ("ArrowDown", BUTTON, False, "next"),
    ("j", RADIO, False, "next"),            # letters still work with a radio focused
    ("y", BODY, False, "yes"),
    ("3", BODY, False, "proposal:2"),
    ("y", TEXT, False, None),               # S4: typing in a field never triggers a shortcut
    ("n", {"tag": "textarea", "type": ""}, False, None),
    ("j", {"tag": "select", "type": ""}, False, None),
    ("1", TEXT, False, None),
    ("/", TEXT, False, None),
    ("Escape", TEXT, False, "close-other"),  # except Escape, which leaves the Other fields
    ("Escape", {"tag": "textarea", "type": ""}, False, "close-other"),
    ("Enter", BUTTON, False, None),         # the focused button acts
    ("Enter", BODY, False, "submit"),
    ("y", BODY, True, None),                # a browser shortcut is left alone
    ("q", BODY, False, None),
]


def test_key_actions_for_every_focus_case():
    script = ("const {keyAction} = require(process.argv[1]); const cases = JSON.parse(process.argv[2]);"
              "console.log(JSON.stringify(cases.map(c => keyAction({key: c[0], tag: c[1].tag, type: c[1].type, ctrl: c[2]}))));")
    done = subprocess.run([NODE, "-e", script, str(KEYS_JS), json.dumps(CASES)], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    got = json.loads(done.stdout)
    wrong = [(c[:3], g, c[3]) for c, g in zip(CASES, got) if g != c[3]]
    assert not wrong, wrong
