from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Carona, Reserva, Avaliacao
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ondago_secret_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ondago.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
import os
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB máximo

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def salvar_foto(ficheiro, usuario_id):
    ext = ficheiro.filename.rsplit('.', 1)[1].lower()
    filename = f"user_{usuario_id}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = Image.open(ficheiro)
    img = img.convert('RGB')
    img.thumbnail((200, 200))
    img.save(filepath, quality=85)
    return filename
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faz login para continuar.'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def index():
    caronas = Carona.query.all()
    activas = [c for c in caronas if not c.expirada]
    return render_template('index.html', caronas=activas)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome     = request.form['nome']
        email    = request.form['email']
        telefone = request.form['telefone']
        nivel    = request.form['nivel']
        senha    = request.form['senha']

        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está registado.', 'erro')
            return redirect(url_for('registro'))

        usuario = Usuario(nome=nome, email=email, telefone=telefone, nivel=nivel)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario)
        return redirect(url_for('index'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            return redirect(url_for('index'))
        flash('Email ou senha incorretos.', 'erro')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/nova', methods=['GET', 'POST'])
@login_required
def nova_carona():
    if request.method == 'POST':
        data_raw = request.form['data']
        dt = datetime.strptime(data_raw, "%Y-%m-%d")
        data_formatada = dt.strftime("%d/%m/%Y")

        carona = Carona(
            motorista_id  = current_user.id,
            ponto_partida = request.form['origem'],
            destino       = request.form['destino'],
            data          = data_formatada,
            hora          = request.form['hora'],
            vagas_totais  = int(request.form['vagas']),
            tipo_prancha  = request.form['prancha']
        )
        db.session.add(carona)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('nova_carona.html')

@app.route('/reservar/<int:carona_id>', methods=['GET', 'POST'])
@login_required
def reservar(carona_id):
    carona = Carona.query.get_or_404(carona_id)

    if request.method == 'POST':
        ja_reservou = Reserva.query.filter_by(
            carona_id=carona_id,
            usuario_id=current_user.id
        ).first()

        if ja_reservou:
            flash('Ja tens reserva nesta barca.', 'erro')
        elif carona.lotado:
            flash('Barca lotada!', 'erro')
        elif carona.motorista_id == current_user.id:
            flash('Nao podes reservar a tua propria barca.', 'erro')
        else:
            reserva = Reserva(carona_id=carona_id, usuario_id=current_user.id)
            db.session.add(reserva)
            db.session.commit()
            flash('Reserva feita com sucesso!', 'sucesso')
            return redirect(url_for('index'))

    return render_template('reservar.html', carona=carona)

@app.route('/minha_conta')
@login_required
def minha_conta():
    minhas_caronas = Carona.query.filter_by(motorista_id=current_user.id).all()
    minhas_reservas = Reserva.query.filter_by(usuario_id=current_user.id).all()
    avaliacoes_feitas = {
        (a.carona_id, a.avaliado_id)
        for a in Avaliacao.query.filter_by(avaliador_id=current_user.id).all()
    }
    return render_template('minha_conta.html', caronas=minhas_caronas, reservas=minhas_reservas,
                           avaliacoes_feitas=avaliacoes_feitas)
@app.route('/cancelar_reserva/<int:reserva_id>', methods=['POST'])
@login_required
def cancelar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)

    if reserva.usuario_id != current_user.id:
        flash('Nao tens permissao para cancelar esta reserva.', 'erro')
        return redirect(url_for('minha_conta'))

    if reserva.carona.expirada:
        flash('Nao podes cancelar uma carona ja realizada.', 'erro')
        return redirect(url_for('minha_conta'))

    db.session.delete(reserva)
    db.session.commit()
    flash('Reserva cancelada com sucesso.', 'sucesso')
    return redirect(url_for('minha_conta'))


@app.route('/editar_carona/<int:carona_id>', methods=['GET', 'POST'])
@login_required
def editar_carona(carona_id):
    carona = Carona.query.get_or_404(carona_id)

    if carona.motorista_id != current_user.id:
        flash('Nao tens permissao para editar esta barca.', 'erro')
        return redirect(url_for('minha_conta'))

    if carona.expirada:
        flash('Nao podes editar uma carona ja realizada.', 'erro')
        return redirect(url_for('minha_conta'))

    if request.method == 'POST':
        novas_vagas = int(request.form['vagas'])

        if novas_vagas < len(carona.reservas):
            flash(f'Ja tens {len(carona.reservas)} reservas. Nao podes reduzir abaixo disso.', 'erro')
            return redirect(url_for('editar_carona', carona_id=carona_id))

        data_raw = request.form['data']
        dt = datetime.strptime(data_raw, "%Y-%m-%d")

        carona.ponto_partida = request.form['origem']
        carona.destino       = request.form['destino']
        carona.data          = dt.strftime("%d/%m/%Y")
        carona.hora          = request.form['hora']
        carona.vagas_totais  = novas_vagas
        carona.tipo_prancha  = request.form['prancha']

        db.session.commit()
        flash('Barca actualizada!', 'sucesso')
        return redirect(url_for('minha_conta'))

    return render_template('editar_carona.html', carona=carona)
@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        if 'foto' in request.files:
            ficheiro = request.files['foto']
            if ficheiro and allowed_file(ficheiro.filename):
                filename = salvar_foto(ficheiro, current_user.id)
                current_user.foto_url = filename
                db.session.commit()
                flash('Foto actualizada com sucesso!', 'sucesso')

    return redirect(url_for('minha_conta'))
@app.route('/avaliar/<int:carona_id>/<int:avaliado_id>', methods=['GET', 'POST'])
@login_required
def avaliar(carona_id, avaliado_id):
    carona = Carona.query.get_or_404(carona_id)
    avaliado = Usuario.query.get_or_404(avaliado_id)

    if not carona.expirada:
        flash('Só podes avaliar depois da carona ter sido realizada.', 'erro')
        return redirect(url_for('minha_conta'))

    if avaliado_id == current_user.id:
        flash('Não podes avaliar-te a ti mesmo.', 'erro')
        return redirect(url_for('minha_conta'))

    eh_motorista = carona.motorista_id == current_user.id
    eh_passageiro = Reserva.query.filter_by(carona_id=carona_id, usuario_id=current_user.id).first() is not None

    if not eh_motorista and not eh_passageiro:
        flash('Não participaste nesta carona.', 'erro')
        return redirect(url_for('minha_conta'))

    avaliado_eh_motorista = carona.motorista_id == avaliado_id
    avaliado_eh_passageiro = Reserva.query.filter_by(carona_id=carona_id, usuario_id=avaliado_id).first() is not None

    if not avaliado_eh_motorista and not avaliado_eh_passageiro:
        flash('Esta pessoa não participou nesta carona.', 'erro')
        return redirect(url_for('minha_conta'))

    if Avaliacao.query.filter_by(avaliador_id=current_user.id, avaliado_id=avaliado_id, carona_id=carona_id).first():
        flash('Já avaliaste esta pessoa nesta carona.', 'erro')
        return redirect(url_for('minha_conta'))

    if request.method == 'POST':
        nota = float(request.form['nota'])
        if nota < 1 or nota > 5:
            flash('Nota inválida.', 'erro')
            return redirect(url_for('avaliar', carona_id=carona_id, avaliado_id=avaliado_id))
        avaliacao = Avaliacao(
            avaliador_id=current_user.id,
            avaliado_id=avaliado_id,
            carona_id=carona_id,
            nota=nota,
            comentario=request.form.get('comentario', '').strip(),
            tipo='motorista' if avaliado_eh_motorista else 'passageiro'
        )
        db.session.add(avaliacao)
        db.session.commit()
        flash('Avaliação enviada!', 'sucesso')
        return redirect(url_for('minha_conta'))

    return render_template('avaliar.html', carona=carona, avaliado=avaliado)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)