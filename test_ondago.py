import pytest
from datetime import datetime, timedelta
from sqlalchemy.pool import StaticPool

from app import app as flask_app, limiter, mail
from models import db, Usuario, Carona, Reserva


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def app():
    """BD SQLite em memoria, isolada por teste.
    StaticPool garante que todas as ligacoes (pedidos HTTP, queries de
    asserts) partilham a mesma ligacao em memoria, em vez de cada uma
    abrir a sua propria BD vazia.
    O rate limiter e o Flask-Mail sao inicializados uma unica vez quando
    app.py e importado, por isso 'TESTING'/'MAIL_SUPPRESS_SEND' no
    app.config (definidos depois desse momento) nao bastam — e preciso
    desligar os respectivos objectos de extensao directamente."""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'poolclass': StaticPool,
            'connect_args': {'check_same_thread': False},
        },
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-key-pytest',
        'MAIL_SUPPRESS_SEND': True,
    })
    limiter.enabled = False
    flask_app.extensions['mail'].suppress = True

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Helpers ───────────────────────────────────────────────────────────────────

def amanha():
    return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


def registar(client, nome='Ana Surf', email='ana@teste.com',
             telefone='910000001', nivel='Iniciante', senha='senha1234'):
    """So regista — a conta fica por verificar e sem sessao iniciada."""
    return client.post('/registro', data={
        'nome': nome, 'email': email, 'telefone': telefone,
        'nivel': nivel, 'senha': senha,
    }, follow_redirects=True)


def verificar_email_de(client, email):
    """Simula o clique no link do email: visita /verificar-email/<token>."""
    usuario = Usuario.query.filter_by(email=email).first()
    return client.get(f'/verificar-email/{usuario.token_verificacao}', follow_redirects=True)


def registar_e_verificar(client, nome='Ana Surf', email='ana@teste.com',
                          telefone='910000001', nivel='Iniciante', senha='senha1234'):
    """Regista e confirma o email — fica com sessao iniciada, como antes
    de existir a verificacao de email."""
    registar(client, nome, email, telefone, nivel, senha)
    return verificar_email_de(client, email)


def fazer_login(client, email, senha):
    return client.post('/login', data={'email': email, 'senha': senha},
                       follow_redirects=True)


def logout(client):
    client.get('/logout', follow_redirects=True)


def criar_barca(client, origem='Lagos', destino='Cordoama',
                hora='08:00', vagas=3, prancha='Qualquer', data=None):
    return client.post('/nova', data={
        'origem': origem, 'destino': destino,
        'data': data or amanha(), 'hora': hora,
        'vagas': vagas, 'prancha': prancha,
    }, follow_redirects=True)


# ── Testes ────────────────────────────────────────────────────────────────────

def test_registo_utilizador_novo(client):
    """Registo cria o utilizador na BD, por verificar e sem sessao iniciada."""
    r = registar(client)
    assert r.status_code == 200
    assert 'Verifica o teu email' in r.data.decode('utf-8')

    usuario = Usuario.query.filter_by(email='ana@teste.com').first()
    assert usuario is not None
    assert usuario.email_verificado is False
    assert usuario.token_verificacao is not None


def test_verificar_email_com_token_valido(client):
    """Visitar o link de verificacao confirma o email e inicia sessao."""
    registar(client)
    r = verificar_email_de(client, 'ana@teste.com')
    assert r.status_code == 200
    assert 'Bem-vindo' in r.data.decode('utf-8')

    usuario = Usuario.query.filter_by(email='ana@teste.com').first()
    assert usuario.email_verificado is True
    assert usuario.token_verificacao is None


def test_login_sem_verificar_email(client):
    """Login com credenciais correctas mas email nao verificado e bloqueado."""
    registar(client)
    r = fazer_login(client, 'ana@teste.com', 'senha1234')
    assert r.status_code == 200
    assert 'Verifica o teu email primeiro' in r.data.decode('utf-8')


