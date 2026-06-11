"""
Inserts two test users + an expired carona with a reservation for rating system testing.
Run from the project root: python seed_test.py
"""
from app import app
from models import db, Usuario, Carona, Reserva

MOTORISTA_EMAIL   = "motorista@teste.com"
PASSAGEIRO_EMAIL  = "passageiro@teste.com"
SENHA             = "teste123"

with app.app_context():
    # --- users ---
    motorista = Usuario.query.filter_by(email=MOTORISTA_EMAIL).first()
    if not motorista:
        motorista = Usuario(nome="Ana Motorista", email=MOTORISTA_EMAIL,
                            telefone="910000001", nivel="Avançado")
        motorista.set_senha(SENHA)
        db.session.add(motorista)
        db.session.flush()
        print(f"Criado motorista  : {motorista.nome} (id={motorista.id})")
    else:
        print(f"Motorista já existe: {motorista.nome} (id={motorista.id})")

    passageiro = Usuario.query.filter_by(email=PASSAGEIRO_EMAIL).first()
    if not passageiro:
        passageiro = Usuario(nome="Bruno Passageiro", email=PASSAGEIRO_EMAIL,
                             telefone="910000002", nivel="Iniciante")
        passageiro.set_senha(SENHA)
        db.session.add(passageiro)
        db.session.flush()
        print(f"Criado passageiro : {passageiro.nome} (id={passageiro.id})")
    else:
        print(f"Passageiro já existe: {passageiro.nome} (id={passageiro.id})")

    # --- expired carona (yesterday) ---
    carona = Carona(
        motorista_id  = motorista.id,
        ponto_partida = "Lisboa",
        destino       = "Peniche",
        data          = "09/06/2026",   # yesterday
        hora          = "06:00",
        vagas_totais  = 3,
        tipo_prancha  = "Shortboard",
    )
    db.session.add(carona)
    db.session.flush()
    print(f"Criada carona     : {carona.ponto_partida} -> {carona.destino} "
          f"({carona.data} {carona.hora}) expirada={carona.expirada}")

    # --- reservation ---
    reserva = Reserva(carona_id=carona.id, usuario_id=passageiro.id)
    db.session.add(reserva)

    db.session.commit()
    print("\nDados inseridos com sucesso.")
    print("-" * 40)
    print(f"Motorista  : {MOTORISTA_EMAIL}  / {SENHA}")
    print(f"Passageiro : {PASSAGEIRO_EMAIL} / {SENHA}")
    print("-" * 40)
    print("1. Login como passageiro -> Minha Conta -> deves ver 'Avaliar motorista'")
    print("2. Login como motorista  -> Minha Conta -> deves ver 'Avaliar Bruno'")
