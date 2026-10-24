import assert from "node:assert/strict";
import { test } from "node:test";
import { runInNewContext } from "node:vm";
import { appearanceValue, appearanceBootstrap } from "../lib/appearance.ts";

test("appearance accepts only light, dark and system", () => {
  for (const value of ["light", "dark", "system"]) assert.equal(appearanceValue(value), value);
  for (const value of [null, undefined, "", "auto", "LIGHT", "<script>bad()</script>"]) assert.equal(appearanceValue(value), "system");
});

test("bootstrap restores an allowed preference before hydration", () => {
  for (const value of ["light", "dark", "system", null, "invalid"]) {
    const document = { documentElement: { dataset: {} } };
    runInNewContext(appearanceBootstrap, { document, localStorage: { getItem: () => value } });
    assert.equal(document.documentElement.dataset.appearance, appearanceValue(value));
  }
});

test("storage denial falls back to system rather than breaking rendering", () => {
  const document = { documentElement: { dataset: {} } };
  runInNewContext(appearanceBootstrap, { document, localStorage: { getItem() { throw Error("Storage denied"); } } });
  assert.equal(document.documentElement.dataset.appearance, "system");
});
