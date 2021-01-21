import asyncio
import datetime
import dotenv
import typer

from tortoise import Tortoise

from fast_tmp.conf import settings

app = typer.Typer()


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
    """
    获取token
    :return:
    """
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


@app.command()
def create_superuser(username: str, password: str):
    """
    创建超级用户
    """
    from fast_tmp.models import User
    async def create_user(username, password):
        dotenv.load_dotenv()
        await Tortoise.init(config=settings.TORTOISE_ORM)
        user = User(username=username)
        user.set_password(password)
        await user.save()
        await Tortoise.close_connections()
        typer.echo("创建成功")
    asyncio.run(create_user(username, password))


def main():
    app()


if __name__ == "__main__":
    main()
