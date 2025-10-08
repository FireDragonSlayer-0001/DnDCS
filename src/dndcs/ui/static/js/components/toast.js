import { $ } from "../util/dom.js";

let dialog = null;

export function init(selector = "#toast") {
  dialog = $(selector);
  if (!dialog) {
    console.warn("Toast element not found", { selector });
  }
}

export function render() {
  // no-op placeholder to align with component contract
}

export function toast(message, duration = 1800) {
  if (!dialog) {
    console.warn("Toast element not initialised", { message });
    return;
  }
  dialog.textContent = message;
  dialog.show();
  setTimeout(() => dialog.close(), duration);
}
