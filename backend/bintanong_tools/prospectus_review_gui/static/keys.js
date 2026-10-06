"use strict";
// Which action a key press means. Pure (no DOM access) so tests/test_review_gui_keys.py can drive it under node.
// `press` is {key, ctrl, tag, type}: the key, whether a modifier is down, and the focused element's tag and input type.

const KEY_ACTIONS = {
  "y": "yes",
  "n": "no",
  "o": "other",
  "Enter": "submit",
  "Escape": "close-other",
  "j": "next",
  "k": "previous",
  "ArrowDown": "next",
  "ArrowUp": "previous",
  "z": "zoom",
  "p": "mode",
  "/": "filter",
  "?": "help",
};
const ARROWS = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"];

function keyAction(press) {
  if (press.ctrl) return null;
  const tag = press.tag, type = press.type || "";
  const typing = tag === "textarea" || tag === "select" || (tag === "input" && type !== "radio" && type !== "checkbox");
  if (typing && press.key !== "Escape") return null;
  // An arrow on a focused radio, checkbox or select belongs to that control, not to the question list.
  if (ARROWS.includes(press.key) && (tag === "input" || tag === "select" || tag === "textarea")) return null;
  if (press.key === "Enter" && (tag === "button" || tag === "a" || tag === "summary")) return null;   // the focused control acts
  if (press.key.length === 1 && "123456789".includes(press.key)) return `proposal:${Number(press.key) - 1}`;
  return KEY_ACTIONS[press.key] || null;
}

if (typeof module !== "undefined") module.exports = { keyAction };
