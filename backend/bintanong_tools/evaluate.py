from __future__ import annotations

from pathlib import Path
import typer

app = typer.Typer(
    name="evaluate",
    help="Bintanong evaluation and benchmark runner tool suite.",
    no_args_is_help=True,
)


@app.command("run")
def run_cmd(
    dataset: Path = typer.Option(None, "--dataset", "-d", help="Path to evaluation dataset"),
    output: Path = typer.Option(None, "--output", "-o", help="Path to write evaluation report"),
) -> None:
    """Run neuro-symbolic and RAG evaluation benchmarks."""
    typer.echo("Bintanong Evaluation Runner: benchmark pipeline ready.")


if __name__ == "__main__":
    app()
