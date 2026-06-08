from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Carona, Reserva
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ondago_secret_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ondago.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    return render_template('minha_conta.html', caronas=minhas_caronas, reservas=minhas_reservas)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)