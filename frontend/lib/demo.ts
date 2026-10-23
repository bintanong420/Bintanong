export const demoAnswer = {
  text: "This is a fictional example response, included to preview how a Bintanong conversation will look.\n\nAn academic answer will appear here with its supporting sources once the public service is connected. This preview has not checked a PalSU policy, curriculum or prerequisite.\n\nAny files you select stay on this page as filename chips. Their contents are not opened, uploaded or analyzed.",
  sources: ["Sample curriculum", "Sample student handbook"],
};

export function prepareDemo(signal: AbortSignal): Promise<typeof demoAnswer> {
  // A short, explicitly simulated pause makes the approved status presentation inspectable.
  return new Promise((resolve, reject) => {
    if (signal.aborted) return reject(new DOMException("Preview reset", "AbortError"));
    const timer = setTimeout(() => { signal.removeEventListener("abort", cancel); resolve(demoAnswer); }, 650);
    function cancel() { clearTimeout(timer); reject(new DOMException("Preview reset", "AbortError")); }
    signal.addEventListener("abort", cancel, { once: true });
  });
}
