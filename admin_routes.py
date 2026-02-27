from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token, verificar_admin
from models import Usuario

admin_router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verificar_admin)])

@admin_router.get("/listar_usuarios")
async def listar(session: Session = Depends(pegar_sessao)):
    usuarios = session.query(Usuario).all()
    return {
        "usuarios" : usuarios
    }

@admin_router.delete("/excluir_usuario/{id_usuario}")
async def excluir(id_usuario: int, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    else:
        session.delete(usuario)
        session.commit()
        return {
            "mensagem" : f"Usuário {id_usuario} excluído com sucesso."
        }