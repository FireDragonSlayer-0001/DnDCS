import { getCurrent } from "../state/store.js";
import { $ } from "../util/dom.js";

let output = null;

export function init() {
  output = $("#rawOut");
  render();
}

export function render() {
  if (!output) return;
  const current = getCurrent();
  output.textContent = current ? JSON.stringify(current, null, 2) : "(no character loaded)";
}
