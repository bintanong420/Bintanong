// Lifecycle tests explicitly skip optional onboarding; scope-onboarding.mjs tests the prompt itself.
export async function dismissInitialScope(page) {
  const dialog = page.getByRole('dialog', { name: 'Program and curriculum', exact: true });
  if (await dialog.isVisible()) await dialog.getByRole('button', { name: 'Skip for now', exact: true }).click();
}
