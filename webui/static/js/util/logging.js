export async function logError(err, context = "") {
  const message = err?.message || String(err);
  const payload = {
    level: "error",
    message: context ? `${context}: ${message}` : message,
    stack: err?.stack,
  };
  try {
    await fetch("/api/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (_) {
    // Swallow logging errors to avoid recursive failures in the UI.
  }
}
