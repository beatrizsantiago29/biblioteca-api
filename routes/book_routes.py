from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import LivroSchema
from models import Livro, Autor, Usuario, Emprestimo

book_router = APIRouter(prefix="/book", tags=["book"])

# rota principal: listar livros
@book_router.get("/")
async def listar(session: Session = Depends(pegar_sessao)):
    dados = session.query(Livro).all()
    return {
        "livros" : dados
    }

# rota cadastro de livro: requer perfil de admin
@book_router.post("/cadastro", status_code=status.HTTP_201_CREATED)
async def cadastrar(livro_schema: LivroSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui autorização para fazer essa ação.")
    
    # verificar se o autor é válido
    autor = session.query(Autor).filter(Autor.id == livro_schema.id_autor).first()
    if not autor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor não encontrado.")

    # verificar se o livro ja existe (nome e autor)
    livro = session.query(Livro).filter(Livro.titulo==livro_schema.titulo, Livro.id_autor == livro_schema.id_autor).first()
    if livro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O livro já está cadastrado")
    else:
        session.add(Livro(livro_schema.titulo, livro_schema.isbn, livro_schema.id_autor, livro_schema.qtd_total))
        session.commit()
        return {"mensagem":f"livro {livro_schema.titulo} cadastrado com sucesso"}


@book_router.put("/{id_livro}")
async def alterar(id_livro: int, livro_schema: LivroSchema, session: Session=Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui autorização para realizar essa ação.")
    # Verificar se o livro é válido
    livro = session.query(Livro).filter(Livro.id == id_livro).first()
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    else:
        # Verificar se o autor é válido
        autor = session.query(Autor).filter(Autor.id == livro_schema.id_autor).first()
        if not autor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor não encontrado.")
        
        # Verificar se a quantidade total nova é válida (superior à quantidade "ativa"/emprestada de livros)
        qtd_emprestado = livro.qtd_total - livro.qtd_disponivel
        if  livro_schema.qtd_total < qtd_emprestado:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Quantidade total não pode ser inferior à quantidade atual de livros emprestados: {qtd_emprestado}.")
        
        # Tudo OK (exceto se o isbn for repetido)
        livro.isbn = livro_schema.isbn

        # Tudo OK
        livro.titulo = livro_schema.titulo
        livro.id_autor = livro_schema.id_autor
        livro.qtd_total = livro_schema.qtd_total
        livro.qtd_disponivel = livro_schema.qtd_total - qtd_emprestado
        session.commit()
        session.refresh(livro)
        return {"mensagem":f"livro {livro.id} alterado com sucesso"}

# rota para excluir livro: necessario perfil de admin
@book_router.delete("/{id_livro}")
async def deletar(id_livro: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui autorização para fazer essa ação.")
    livro = session.query(Livro).filter(Livro.id == id_livro).first()
    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    else: 
        # verificar se o livro está associado a algum emprestimo
        emprestimo = session.query(Emprestimo).filter(Emprestimo.id_livro == id_livro).first()
        if emprestimo:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O livro possui empréstimos associados.")
        
        session.delete(livro)
        session.commit()
        return {"mensagem":f"livro {id_livro} deletado com sucesso"}