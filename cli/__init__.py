import asyncio
import datetime

import typer
import sys

app = typer.Typer()
import os


@app.command()
def hello(name: str, aer: str = typer.Option(..., )):
    typer.echo(f"hello {name}")
    typer.secho(aer, color='green')


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    else:
        typer.echo(f"Bye {name}!")


@app.command()
def access_token():
    from fast_tmp.models import User
    from fast_tmp.utils.token import create_access_token
    async def get_superuser():
        user = await User.filter(is_superuser=True).first()
        typer.echo(
            create_access_token(
                data={"sub": user.username},
                expires_delta=datetime.timedelta(
                    hours=30
                )
            )
        )

    asyncio.run(get_superuser())


if __name__ == "__main__":
    app()
