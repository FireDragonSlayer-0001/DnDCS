import { logError } from "../util/logging.js";

async function requestJSON(url, options = {}, context = "api request") {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    await logError(error, context);
    throw error;
  }
}

export function apiModules() {
  return requestJSON("/api/modules", undefined, "modules");
}

export function apiNewCharacter(moduleId, name = "New Hero") {
  return requestJSON(
    "/api/new_character",
    {
      method: "POST",
      body: JSON.stringify({ module_id: moduleId, name }),
    },
    "new character"
  );
}

export function apiDerive(character) {
  return requestJSON(
    "/api/derive",
    {
      method: "POST",
      body: JSON.stringify(character),
    },
    "derive"
  );
}

export function apiValidate(character) {
  return requestJSON(
    "/api/validate",
    {
      method: "POST",
      body: JSON.stringify(character),
    },
    "validate"
  );
}

export function apiSpells(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, value);
    }
  });

  return requestJSON(`/api/spells?${query.toString()}`, undefined, "spells");
}
