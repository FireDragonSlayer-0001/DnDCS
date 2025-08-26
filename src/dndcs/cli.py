import json
import click

@click.group()
def main():
    """DnDCS CLI."""
    pass

@main.command("ui")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, type=int, show_default=True)
@click.option("--no-open", is_flag=True, help="Do not auto-open the browser")
def ui(host: str, port: int, no_open: bool):
    """Start local web UI and open it in your browser."""
    try:
        from dndcs.ui.server import serve
    except Exception as e:
        import traceback, sys
        click.echo("UI dependencies missing or import failed.", err=True)
        click.echo('Tip (PowerShell): python -m pip install -e ".[ui]"', err=True)
        click.echo(f"\nImport error: {e}\n{traceback.format_exc()}", err=True)
        sys.exit(1)
    serve(host=host, port=port, open_browser=(not no_open))


@main.group()
def spells():
    """Spell search helpers."""
    pass


@spells.command("find")
@click.argument("name")
def find_spell(name: str):
    """Show details for a spell by name."""
    from dndcs.modules.fivee_stock.spells.example import get_spell

    sp = get_spell(name)
    if not sp:
        click.echo("Spell not found", err=True)
        return
    click.echo(json.dumps(sp, indent=2))


@spells.command("for-class")
@click.argument("cls")
def spells_for_class(cls: str):
    """List spells available to a class."""
    from dndcs.modules.fivee_stock.spells.example import get_spells_for_class

    spells = get_spells_for_class(cls)
    for sp in sorted(spells, key=lambda s: (s["level"], s["name"])):
        click.echo(f"Level {sp['level']}: {sp['name']}")


@spells.command("search")
@click.option("--name", "name", help="Substring to search for")
@click.option("--class", "cls", help="Filter by class")
def search_spells(name: str | None, cls: str | None):
    """Search spells by name and/or class."""
    from dndcs.modules.fivee_stock.spells.example import search

    results = search(name=name, cls=cls)
    for sp in sorted(results, key=lambda s: (s["level"], s["name"])):
        click.echo(f"{sp['name']} (Level {sp['level']} {sp['school']})")
