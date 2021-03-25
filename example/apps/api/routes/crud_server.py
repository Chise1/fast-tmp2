from example.models import Message
from fast_tmp.amis.creator_server import CRUD_Server
from fast_tmp.amis_router import AmisRouter
from fast_tmp.models import User

crud_server_route = AmisRouter(title="server test", prefix="/server")
CRUD_Server(crud_server_route, base_path="server", model=Message, searchs=["info"], filters=["id"])
crud_user_route = AmisRouter(title="user test", prefix="/user")
CRUD_Server(crud_user_route, base_path="user", model=User)
