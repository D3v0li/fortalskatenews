"""
Script para trocar a senha do admin.
Uso: python trocar_senha.py
"""
from getpass import getpass
from app import app
from models import db, User

with app.app_context():
    usuario_nome = input("Usuário admin (Enter para 'admin'): ").strip() or "admin"
    user = User.query.filter_by(username=usuario_nome).first()

    if not user:
        print(f"❌ Usuário '{usuario_nome}' não encontrado.")
        exit(1)

    print(f"✅ Usuário encontrado: {user.username}")
    nova = getpass("Nova senha (não aparece na tela): ")
    confirmar = getpass("Confirme a nova senha: ")

    if nova != confirmar:
        print("❌ As senhas não coincidem.")
        exit(1)

    if len(nova) < 6:
        print("❌ Senha muito curta. Use pelo menos 6 caracteres.")
        exit(1)

    user.set_password(nova)
    db.session.commit()
    print(f"✅ Senha de '{user.username}' alterada com sucesso!")