from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from models import Autor, Usuario
from schemas import AutorSchema

autor_router = APIRouter(prefix="/autor", tags=["autor"])

# rota principal: lista os autores
@autor_router.get("/")
async def listar(session: Session = Depends(pegar_sessao)):
    dados = session.query(Autor).all()
    return {
        "autores" : dados
    }

# rota de cadastrar autor
# requer perfil de admin
@autor_router.post("/cadastrar_autor")
async def cadastrar(autor_schema: AutorSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não possui autorização para fazer essa ação.")
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
    
# rota para excluir autor: necessario perfil de admin
@autor_router.delete("/excluir_autor/{id_autor}")
async def excluir(id_autor: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não possui autorização para fazer essa ação.")
    autor = session.query(Autor).filter(Autor.id == id_autor).first()
    if not autor:
        raise HTTPException(status_code=400, detail="Autor não encontrado.")
    else:
        session.delete(autor)
        session.commit()
        return {
            "mensagem" : f"Autor {id_autor} excluído com sucesso." 
        }