# AGENTS.md

> Guidance for autonomous contributors (AI agents and humans) working on **DnDCS** — a modular, web‑based character‑sheet manager. Read this first to understand **purpose**, **style**, **architecture**, and **safe extension points**.

---

## 1) Product purpose (short)

**DnDCS** is a universal, modular **Character Sheet Manager** for tabletop RPGs. Out‑of‑the‑box it ships with support for **D&D 5e** (SRD‑compatible), but the system is designed so that **any ruleset** (characters, abilities, skills, spells, companions, items, dice, rests, conditions, attacks, saving throws, etc.) can be added as a **feature‑module** without modifying the core.

**Key expectations:**

* Users can **create, load, edit and save** characters.
* Users can **roll** (ability checks, saving throws, attacks, damage, custom dice) with rules‑aware calculations.
* Users can manage **spells, companions, inventory, features/feats, proficiencies, conditions, resources** and rests.
* A **Web UI** renders the sheet, rolls console, rules reference, and settings. **Add‑ons** may extend both **logic** and **UI** safely.

---

## 2) Operating principles (style the agent should follow)

* **Feature‑first structure:** group code by **feature/domain** (e.g., `characters/`, `spells/`, `rolls/`) rather than by technical layer (no global `components/` dump).
* **Strict modularity:** core exposes a **stable Engine API**; everything else is an **add‑on**. Never couple add‑ons directly to each other.
* **Schema‑driven UI:** render screens from **schemas** and declarative **layout descriptors**, enabling add‑ons to patch or inject panels/routes without forking core UI code.
* **Safety by default:** treat third‑party content as **untrusted**. No dynamic code execution unless explicitly permitted; use **YAML safe_load**; validate manifests.
* **Reproducibility:** typed models, deterministic calculations, tests as specification. Prefer **Pydantic v2** models for all public data contracts.
* **Web‑first:** API via **FastAPI**; serve a SPA or templated pages; run under **Uvicorn** in dev.
* **Portability:** file‑based data by default; optional **SQLite** (via SQLModel/SQLAlchemy) for persistence.
* **Concision & EU English:** prefer concise, clear prose; use EU/British spelling.

---

## 3) Repository layout & conventions

```
/ main/                     # launch entry points (e.g., .bat, shell scripts), minimal config
/ main-Core/                # the core engine and default features
  ├─ api/                   # FastAPI app, routers, dependency wiring
  ├─ domain/                # Pydantic models (Character, Ability, Skill, Spell, Attack, Save, Item, Feature, Companion, Resource, Condition, etc.)
  ├─ rules/                 # rules engines (e.g., dnd5e baseline), calculators, dice expressions
  ├─ services/              # RulesService, DiceService, StorageService, CalcService, UI Schema Service
  ├─ storage/               # file/SQLite adapters, import/export, migrations
  ├─ ui_schema/             # JSON/YAML schemas for layouts, panels, forms, tables, actions
  ├─ rulesets/              # packaged rulesets (e.g., dnd5e/) with SRD‑compatible data
  ├─ docs/                  # end‑user and developer docs
  └─ tests/                 # unit + contract tests (pytest)
/ main-Addons/              # user add‑ons (each folder is one module)
  └─ <addon-name>/
      ├─ Masterfile.(yaml|json)   # manifest (see §5)
      ├─ data/                    # resources (spells, items, etc.)
      ├─ logic/                   # optional Python logic (safe, permissioned)
      ├─ ui/                      # UI layout patches, routes, panels, assets
      └─ tests/                   # add‑on tests
/ webui/                   # (optional) SPA sources if split; otherwise core serves templates/assets
/ tooling/                 # linters, configs, CI workflows, scripts
```

**Feature grouping examples** inside `main-Core/` and add‑ons:

* `characters/`, `sheets/`, `rolls/`, `spells/`, `inventory/`, `companions/`, `conditions/`, `proficiencies/`, `rulesets/`, `import_export/`, `settings/`.