def test_login_credenciais_correctas(client):
    """Login correcto (apos verificar o email) redireciona para o mural."""
    registar_e_verificar(client)
    logout(client)
    r = fazer_login(client, 'ana@teste.com', 'senha1234')
    assert r.status_code == 200
    assert 'Caronas para a queda' in r.data.decode('utf-8')


def test_login_credenciais_erradas(client):
    """Login falhado devolve HTTP 200 na pagina de login com mensagem de erro."""
    registar_e_verificar(client)
    logout(client)
    r = client.post('/login', data={
        'email': 'ana@teste.com',
        'senha': 'senha_errada',
    }, follow_redirects=False)
    assert r.status_code == 200
    assert 'incorretos' in r.data.decode('utf-8')


def test_criar_barca_data_futura(client):
    """Barca normal e criada com saida_imediata=False e dados correctos."""
    registar_e_verificar(client)
    criar_barca(client)
    carona = Carona.query.first()
    assert carona is not None
    assert carona.saida_imediata is False
    assert carona.destino == 'Cordoama'


def test_criar_barca_saida_imediata(client):
    """Saida Imediata cria barca sem data/hora no formulario e marca o campo."""
    registar_e_verificar(client)
    client.post('/nova', data={
        'origem': 'Lagos', 'destino': 'Arrifana',
        'vagas': 2, 'prancha': 'Shortboard',
        'saida_imediata': 'on',
    }, follow_redirects=True)
    carona = Carona.query.first()
    assert carona is not None
    assert carona.saida_imediata is True
    assert carona.hora != ''


def test_reservar_vaga(client):
    """Passageiro consegue reservar uma vaga numa barca de outro utilizador."""
    registar_e_verificar(client, nome='Motorista', email='motor@teste.com', senha='senha1234')
    criar_barca(client)
    logout(client)

    registar_e_verificar(client, nome='Passageiro', email='pass@teste.com', senha='senha1234')
    carona_id = Carona.query.first().id

    r = client.post(f'/reservar/{carona_id}', follow_redirects=True)
    assert r.status_code == 200
    assert Reserva.query.count() == 1


def test_reservar_propria_barca(client):
    """Motorista nao pode reservar a sua propria barca — nenhuma reserva criada."""
    registar_e_verificar(client)
    criar_barca(client)
    carona_id = Carona.query.first().id

    client.post(f'/reservar/{carona_id}', follow_redirects=True)
    assert Reserva.query.count() == 0


def test_reservar_mesma_barca_duas_vezes(client):
    """Segunda tentativa de reserva na mesma barca e ignorada."""
    registar_e_verificar(client, nome='Motorista', email='motor@teste.com', senha='senha1234')
    criar_barca(client)
    logout(client)

    registar_e_verificar(client, nome='Passageiro', email='pass@teste.com', senha='senha1234')
    carona_id = Carona.query.first().id

    client.post(f'/reservar/{carona_id}', follow_redirects=True)
    client.post(f'/reservar/{carona_id}', follow_redirects=True)
    assert Reserva.query.count() == 1


def test_cancelar_reserva(client):
    """Passageiro consegue cancelar a sua reserva — tabela fica vazia."""
    registar_e_verificar(client, nome='Motorista', email='motor@teste.com', senha='senha1234')
    criar_barca(client)
    logout(client)

    registar_e_verificar(client, nome='Passageiro', email='pass@teste.com', senha='senha1234')
    carona_id = Carona.query.first().id

    client.post(f'/reservar/{carona_id}', follow_redirects=True)
    reserva_id = Reserva.query.first().id

    r = client.post(f'/cancelar_reserva/{reserva_id}', follow_redirects=True)
    assert r.status_code == 200
    assert Reserva.query.count() == 0


def test_minha_conta_sem_login(client):
    """Aceder a /minha_conta sem sessao redireciona para /login."""
    r = client.get('/minha_conta', follow_redirects=False)
    assert r.status_code == 302
    assert '/login' in r.headers['Location']
