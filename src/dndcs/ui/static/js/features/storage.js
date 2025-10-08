import { apiNewCharacter, apiValidate } from "../services/api.js";
import { slug } from "../util/slug.js";

export async function newCharacter(moduleId, name = "New Hero") {
  if (!moduleId) throw new Error("Module ID required");
  return apiNewCharacter(moduleId, name);
}

export async function openFile(file) {
  if (!file) throw new Error("File required");
  const text = await file.text();
  return JSON.parse(text);
}

export function saveCharacter(character) {
  if (!character) throw new Error("Character data required");
  const filename = `${slug(character.name || "character")}.json`;
  const blob = new Blob([JSON.stringify(character, null, 2)], { type: "application/json" });
  const anchor = document.createElement("a");
  anchor.href = URL.createObjectURL(blob);
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(anchor.href);
  return filename;
}

export async function validateCharacter(character) {
  if (!character) throw new Error("Character data required");
  const result = await apiValidate(character);
  return result.issues || [];
}
