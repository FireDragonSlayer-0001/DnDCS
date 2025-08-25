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
