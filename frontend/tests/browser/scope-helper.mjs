// Chat is locked until a program is chosen (owner decision, 3 Nov 2026). Lifecycle tests pick the
// first listed program; scope-onboarding.mjs tests the picker and the lock themselves.
export async function dismissInitialScope(page) {
  const dialog = page.getByRole('dialog', { name: 'Choose your program', exact: true });
  await dialog.waitFor();
  await dialog.locator('.program-option').first().click();
  const year = page.getByRole('dialog', { name: 'When did you start?', exact: true });
  if (await year.isVisible()) {
    await year.getByRole('radio', { name: 'S.Y. 2025–2026', exact: true }).check();
    await year.getByRole('button', { name: 'Use this program', exact: true }).click();
  }
  await page.getByRole('textbox', { name: 'Your question', exact: true }).waitFor({ state: 'visible' });
}
