from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    nome:str
    email:str
    senha:str
    ativo:Optional[bool]
    admin:Optional[bool]

    class Config:
        from_attributes = True # conectar os modelos (ORM)

class LoginSchema(BaseModel):
    email:str
    senha:str

    class Config:
        from_attributes = True # nao tem modelo, tratar como classe e nao como dicionarios

class LivroSchema(BaseModel):
    titulo:str
    isbn: str
    id_autor:int
    qtd_total:int

    class Config:
        from_attributes = True # conectar os modelos (ORM)

class AutorSchema(BaseModel):
    nome:str

    class Config:
        from_attributes = True