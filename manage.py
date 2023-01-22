import click
import uvicorn

from app.core.config import settings


@click.group()
def cli() -> None:
    pass


@cli.command()
def runserver() -> None:
    uvicorn.run(
        "app.main:app_factory",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.AUTO_RELOAD,
        factory=True,
    )


if __name__ == "__main__":
    cli()
