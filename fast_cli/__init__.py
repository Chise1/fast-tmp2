import asyncio
import datetime
import typer

app = typer.Typer()


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
def createsuperuser(username: str, password: str):
    """
    创建超级用户
    """
    import os
    project_slug = os.path.split(os.getcwd())[1]
    os.environ.setdefault('FASTAPI_SETTINGS_MODULE', project_slug + ".settings")
    from fast_tmp.db import SessionLocal
    from fast_tmp.models import User
    async def create_user(username, password):
        async with SessionLocal() as session:
            async with session.begin():
                user = User(
                    username=username, is_superuser=True
                )
                user.set_password(password)
                session.add(user)
                await session.flush()

    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(create_user(username, password), loop)
    print(f"创建{username}成功")

    @app.command()
    def startapp():
        import sys
        print(sys.path[0])
        import os
        basedir = os.path.abspath(os.path.dirname(__file__))
        from cookiecutter.main import cookiecutter
        cookiecutter(basedir + "/tpl/")

    def main():
        app()

    if __name__ == "__main__":
        main()
