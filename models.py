from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, senha):
        self.password_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.password_hash, senha)


class Artigo(db.Model):
    __tablename__ = "artigos"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    subcategoria = db.Column(db.String(50))
    resumo = db.Column(db.String(300), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    imagem_capa = db.Column(db.String(255))
    destaque = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="rascunho")
    data_publicacao = db.Column(db.DateTime, default=datetime.utcnow)


class Pista(db.Model):
    __tablename__ = "pistas"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(255))
    descricao = db.Column(db.Text, nullable=False)
    estrutura = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    imagem = db.Column(db.String(255))
    link_maps = db.Column(db.String(500))
    status = db.Column(db.String(20), default="publicado")
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)