**Coding standards**

* Python **3.11+**, **Pydantic v2**, **Click** (CLI), **PyYAML** (safe load only), optional **SQLModel**.
* Lint/format/type: **ruff**, **black**, **mypy**.
* Commits: **Conventional Commits** (`feat:`, `fix:`, `docs:`...).
* Tests: **pytest**; property‑based tests where valuable.

---

## 4) Engine API (contract for core and add‑ons)

The Engine API is the only stable surface add‑ons may depend on. Version with **semver** and publish a compatibility range in add‑on manifests.

### 4.1 Core data models (Pydantic v2)

* `Character` (id, name, ancestry, class, level, abilities, skills, proficiencies, inventory, features, spells, companions, conditions, resources, notes)
* `AbilityScore` (score, modifier, save proficiency)
* `Skill` (ability, proficient, expertise, misc bonuses)
* `Spell` (level, school, casting time, components, range, duration, scaling, prepared, uses)
* `Attack` (to‑hit calc, damage roll expression, properties, ammo/uses)
* `Save` (DC calc, advantage/disadvantage hooks)
* `Item`, `Feature`, `Companion`, `Condition`, `Resource` (uses/rest, recharge)
* `RollResult` (expression, parts, totals, advantage/disadvantage, critical flags)

> Agents: extend models only via **add‑on schemas** or clearly versioned core updates.

### 4.2 Core services

* **RulesService** — ruleset selection, proficiency & DC maths, advantage logic.
* **DiceService** — parse/evaluate dice expressions with deterministic seeds for tests.
* **CalcService** — aggregates modifiers from character state + rules to produce derived values (AC, initiative, passive scores, etc.).
* **StorageService** — file & SQLite backends (import/export), migrations.
* **UISchemaService** — composes base layouts with add‑on UI patches.

### 4.3 Events & hooks (examples)

* `on_character_loaded`, `before_roll`, `after_roll`, `on_resource_spent`, `on_turn_start`, `on_turn_end`.
* Add‑ons may subscribe via declarative hooks in `Masterfile` or light code entry points.

---

## 5) Add‑on manifest: **Masterfile** spec

Each add‑on lives under `main-Addons/<addon-name>/` and must include a `Masterfile.yaml` (or `.json`) at its root.

### 5.1 Schema (conceptual)

```yaml
module_id: "my-addon"              # required, kebab-case unique id
version: "1.0.0"                   # semver
engine_api_version: ">=1.0,<2.0"   # required compatibility range
display_name: "My Add‑on"
author: "Name or org"
license: "MIT"                     # SPDX id; ensure data licensing is compatible
summary: "Adds new spells and a spellbook panel."
description: |
  Longer, multi‑line description.

permissions:                       # hardened by default; opt‑in only
  filesystem: read                 # none|read|readwrite (scoped to addon dir)
  network: none                    # none|outbound (discouraged in core distribution)
  eval: false                      # disallow dynamic code execution by default

entry_points:                      # optional backend logic hooks
  python:
    - "my_addon.logic:register"   # dotted path; receives (EngineContext)

resources:                         # structured data files bundled with addon
  - path: data/spells.yaml
    kind: spell
  - path: data/items.json
    kind: item

ui_patches:                        # declarative UI additions/modifications
  - target: route                  # route|panel|component
    selector: "/spells"           # route id or path
    action: add                    # add|before|after|replace|remove
    payload: ui/spellbook.panel.yaml  # layout fragment or JSON Patch file
  - target: nav
    selector: "left"
    action: add
    payload: ui/nav/spellbook.link.yaml

routes:                            # optional API surface contributed by addon
  - openapi: ui/routes.openapi.yaml

config_schema: ui/config.schema.yaml  # optional user‑config schema (forms)

depends_on:                        # other addons (by module_id) and versions
  - module_id: "my-shared"
    version: ">=0.3,<1.0"

tests:                             # smoke/contract tests for the addon
  - path: tests/test_smoke.py

migrations:                        # optional data migrations
  - from: "0.9.x"
    to:   "1.0.0"
    path: migrations/0_9_to_1_0.py
```

