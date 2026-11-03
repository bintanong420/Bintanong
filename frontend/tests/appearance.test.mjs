import assert from "node:assert/strict";
import { test } from "node:test";
import { runInNewContext } from "node:vm";
import { appearanceValue, appearanceBootstrap } from "../lib/appearance.ts";

test("appearance accepts light, dark and system and defaults to light", () => {
  for (const value of ["light", "dark", "system"]) assert.equal(appearanceValue(value), value);
  for (const value of [null, undefined, "", "auto", "LIGHT", "<script>bad()</script>"]) assert.equal(appearanceValue(value), "light");
});

test("bootstrap restores an allowed preference before hydration", () => {
  for (const value of ["light", "dark", "system", null, "invalid"]) {
    const document = { documentElement: { dataset: {} } };
    runInNewContext(appearanceBootstrap, { document, localStorage: { getItem: () => value } });
    assert.equal(document.documentElement.dataset.appearance, appearanceValue(value));
  }
});

test("storage denial falls back to light rather than breaking rendering", () => {
  const document = { documentElement: { dataset: {} } };
  runInNewContext(appearanceBootstrap, { document, localStorage: { getItem() { throw Error("Storage denied"); } } });
  assert.equal(document.documentElement.dataset.appearance, "light");
});
