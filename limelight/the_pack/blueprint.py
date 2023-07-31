import click
from flask import Blueprint
from rich import print

from ..database import db
from ..models import StarQueue
from . import yuko

blueprint = Blueprint("pack", __name__, cli_group="pack")


@blueprint.cli.command("create-package", help="Creates a PyPi Package (Public or Private)")
@click.argument("registry", type=click.Choice(["pypi", "conda"], case_sensitive=False))
@click.option(
    "--slug",
    "slug",
    type=str,
    help="The project's Slug",
    multiple=True,
)
@click.option("--url", "url", type=str, help="The project's URL", multiple=True)
def create_package(registry, slug: str = None, url: str = None):
    if not slug and not url:
        raise click.UsageError("You need `--slug` or `--url` to be set")
    print(f"create-package {registry} {slug=} {url=}")
    if registry == "pypi":
        for project in slug:
            print(f"{project=}")
            db.session.add(StarQueue(pypi_slug=project, status="created"))
        db.session.commit()
