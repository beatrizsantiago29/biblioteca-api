from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Autor, Usuario
from schemas import AutorSchema 
from datetime import timedelta, timezone, datetime

author_router = APIRouter(prefix="/autor", tags=["autor"], dependencies=[Depends(verificar_token)])

@author_router.post("/cadastrar_autor")
async def cadastrar(autor_schema: AutorSchema, session: Session = Depends(pegar_sessao)):
    autor = session.query(Autor).filter(Autor.nome == autor_schema.nome).first()
    if autor:
        raise HTTPException(status_code=400, detail="Autor já cadastrado.")
    else:
        novo_autor = Autor(autor_schema.nome)
        session.add(novo_autor)
        session.commit()
        return {
            "mensagem": f"Autor {autor_schema.nome} cadastrado com sucesso."
        }