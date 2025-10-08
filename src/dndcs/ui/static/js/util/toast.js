const SELECTOR = "#toast";

export function toast(message, duration = 1800) {
  const dialog = document.querySelector(SELECTOR);
  if (!dialog) {
    console.warn("Toast element not found", { selector: SELECTOR, message });
    return;
  }
  dialog.textContent = message;
  dialog.show();
  setTimeout(() => dialog.close(), duration);
}
