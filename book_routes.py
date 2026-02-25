from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import LivroSchema
from models import Livro, Autor, Usuario

book_router = APIRouter(prefix="/book", tags=["book"])

@book_router.post("/cadastrar_livro")
async def cadastrar(livro_schema: LivroSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    # verificar se o autor é válido
    autor = session.query(Autor).filter(Autor.id == livro_schema.id_autor).first()
    if not autor:
        raise HTTPException(status_code=400, detail="Autor inválido.")

    # verificar se o livro ja existe (nome e autor)
    livro = session.query(Livro).filter(Livro.titulo==livro_schema.titulo, Livro.id_autor == livro_schema.id_autor).first()
    if livro:
        raise HTTPException(status_code=400, detail="O livro já está cadastrado")
    else:
        session.add(Livro(livro_schema.titulo, livro_schema.isbn, livro_schema.id_autor, livro_schema.qtd_total))
        session.commit()
        return {"mensagem":f"livro {livro_schema.titulo} cadastrado com sucesso"}


# @book_router.delete("/delete")
# async def deletar(isbn: str, session: Session = Depends(pegar_sessao)):
#     livro = session.query(Livro).filter(Livro.isbn == isbn).first()
#     if livro:
#         session.delete(livro)
#         session.commit
#         return {"mensagem":f"livro {livro.titulo} deletado com sucesso"}
    
