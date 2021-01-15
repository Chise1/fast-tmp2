from  io import StringIO
from pydantic import BaseModel
class A(BaseModel):
    s:StringIO
s=StringIO("x1")
a=A(s=s)
print(a.dict())
s.write("tou"+s.getvalue())
print(a.dict())