### 5.2 Validation & install rules

* Core validates `Masterfile` against a JSON Schema; incompatible or unsafe permissions cause **install refusal** with a clear message.
* Add‑ons may only access their own folder unless explicitly granted.
* Network access is **off** by default and discouraged.
* Engine API hooks run in a constrained context; long‑running tasks must not block the UI thread.

---

## 6) Web UI contract

* The UI is assembled from **base layouts** (`main-Core/ui_schema/`) plus **add‑on patches**.
* **Key regions**: Navigation, Character Sheet, Rolls Console, Rules Reference, Settings.
* **Routes** should be stable IDs (e.g., `/sheet`, `/rolls`, `/spells`). Add‑ons inject **panels** or **routes** using `ui_patches`.
* **Accessibility**: keyboard navigation, ARIA labels, colour‑contrast compliant. Don’t ship unreadable themes.
* **Internationalisation**: string keys in schemas, translations in add‑ons under `ui/i18n/`.

---

## 7) Storage & data

* Default: **file‑based** character profiles (`.json`/`.yaml`) under a user folder.
* Optional: **SQLite** for multi‑profile libraries and search.
* Import/Export: deterministic serialisation; include ruleset & addon provenance to ensure portability.
* Never embed proprietary rules text unless licensing permits; prefer SRD‑compatible or user‑supplied data.

---

## 8) Security & privacy

* Offline‑first, no telemetry by default. If analytics become optional, ask explicit consent.
* Guard against malicious manifests; validate schemas; never `exec()` untrusted content.
* Honour EU privacy norms (e.g., easy data export/delete for user profiles).

---

## 9) Developer workflow (agents & humans)

**Run (dev):**

* Backend: `uvicorn main-Core.api.app:app --reload` (or launch via `/main/*.bat`).
* Frontend: if present in `/webui`, run the SPA dev server and proxy to the API.

**Quality gates:**

* `ruff`, `black`, `mypy` must pass.
* `pytest` unit + contract tests must pass.
* New or changed Engine API requires version bump and changelog entry.

**Conventional Commits examples:**

* `feat(rolls): add advantage/disadvantage parser`
* `fix(dnd5e): correct proficiency bonus at level 17`
* `docs(addons): clarify Masterfile permissions`

---

## 10) Backlog for autonomous agents (prioritised)

1. **Define Engine API v1.0** (models, services, events) and publish JSON Schemas.
2. **Implement DiceService** with parser, evaluator, deterministic seeds, tests.
3. **Implement RulesService (dnd5e base)**: proficiency, ability mods, saves, attacks, spell DCs.
4. **Character CRUD**: load/save JSON, migration stub, profile folder structure.
5. **UI baseline**: navigation, sheet view, rolls console, settings; wire to schemas.
6. **Masterfile validator** and installer with permission checks.
7. **Example add‑on**: adds a new panel + a few SRD‑compatible spells and items.
8. **Contract tests** for add‑on compatibility (engine_api_version range).
9. **StorageService adapters**: file + optional SQLite (SQLModel) with tests.
10. **Import/Export**: portable bundles with provenance.
11. **Ruleset packaging** conventions under `main-Core/rulesets/`.
12. **CI pipeline**: lint, type‑check, tests; produce dev artefacts.
13. **Docs**: end‑user quickstart, add‑on authoring guide, UI schema reference.

**Definition of Done (per change):**

* Tests added/updated; docs updated; schemas versioned; no linter/type errors; no breaking changes without semver bump.

---

## 11) Don’ts (hard guardrails)

