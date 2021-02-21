import asyncio
import datetime
import dotenv
import typer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_tmp.conf import settings
from fast_tmp.db import get_db_session, SessionLocal

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
def create_superuser(username: str, password: str):
    """
    创建超级用户
    """
    from fast_tmp.models import User
    async def create_user(username, password):
        async with SessionLocal() as session:
            async with session.begin():
                user = User(
                    # id=1,
                    username=username,
                    password=password
                )
                session.add(user)
                await session.flush()
                return

    asyncio.run(create_user(username, password))


def main():
    app()


if __name__ == "__main__":
    main()
