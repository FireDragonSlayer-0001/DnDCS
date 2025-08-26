# DnDCS

Modular backend for Dungeons & Dragons character sheets with an integrated web UI.

## Features
- Discoverable rules modules loaded from `mods/`, `modules/` or a user config directory.
- Command line interface `dndcs` with a subcommand to launch a local web interface.

## Installation
Requires **Python 3.10+**. Clone the repository and install with the included script:

```bash
git clone https://github.com/FireDragonSlayer-0001/DnDCS
cd DnDCS
./install.sh
```

## Usage
Start the web interface:

```bash
./run.sh
```

The server listens on `http://127.0.0.1:8000` by default and opens in your browser. Use `--host`, `--port` and `--no-open` to control the startup behaviour.

Rules modules are discovered automatically. Drop a module directory containing a `manifest.yaml` and a main file into `mods/` or `modules/` to extend the rules. The manifest can declare a `subsystems` list so Python files placed in those named subfolders (for example `items/`, `feats` or `spells`) are pulled in automatically. See `src/dndcs/modules/fivee_stock` for a built-in 5e implementation example.

## Character Model

The `dndcs.core.models.Character` schema contains the core data for a character. In addition to baseline fields such as `name`, `level`, and `module`, the model also supports:

- `class` – character class
- `subclass` – optional subclass or archetype
- `race` – character race
- `background` – starting background
- `alignment` – moral alignment
- `hit_points` – current hit point total
- `hit_dice` – hit dice expression (e.g. `"1d8"`)
- `spellcasting` – spellcasting data, free-form and module defined
- `companions` – list of companion characters

All of these fields are optional and default to empty or `None` so existing code that constructs a `Character` without them continues to work.
