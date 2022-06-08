"""Command-line interface."""
import click
import uvicorn


@click.command()
@click.version_option()
def main() -> None:
    """entersim."""
    uvicorn.run("entersim.api.server:app", host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main(prog_name="entersim")  # pragma: no cover
