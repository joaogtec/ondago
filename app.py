from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, Usuario, Carona, Reserva, Avaliacao
from datetime import datetime
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from PIL import Image

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_key_apenas_para_desenvolvimento')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ondago.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

# Rate limiting — protege contra ataques de força bruta
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faz login para continuar.'

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

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.context_processor
def utility_processor():
    def media_avaliacoes(usuario_id, tipo):
        avals = Avaliacao.query.filter_by(avaliado_id=usuario_id, tipo=tipo).all()
        if not avals:
            return None
        return round(sum(a.nota for a in avals) / len(avals), 1)

    def total_avaliacoes(usuario_id, tipo):
        return Avaliacao.query.filter_by(avaliado_id=usuario_id, tipo=tipo).count()

    return dict(media_avaliacoes=media_avaliacoes, total_avaliacoes=total_avaliacoes)

@app.route('/')
def index():
    caronas = Carona.query.all()
    activas = [c for c in caronas if not c.expirada]
    return render_template('index.html', caronas=activas)

@app.route('/registro', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def registro():
    if request.method == 'POST':
        nome     = request.form.get('nome', '').strip()
        email    = request.form.get('email', '').strip().lower()
        telefone = request.form.get('telefone', '').strip()
        nivel    = request.form.get('nivel', 'Iniciante')
        senha    = request.form.get('senha', '')

        if len(nome) < 2:
            flash('Nome invalido.', 'erro')
            return redirect(url_for('registro'))
        if len(senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'erro')
            return redirect(url_for('registro'))
        if Usuario.query.filter_by(email=email).first():
            flash('Este email ja esta registado.', 'erro')
            return redirect(url_for('registro'))

        usuario = Usuario(nome=nome, email=email, telefone=telefone, nivel=nivel)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario)
        return redirect(url_for('index'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
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
        data_raw = request.form.get('data', '')
        try:
            dt = datetime.strptime(data_raw, "%Y-%m-%d")
            if dt < datetime.now():
                flash('A data tem de ser no futuro.', 'erro')
                return redirect(url_for('nova_carona'))
        except ValueError:
            flash('Data invalida.', 'erro')
            return redirect(url_for('nova_carona'))

        data_formatada = dt.strftime("%d/%m/%Y")
        vagas = int(request.form.get('vagas', 1))
        if vagas < 1 or vagas > 8:
            flash('Numero de vagas invalido.', 'erro')
            return redirect(url_for('nova_carona'))

        carona = Carona(
            motorista_id  = current_user.id,
            ponto_partida = request.form.get('origem', '').strip(),
            destino       = request.form.get('destino', '').strip(),
            data          = data_formatada,
            hora          = request.form.get('hora', ''),
            vagas_totais  = vagas,
            tipo_prancha  = request.form.get('prancha', 'Qualquer')
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
        elif carona.expirada:
            flash('Esta barca ja expirou.', 'erro')
        else:
            reserva = Reserva(carona_id=carona_id, usuario_id=current_user.id)
            db.session.add(reserva)
            db.session.commit()
            flash('Reserva feita com sucesso!', 'sucesso')
            return redirect(url_for('index'))

    return render_template('reservar.html', carona=carona)

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
        novas_vagas = int(request.form.get('vagas', 1))

        if novas_vagas < len(carona.reservas):
            flash(f'Ja tens {len(carona.reservas)} reservas. Nao podes reduzir abaixo disso.', 'erro')
            return redirect(url_for('editar_carona', carona_id=carona_id))

        data_raw = request.form.get('data', '')
        try:
            dt = datetime.strptime(data_raw, "%Y-%m-%d")
        except ValueError:
            flash('Data invalida.', 'erro')
            return redirect(url_for('editar_carona', carona_id=carona_id))

        carona.ponto_partida = request.form.get('origem', '').strip()
        carona.destino       = request.form.get('destino', '').strip()
        carona.data          = dt.strftime("%d/%m/%Y")
        carona.hora          = request.form.get('hora', '')
        carona.vagas_totais  = novas_vagas
        carona.tipo_prancha  = request.form.get('prancha', 'Qualquer')

        db.session.commit()
        flash('Barca actualizada!', 'sucesso')
        return redirect(url_for('minha_conta'))

    return render_template('editar_carona.html', carona=carona)

@app.route('/editar_perfil', methods=['POST'])
@login_required
def editar_perfil():
    if 'foto' in request.files:
        ficheiro = request.files['foto']
        if ficheiro and allowed_file(ficheiro.filename):
            filename = salvar_foto(ficheiro, current_user.id)
            current_user.foto_url = filename
            db.session.commit()
            flash('Foto actualizada com sucesso!', 'sucesso')
    return redirect(url_for('minha_conta'))

@app.route('/minha_conta')
@login_required
def minha_conta():
    minhas_caronas  = Carona.query.filter_by(motorista_id=current_user.id).all()
    minhas_reservas = Reserva.query.filter_by(usuario_id=current_user.id).all()
    avaliacoes_feitas = {
        a.carona_id for a in Avaliacao.query.filter_by(avaliador_id=current_user.id).all()
    }
    return render_template('minha_conta.html', caronas=minhas_caronas, reservas=minhas_reservas,
                           avaliacoes_feitas=avaliacoes_feitas)

@app.route('/avaliar/<int:carona_id>', methods=['GET', 'POST'])
@login_required
def avaliar(carona_id):
    carona = Carona.query.get_or_404(carona_id)

    if not carona.expirada:
        flash('So podes avaliar apos a carona ser realizada.', 'erro')
        return redirect(url_for('minha_conta'))

    if current_user.id == carona.motorista_id:
        pessoas_a_avaliar = [r.passageiro for r in carona.reservas]
        tipo = 'passageiro'
    else:
        reserva = Reserva.query.filter_by(
            carona_id=carona_id,
            usuario_id=current_user.id
        ).first()
        if not reserva:
            flash('Nao fizeste parte desta carona.', 'erro')
            return redirect(url_for('minha_conta'))
        pessoas_a_avaliar = [carona.motorista]
        tipo = 'motorista'

    ja_avaliou = Avaliacao.query.filter_by(
        avaliador_id=current_user.id,
        carona_id=carona_id
    ).first()
    if ja_avaliou:
        flash('Ja avaliaste esta carona.', 'erro')
        return redirect(url_for('minha_conta'))

    if request.method == 'POST':
        ja_avaliou_post = Avaliacao.query.filter_by(
            avaliador_id=current_user.id,
            carona_id=carona_id
        ).first()
        if not ja_avaliou_post:
            for pessoa in pessoas_a_avaliar:
                nota = max(1.0, min(5.0, float(request.form.get(f'nota_{pessoa.id}', 5))))
                comentario = request.form.get(f'comentario_{pessoa.id}', '').strip()[:300]
                avaliacao = Avaliacao(
                    avaliador_id=current_user.id,
                    avaliado_id=pessoa.id,
                    carona_id=carona_id,
                    nota=nota,
                    comentario=comentario,
                    tipo=tipo
                )
                db.session.add(avaliacao)
        db.session.commit()
        flash('Avaliacao enviada! Obrigado.', 'sucesso')
        return redirect(url_for('minha_conta'))

    return render_template('avaliar.html', carona=carona, pessoas=pessoas_a_avaliar, tipo=tipo)

@app.route('/apagar_conta', methods=['POST'])
@login_required
def apagar_conta():
    senha = request.form.get('senha', '')
    if not current_user.check_senha(senha):
        flash('Senha incorrecta. A conta não foi apagada.', 'erro')
        return redirect(url_for('minha_conta'))
    usuario = Usuario.query.get(current_user.id)
    logout_user()
    db.session.delete(usuario)
    db.session.commit()
    flash('A tua conta foi apagada.', 'sucesso')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)