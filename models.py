from datetime import date

from sqlalchemy import create_engine, Column, String, Boolean, Integer, ForeignKey, Date

from sqlalchemy.orm import declarative_base

# cria a conexao com o banco de dados SQLite
DATABASE_URL = "sqlite:///banco.db" # postgres: "postgresql://postgres:postgres@localhost:5432/biblioteca"
db = create_engine(DATABASE_URL) # cria a conexao com o banco

# Cria a base do banco de dados
Base = declarative_base() # cria a base para definir as tabelas (ORM)

# criar as classes/tabelas do banco
# Usuario
class Usuario(Base):
    __tablename__ = "usuarios" # opcional: nome

    # colunas
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, default="nome")
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    # construtor
    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


# Autor
class Autor(Base):
    __tablename__ = "autores"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, default="nome autor")

    def __init__(self, nome="nome autor"):
        self.nome = nome

# Livro
class Livro(Base):
    __tablename__ = "livros"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    titulo = Column("titulo", String)
    isbn = Column("isbn", String, unique=True) # codigo unico internacional do livro
    id_autor = Column("id_autor", ForeignKey("autores.id"), nullable=False)
    qtd_total = Column("qtd_total", Integer, default=1)
    qtd_disponivel = Column("qtd_disponivel", Integer, default=1)

    def __init__(self, titulo, isbn, id_autor, qtd_total = 1):
        self.titulo = titulo
        self.isbn = isbn
        self.id_autor = id_autor
        self.qtd_total = qtd_total
        self.qtd_disponivel = qtd_total


# Emprestimo
class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    id_livro = Column("id_livro", ForeignKey("livros.id"), nullable=False)
    id_usuario = Column("id_usuario", ForeignKey("usuarios.id"), nullable=False)
    data_emprestimo = Column("data_emprestimo", Date, default=date.today())
    data_devolucao = Column("data_devolucao", Date, nullable=False)
    status = Column("status", String, default="ativo")

    def __init__(self, id_livro, id_usuario, data_devolucao, data_emprestimo=date.today(), status="ativo"):
        self.id_livro = id_livro
        self.id_usuario = id_usuario
        self.data_devolucao = data_devolucao
        self.data_emprestimo = data_emprestimo
        self.status = status

# executar a criação dos metadados do seu banco (criar efetivamente o banco de dados)