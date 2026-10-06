"""Mechanical checks of the review page's static files (D7, D8 and the accessibility basics)."""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

STATIC = Path(__file__).resolve().parent.parent / "backend" / "bintanong_tools" / "prospectus_review_gui" / "static"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
FOCUSABLE = {"a", "button", "input", "select", "textarea"}
CONTROLS = {"input", "select", "textarea"}


class Page(HTMLParser):
    """Element list with attributes, text content and ancestry."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        element = {"tag": tag, "attrs": dict(attrs), "text": "", "parents": [e["tag"] for e in self.stack],
                   "ancestors": list(self.stack)}
        self.elements.append(element)
        if tag not in ("meta", "link", "input", "img", "br", "hr"):
            self.stack.append(element)

    def handle_endtag(self, tag):
        while self.stack:
            if self.stack.pop()["tag"] == tag:
                break

    def handle_data(self, data):
        for element in self.stack:
            element["text"] += data

    def find(self, tag=None, **attrs):
        return [e for e in self.elements if (tag is None or e["tag"] == tag)
                and all(e["attrs"].get(k.replace("_", "-")) == v for k, v in attrs.items())]


@pytest.fixture(scope="module")
def page():
    parser = Page()
    parser.feed((STATIC / "index.html").read_text(encoding="utf-8"))
    parser.close()
    return parser


def css():
    return (STATIC / "review.css").read_text(encoding="utf-8")


def js():
    return (STATIC / "review.js").read_text(encoding="utf-8")


def test_static_folder_has_the_three_files():
    assert sorted(p.name for p in STATIC.iterdir()) == ["index.html", "review.css", "review.js"]


def test_no_external_url_in_any_static_asset():
    for path in STATIC.iterdir():
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"https?://[^\s\"'<>)]*", text):
            assert match.group(0) == SVG_NAMESPACE, (path.name, match.group(0))
        assert "//cdn" not in text and "@import" not in text and "url(" not in text.replace("url(data:", ""), path.name


def test_page_has_no_inline_script_style_or_event_handler_attribute(page):
    assert page.find("style") == []
    for script in page.find("script"):
        assert script["attrs"].get("src", "").startswith("/static/") and script["text"].strip() == ""
    for element in page.elements:
        for name in element["attrs"]:
            assert not name.startswith("on"), (element["tag"], name)
            assert name != "style", element["tag"]
    for link in page.find("link"):
        assert link["attrs"]["href"].startswith("/static/")


def test_js_never_builds_inline_handlers_or_evaluates_text():
    source = js()
    for bad in ("eval(", "new Function", "setAttribute(\"on", "setAttribute('on", ".onclick", "document.write", "insertAdjacentHTML"):
        assert bad not in source, bad
    # innerHTML is used once, for the server-rendered twin (escaped by the renderer); nothing else is injected as HTML
    assert source.count(".innerHTML") == 1 and "twinBox.innerHTML = twin.html" in source


def test_page_landmarks_and_headings(page):
    assert len(page.find("h1")) == 1
    for tag in ("main", "nav", "header", "footer"):
        assert len(page.find(tag)) == 1, tag
    focusable = [e for e in page.elements if (e["tag"] in FOCUSABLE and (e["tag"] != "a" or "href" in e["attrs"]))
                 or "tabindex" in e["attrs"] and e["attrs"]["tabindex"] != "-1"]
    first = focusable[0]
    assert first["tag"] == "a" and first["attrs"]["href"].startswith("#") and "skip" in first["text"].lower()
    target = first["attrs"]["href"][1:]
    assert page.find(id=target), target
    assert page.find("nav")[0]["attrs"].get("aria-label")


def accessible_name(page, element):
    attrs = element["attrs"]
    if attrs.get("aria-label", "").strip() or attrs.get("aria-labelledby"):
        return True
    if element["tag"] == "button":
        return bool(element["text"].strip())
    if "label" in element["parents"]:
        label = next(a for a in reversed(element["ancestors"]) if a["tag"] == "label")
        return bool(label["text"].strip())
    return bool(attrs.get("id")) and any(l["attrs"].get("for") == attrs["id"] and l["text"].strip() for l in page.find("label"))


def test_every_form_control_has_an_accessible_name(page):
    controls = [e for e in page.elements if e["tag"] in CONTROLS | {"button"} and e["attrs"].get("type") != "hidden"]
    assert len(controls) >= 8
    for element in controls:
        assert accessible_name(page, element), (element["tag"], element["attrs"])
    radios = page.find("input", type="radio")
    assert {r["attrs"]["value"] for r in radios} == {"yes", "no", "other"}
    for radio in radios:
        assert "fieldset" in radio["parents"] and radio["attrs"]["name"] == "choice"
    fieldset = next(a for a in radios[0]["ancestors"] if a["tag"] == "fieldset")
    legends = [e for e in page.elements if e["tag"] == "legend" and fieldset in e["ancestors"]]
    assert legends and legends[0]["text"].strip()


def test_live_region_exists_for_status_and_errors(page):
    assert page.find(aria_live="polite")
    alert = page.find(role="alert")
    assert alert and alert[0]["attrs"].get("id")
    describes = [e for e in page.elements if alert[0]["attrs"]["id"] in e["attrs"].get("aria-describedby", "").split()]
    assert describes   # the reason field points at the error message
    assert "aria-invalid" in js()


def test_images_and_overlays_have_text_alternatives(page):
    image = page.find("img", id="page-image")
    assert image and "alt" in image[0]["attrs"]
    assert re.search(r"\.alt\s*=\s*`Page \$\{", js())   # the script names the page and the asked field
    assert page.find(id="overlays", aria_hidden="true")


def rules(text):
    return re.findall(r"([^{}]+)\{([^{}]*)\}", text)


def test_css_defines_visible_focus_and_respects_reduced_motion():
    text = css()
    focus = [body for selector, body in rules(text) if ":focus-visible" in selector]
    assert focus
    widths = [float(w) for body in focus for w in re.findall(r"outline:\s*([0-9.]+)px", body)]
    assert widths and min(widths) >= 2
    assert "@media (prefers-reduced-motion: reduce)" in text
    assert not re.search(r"outline:\s*(none|0)\b", text)


def tokens(block):
    return {name: value for name, value in re.findall(r"(--[a-z-]+):\s*(#[0-9a-fA-F]{6})", block)}


def luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


TEXT_PAIRS = [("--fg", "--bg"), ("--muted", "--bg"), ("--fg", "--panel"), ("--muted", "--panel"), ("--link", "--bg"),
              ("--on-accent", "--accent"), ("--error", "--bg"), ("--warn-fg", "--warn-bg"), ("--ok-fg", "--ok-bg"),
              ("--broken-fg", "--broken-bg"), ("--fg", "--highlight")]


def test_css_colours_meet_contrast():
    text = css()
    light = tokens(re.search(r":root\s*\{([^}]*)\}", text).group(1))
    dark_block = re.search(r"@media \(prefers-color-scheme: dark\)\s*\{\s*:root\s*\{([^}]*)\}", text)
    assert dark_block, "a dark scheme is declared"
    dark = {**light, **tokens(dark_block.group(1))}
    for scheme, palette in (("light", light), ("dark", dark)):
        for fg, bg in TEXT_PAIRS:
            assert fg in palette and bg in palette, (scheme, fg, bg)
            assert contrast(palette[fg], palette[bg]) >= 4.5, (scheme, fg, bg, round(contrast(palette[fg], palette[bg]), 2))
    assert round(contrast("#000000", "#ffffff"), 1) == 21.0


def test_key_help_lists_every_bound_key(page):
    source = js()
    keymap = re.search(r"const KEYS = \{(.*?)\n\};", source, re.S).group(1)
    bound = set(re.findall(r'^\s*"([^"]+)":', keymap, re.M))
    if re.search(r'const PROPOSAL_KEYS = "123456789"', source):
        bound.add("1-9")
    help_box = page.find(id="key-help")[0]
    helped = {e["text"].strip() for e in page.elements if e["tag"] == "kbd" and help_box in e["ancestors"]}
    assert bound and bound == helped


def test_static_route_refuses_path_traversal(tmp_path):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from backend.bintanong_tools.prospectus_review_gui.app import create_app, new_token
    from backend.bintanong_tools.prospectus_review_gui.session import open_session

    import review_gui_fixtures as rf

    ws = rf.workspace(tmp_path)
    with open_session(ws.candidate, ws.identity, "Nestor", ws.review) as session:
        client = TestClient(create_app(session, new_token(), port=8765), base_url="http://127.0.0.1:8765")
        assert client.get("/static/review.js").status_code == 200
        for bad in ("/static/..%2fsession.py", "/static/..%2f..%2fsession.py", "/static/%2e%2e%2fapp.py", "/static/index.html"):
            assert client.get(bad).status_code == 404, bad
