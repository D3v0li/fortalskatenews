import os
import re
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Artigo, Pista

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar o painel."

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("instance", exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- Utilidades ----------
def gerar_slug(texto):
    texto = texto.lower()
    for a, b in [("áàãâä","a"),("éèêë","e"),("íìîï","i"),
                 ("óòõôö","o"),("úùûü","u"),("ç","c")]:
        for c in a:
            texto = texto.replace(c, b)
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")


def salvar_imagem(arquivo):
    if not arquivo or arquivo.filename == "":
        return None
    ext = arquivo.filename.rsplit(".", 1)[-1].lower()
    if ext not in app.config["ALLOWED_EXTENSIONS"]:
        return None
    nome = f"{datetime.utcnow().timestamp():.0f}_{secure_filename(arquivo.filename)}"
    arquivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nome))
    return nome


# ---------- Rotas públicas ----------
@app.route("/")
def index():
    destaque = Artigo.query.filter_by(status="publicado", destaque=True).first()
    artigos = (Artigo.query
               .filter_by(status="publicado")
               .order_by(Artigo.data_publicacao.desc())
               .limit(9).all())
    return render_template("index.html", destaque=destaque, artigos=artigos)


@app.route("/artigo/<slug>")
def artigo(slug):
    art = Artigo.query.filter_by(slug=slug, status="publicado").first_or_404()
    return render_template("artigo.html", artigo=art)


@app.route("/pistas")
def pistas():
    lista = Pista.query.filter_by(status="publicado").all()
    return render_template("pistas.html", pistas=lista)


@app.route("/pistas/<int:pista_id>")
def pista_detalhe(pista_id):
    pista = Pista.query.get_or_404(pista_id)
    return render_template("pista_detalhe.html", pista=pista)


@app.route("/preparacao-fisica")
def preparacao():
    lista = (Artigo.query
             .filter_by(status="publicado", categoria="preparacao")
             .order_by(Artigo.data_publicacao.desc()).all())
    return render_template("preparacao.html", artigos=lista)


@app.route("/quem-sou")
def quem_sou():
    return render_template("quem_sou.html")


# ---------- Autenticação ----------
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        usuario = request.form.get("username", "").strip()
        senha = request.form.get("password", "")
        user = User.query.filter_by(username=usuario).first()
        if user and user.check_password(senha):
            login_user(user)
            return redirect(url_for("admin_dashboard"))
        flash("Usuário ou senha inválidos.", "erro")
    return render_template("admin/login.html")


@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ---------- Painel administrativo ----------
@app.route("/admin")
@login_required
def admin_dashboard():
    artigos = Artigo.query.order_by(Artigo.data_publicacao.desc()).all()
    pistas = Pista.query.order_by(Pista.data_cadastro.desc()).all()
    return render_template("admin/dashboard.html", artigos=artigos, pistas=pistas)


@app.route("/admin/artigos/novo", methods=["GET", "POST"])
@login_required
def novo_artigo():
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        slug = gerar_slug(request.form.get("slug") or titulo)
        base, cont = slug, 1
        while Artigo.query.filter_by(slug=slug).first():
            cont += 1
            slug = f"{base}-{cont}"

        art = Artigo(
            titulo=titulo,
            slug=slug,
            categoria=request.form["categoria"],
            subcategoria=request.form.get("subcategoria", ""),
            resumo=request.form["resumo"],
            conteudo=request.form["conteudo"],
            imagem_capa=salvar_imagem(request.files.get("imagem")),
            destaque=bool(request.form.get("destaque")),
            status=request.form.get("status", "rascunho"),
        )
        db.session.add(art)
        db.session.commit()
        flash("Artigo criado com sucesso!", "sucesso")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_artigo.html", artigo=None)


@app.route("/admin/artigos/<int:artigo_id>/editar", methods=["GET", "POST"])
@login_required
def editar_artigo(artigo_id):
    art = Artigo.query.get_or_404(artigo_id)
    if request.method == "POST":
        art.titulo = request.form["titulo"].strip()
        art.categoria = request.form["categoria"]
        art.subcategoria = request.form.get("subcategoria", "")
        art.resumo = request.form["resumo"]
        art.conteudo = request.form["conteudo"]
        art.destaque = bool(request.form.get("destaque"))
        art.status = request.form.get("status", "rascunho")
        nova_img = salvar_imagem(request.files.get("imagem"))
        if nova_img:
            art.imagem_capa = nova_img
        db.session.commit()
        flash("Artigo atualizado.", "sucesso")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_artigo.html", artigo=art)


@app.route("/admin/artigos/<int:artigo_id>/excluir", methods=["POST"])
@login_required
def excluir_artigo(artigo_id):
    art = Artigo.query.get_or_404(artigo_id)
    db.session.delete(art)
    db.session.commit()
    flash("Artigo excluído.", "sucesso")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/pistas/nova", methods=["GET", "POST"])
@login_required
def nova_pista():
    if request.method == "POST":
        pista = Pista(
            nome=request.form["nome"].strip(),
            bairro=request.form["bairro"].strip(),
            endereco=request.form.get("endereco", ""),
            descricao=request.form["descricao"],
            estrutura=request.form.get("estrutura", ""),
            observacoes=request.form.get("observacoes", ""),
            link_maps=request.form.get("link_maps", ""),
            imagem=salvar_imagem(request.files.get("imagem")),
        )
        db.session.add(pista)
        db.session.commit()
        flash("Pista cadastrada!", "sucesso")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_pista.html", pista=None)


@app.route("/admin/pistas/<int:pista_id>/editar", methods=["GET", "POST"])
@login_required
def editar_pista(pista_id):
    pista = Pista.query.get_or_404(pista_id)
    if request.method == "POST":
        pista.nome = request.form["nome"].strip()
        pista.bairro = request.form["bairro"].strip()
        pista.endereco = request.form.get("endereco", "")
        pista.descricao = request.form["descricao"]
        pista.estrutura = request.form.get("estrutura", "")
        pista.observacoes = request.form.get("observacoes", "")
        pista.link_maps = request.form.get("link_maps", "")
        nova = salvar_imagem(request.files.get("imagem"))
        if nova:
            pista.imagem = nova
        db.session.commit()
        flash("Pista atualizada.", "sucesso")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_pista.html", pista=pista)


@app.route("/admin/pistas/<int:pista_id>/excluir", methods=["POST"])
@login_required
def excluir_pista(pista_id):
    pista = Pista.query.get_or_404(pista_id)
    db.session.delete(pista)
    db.session.commit()
    flash("Pista excluída.", "sucesso")
    return redirect(url_for("admin_dashboard"))


# ---------- Filtros Jinja ----------
@app.template_filter("data_br")
def data_br(valor):
    if not valor:
        return ""
    return valor.strftime("%d/%m/%Y")


@app.template_filter("resumo_curto")
def resumo_curto(texto, n=140):
    if not texto:
        return ""
    return texto[:n] + ("..." if len(texto) > n else "")


# ---------- Inicialização ----------
def criar_admin_padrao():
    if not User.query.first():
        u = User(username=app.config["ADMIN_USER"])
        senha = os.getenv("ADMIN_PASSWORD", "skate123")
        u.set_password(senha)
        db.session.add(u)
        db.session.commit()
        print(f"[init] Usuário admin criado: {app.config['ADMIN_USER']} / {senha}")


with app.app_context():
    db.create_all()
    criar_admin_padrao()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)