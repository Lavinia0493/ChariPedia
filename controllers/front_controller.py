from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
import requests
from models.data_manager import load_data_fav, save_data_fav, load_data_user, save_data_user
import config
import os
import uuid

front_controller = Blueprint('front_controller', __name__)

def imgPerfil():
    usuarios = load_data_user()
    user_email = session.get('user')
    user_img = None

    if user_email:
        for u in usuarios:
            if u['email'] == user_email:
                user_img = u.get('imagem')
                break
    return user_img

@front_controller.route('/')
def home():
    data = load_data_user()
    userAtual = session.get('user')
    item = next((item for item in data if item["email"] == userAtual), None)
    if item:
        nome = item["nome"]
    else: 
        nome = None

    return render_template("home.html", user_img = imgPerfil(), nome = nome)

def upload_imagem(imagem):    
    # Garante que a pasta de upload exista
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True) #garante que o diretório upload existe ou, caso contrário, ele é criado
    
    if (not getattr(imagem,"filename","")):
        flash("Nenhum arquivo carregado.", "danger")
        return None
    elif (not verificarArquivos(imagem)):
        flash("Formato de arquivo não permitido.", "warning")
        return None
    else:
        # Gera um nome ÚNICO para a imagem e salva no diretório de uploads
        filename = f"{uuid.uuid4()}.{imagem.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        imagem.save(filepath)
        return f"static/uploads/image/{filename}"  # Caminho relativo para salvar no JSON, junto ao dados do contato
    
def verificarArquivos(imagem):
    	return ('.' in imagem.filename and imagem.filename.rsplit('.', 1)[1].lower() in config.TIPOS_IMAGEM)
    #Verifica se o arquivo está em um dos formatos permitidos 

@front_controller.route("/cadastro", methods=["POST", "GET"])
def cadastro():
    if request.method == "POST":
        data = load_data_user( )

        nome = request.form.get("usuario")
        senha = request.form.get("senha")
        email = request.form.get("email")
        imagem = request.files.get("fileFoto")
        
        imagem_path = upload_imagem(imagem)

        repeticao = False
        for item in data:
            if email == item["email"]:
                repeticao = True
                break

        if not repeticao:
            data.append({"nome": nome, "senha": senha, "email": email, "imagem": imagem_path})
            data.sort(key=lambda x: x["nome"])
            save_data_user(data)  
            flash("Dados adicionados com sucesso!", "success")
            return(redirect(url_for("front_controller.pokemons")))
        else:
            flash("E-mail já cadastrado!", "warning")
    return(render_template('cadastro.html', user_img = imgPerfil()))

@front_controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        email = request.form.get('email')

        usuarios = load_data_user()

        i = True
        for item in usuarios:
            if item['email'] == email and item['senha'] == senha and item['nome'] == usuario:
                i = False

        if i == False:
            session["user"] = email
            flash(f"{usuario} logado com sucesso!", "success")
            return(redirect(url_for('front_controller.pokemons')))
        else:
            flash("Dados incorretos.", "danger")
    return render_template("login.html", user_img = imgPerfil())

@front_controller.route("/editar_login", methods = ["POST", "GET"])
def editar_login():
    data = load_data_user()
    item_email = session.get('user')
    item = next((item for item in data if item['email'] == item_email), None)

    if not item:
        flash("Os dados não foram encontrados!", "danger")
        return "Contato não encontrado", 404
    
    if request.method == "POST":
        item['nome'] = request.form.get('usuario')
        item['senha'] = request.form.get('senha')
        item['email'] = request.form.get('email')
        session['user'] = request.form.get('email')

        nova_imagem = request.files.get("fileFoto")
        novo_caminho = upload_imagem(nova_imagem)

        if (item.get("imagem") != None):
            caminho_antigo = os.path.join(config.BASE_DIR, item.get("imagem"))
            
            if (os.path.exists(caminho_antigo)):
                os.remove(caminho_antigo)

        # Atualiza o caminho da imagem no JSON (relativo)
        item["imagem"] = novo_caminho

        # Ordena os contatos por nome e salva os dados no JSON
        data.sort(key=lambda x: x["nome"])
        save_data_user(data)
        flash("Dados alterados com sucesso!", "success")
        return redirect(url_for("front_controller.home"))
    return render_template("editar.html", item=item, user_img = imgPerfil())

