# DnDCS

Modular backend for Dungeons & Dragons character sheets with an optional web UI.

## Features
- Discoverable rules modules loaded from `mods/`, `modules/` or a user config directory.
- Command line interface `dndcs` with a subcommand to launch a local web interface.
- Minimal standalone script `first_program.py` to create and inspect character files without extra dependencies.

## Installation
Requires **Python 3.10+**. Clone the repository and install with pip:

```bash
git clone https://github.com/FireDragonSlayer-0001/DnDCS
cd DnDCS
python -m pip install -e .
```

To include the optional web UI dependencies:

```bash
python -m pip install -e .[ui]
```

## Usage
Start the web interface:

```bash
dndcs ui
```

The server listens on `http://127.0.0.1:8000` by default and opens in your browser. Use `--host`, `--port` and `--no-open` to control the startup behaviour.

Rules modules are discovered automatically. Drop a module directory containing a `manifest.yaml` into `mods/` or `modules/` to extend the rules. The repository includes an example placeholder module for D&D 5e under `modules/fivee`.

For a minimal dependency-free CLI demo:

```bash
python first_program.py --help
```