* ❌ Do not collapse the **feature‑first** layout into layer‑based folders.
* ❌ Do not hardcode UI; always go through **UI schemas** or `ui_patches`.
* ❌ Do not import from another add‑on directly; communicate via Engine API events/contracts.
* ❌ Do not enable network/file write permissions by default in add‑ons.
* ❌ Do not ship copyrighted rules text or assets without a compatible licence.

---

## 12) Glossary

* **Engine API** — stable contracts for models/services/events exposed by core.
* **Masterfile** — add‑on manifest describing compatibility, permissions, resources, UI patches, and optional logic.
* **UI Schema** — declarative layout/flow definitions used to render the Web UI.
* **SRD** — System Reference Document (e.g., D&D 5e SRD‑compatible content).

---

### Appendix A — Minimal `Masterfile.yaml` example

```yaml
module_id: "spellbook-basic"
display_name: "Spellbook (Basic)"
version: "1.0.0"
engine_api_version: ">=1.0,<2.0"
summary: "Adds a simple spellbook panel and SRD‑compatible cantrips."
permissions:
  filesystem: read
  network: none
  eval: false
resources:
  - path: data/spells.cantrips.yaml
    kind: spell
ui_patches:
  - target: route
    selector: "/spells"
    action: add
    payload: ui/panels/spellbook.panel.yaml
```

### Appendix B — UI panel fragment (example)

```yaml
id: "panel.spellbook"
title: "Spellbook"
layout:
  kind: table
  source: spell.list          # data source identifier
  columns:
    - key: name
      title: Name
    - key: level
      title: Level
    - key: school
      title: School
actions:
  - id: spell.prepare
    title: Toggle Prepared
    kind: toggle
    target: selection
```

---

## 13) FAQ — sanity checks

**Q: Is the proposed folder structure a hard requirement?**
**A:** No. Treat it as a **recommended stencil** for clarity and tooling defaults. The only expectations are:

* `main-Core/` contains the engine/API so add‑ons can resolve imports.
* `main-Addons/` is the default scan root for add‑ons.
  Everything else (exact subfolders, names) can vary if the **Engine API** contracts and the **Masterfile** paths are respected.

**Q: Can add‑ons introduce new stats beyond STR/DEX/CON/INT/WIS/CHA?**
**A:** Yes. Add‑ons may define **new abilities/attributes** via schema and/or logic hooks, and register how they participate in calculations:

```yaml
# Example (within an add‑on)
resources:
  - path: data/abilities.yaml
    kind: ability
ui_patches:
  - target: panel
    selector: "panel.abilities"
    action: add
    payload: ui/panels/psionics.fragment.yaml
entry_points:
  python:
    - "my_addon.logic:register"  # add modifiers into CalcService
```

**Notes:**

* New stats should be **namespaced** to avoid collisions (e.g., `psi_power`).
* Derived values (e.g., saves, DCs) plug in via **CalcService** hooks or declarative formulas in rules data.

**Q: Can add‑ons add entirely new systems/mechanics?**
**A:** Yes. An add‑on can ship a **rules module** (e.g., stress, sanity, grit, psionics), new **resources** (with rest/recharge semantics), **conditions**, **turn cycles**, or **resolution mechanics**. Wire them by registering with **RulesService**, exposing any routes/endpoints (optional), and patching the **UI schema** to surface controls and views. Ensure `engine_api_version` is declared in the Masterfile.

**Q: Are the D&D 5e references just examples?**
**A:** Yes. D&D 5e is the **baseline example ruleset** (SRD‑compatible) to prove the architecture. The core is system‑agnostic; other rulesets can be first‑class add‑ons.

**Q: Will this help Users/Devs/Agents understand and guide development?**
**A:** Yes. That is the goal of **AGENTS.md**: a single, stable **orientation document** describing purpose, style, contracts (Engine API, Masterfile), and safe extension points. Combined with JSON Schemas and tests, it enables confident extension and review.

---

**End of AGENTS.md**
