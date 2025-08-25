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
    except Exception:
        raise SystemExit("UI deps missing. Install with: pip install -e .[ui]")
    serve(host=host, port=port, open_browser=(not no_open))