@front_controller.route("/excluir")
def excluir():
    data = load_data_user()
    fav = load_data_fav()
    userAtual = session.get('user')
    
    removido_fav = [f for f in fav if f["email"] != userAtual]
    removido = [u for u in data if u["email"] != userAtual]
    data = removido
    save_data_user(data)
    save_data_fav(removido_fav)
    session['user'] = None
    return(redirect(url_for('front_controller.home')))

@front_controller.route('/logout', methods=["GET", "POST"])
def logout():
    session['user'] = None
    return(redirect(url_for('front_controller.home')))

@front_controller.route('/pokemons', methods = ["GET", "POST"])
def pokemons():

    pokemons_dados = []

    api_base = "https://pokeapi.co/api/v2/pokemon?limit=1025"

    resp = requests.get(api_base)
    if(resp.status_code == 200):
        dados = resp.json()

        for i, poke in enumerate(dados['results'], start=1):
            nome = poke['name']
            img = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{i}.png"

            pokemons_dados.append(
                {
                    "nome": nome,
                    "img": img
                }
            )

    else:
        flash('Erro de carregamento.', 'danger')
    return(render_template('pokemons.html', pokemons_dados = pokemons_dados, user_img = imgPerfil())) 


@front_controller.route('/favoritos', methods = ["GET", "POST"])
def favoritos():
    if (session.get('user')):
        favoritos = load_data_fav()
        userAtual = session.get('user')

        favoritos_usuario = [f for f in favoritos if f["email"] == userAtual]

        if request.method == "POST":
            nome = request.form.get('nome')
            img = request.form.get('img')

            for item in favoritos:
                if (item['email'] == userAtual) and (item['img'] == img):
                    flash("Você já favoritou este pokemon.", "danger")
                    return(redirect(url_for('front_controller.pokemons')))
                
            favoritos.append({"email": userAtual, "nome": nome, "img": img})
            save_data_fav(favoritos)
            flash("Pokemon favoritado com sucesso!", "success")

            favoritos_usuario = [f for f in favoritos if f["email"] == userAtual]
        if not favoritos:
            flash('Você ainda não tem nenhum pokemon favoritado.', 'danger')
            return(redirect(url_for("front_controller.pokemons")))
        return(render_template('favoritos.html', favoritos_usuario = favoritos_usuario, user_img = imgPerfil()))
    else:
        flash('Você precisa estar logado para favoritar pokemons!', 'danger')
        return(redirect(url_for('front_controller.login')))
    

@front_controller.route('/remover_poke', methods = ["POST", "GET"])
def remover_poke():
    if request.method == "POST":
        nome = request.form.get('nome')
        favoritos = load_data_fav()
        userAtual = session.get('user')


        removidos = [f for f in favoritos if f['nome'] != nome and f['email'] == userAtual]
        favoritos = removidos
        save_data_fav(favoritos)
        flash(f"{nome} removido com sucesso!", "success")
        return(redirect(url_for('front_controller.pokemons')))
    
@front_controller.route('/apelidar', methods = ["POST", "GET"])
def apelidar():
    if request.method == "POST":
        nome = request.form.get('nome')
        userAtual = session.get('user')
        apelido = request.form.get('apelido')

        favoritos = load_data_fav()

        for item in favoritos:
            if item['nome'] == nome and item['email'] == userAtual:
                item['nome'] = apelido

        save_data_fav(favoritos)
        return(redirect(url_for('front_controller.favoritos')))
    
@front_controller.route('/pesquisar', methods = ["POST", "GET"])
def pesquisar():
    if request.method == "POST":
        pesquisa = request.form.get('pesquisar')

        if not pesquisa:
            flash('Digite o nome de um pokemon.', 'danger')
            return(redirect(url_for('front_controller.pokemons')))

        url = f"https://pokeapi.co/api/v2/pokemon/{pesquisa}"
        resp = requests.get(url)

        if resp.status_code != 200:
            flash("Pokémon não encontrado!", "danger")
            return redirect(url_for('front_controller.pokemons'))

        dados = resp.json()

        resultado = [{
            "nome": dados['name'],
            "img": dados['sprites']['front_default']
        }]  
    return(render_template('pokemons.html', pokemons_dados = resultado, user_img = imgPerfil()))