from .app import app
from db_init import db
ctx = app.app_context()
ctx.push()
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    preco = db.Column(db.Float, nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(80), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    produto = db.relationship('Produto', backref=db.backref('pedidos', lazy=True))
    quantidade = db.Column(db.Integer, nullable=False)
    pago = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default='Preparando')

    ctx.pop()