from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    telefone   = db.Column(db.String(20), nullable=False)
    nivel      = db.Column(db.String(30), default='Iniciante')
    foto_url   = db.Column(db.String(300), default='')
    senha_hash = db.Column(db.String(256), nullable=False)
    criado_em  = db.Column(db.DateTime, default=datetime.utcnow)

    email_verificado   = db.Column(db.Boolean, default=False)
    token_verificacao  = db.Column(db.String(100), nullable=True)

    caronas    = db.relationship('Carona', backref='motorista', lazy=True)
    reservas   = db.relationship('Reserva', backref='passageiro', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def media_avaliacao(self):
        from sqlalchemy import func
        result = db.session.query(func.avg(Avaliacao.nota)).filter_by(avaliado_id=self.id).scalar()
        return round(result, 1) if result else None

class Carona(db.Model):
    __tablename__ = 'caronas'
    id            = db.Column(db.Integer, primary_key=True)
    motorista_id  = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ponto_partida = db.Column(db.String(100), nullable=False)
    destino       = db.Column(db.String(100), nullable=False)
    data          = db.Column(db.String(10), nullable=False)
    hora          = db.Column(db.String(5), nullable=False)
    vagas_totais  = db.Column(db.Integer, nullable=False)
    tipo_prancha   = db.Column(db.String(30), default='Qualquer')
    saida_imediata = db.Column(db.Boolean, default=False)
    criado_em      = db.Column(db.DateTime, default=datetime.utcnow)

    reservas      = db.relationship('Reserva', backref='carona', lazy=True)

    @property
    def vagas_disponiveis(self):
        return self.vagas_totais - len(self.reservas)

    @property
    def lotado(self):
        return self.vagas_disponiveis == 0

    @property
    def expirada(self):
        try:
            dt = datetime.strptime(f"{self.data} {self.hora}", "%d/%m/%Y %H:%M")
            return datetime.now() > dt
        except:
            return False

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id         = db.Column(db.Integer, primary_key=True)
    carona_id  = db.Column(db.Integer, db.ForeignKey('caronas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    criado_em  = db.Column(db.DateTime, default=datetime.utcnow)

class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'
    __table_args__ = (UniqueConstraint('avaliador_id', 'avaliado_id', 'carona_id', name='uq_avaliacao'),)
    id           = db.Column(db.Integer, primary_key=True)
    avaliador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    avaliado_id  = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    carona_id    = db.Column(db.Integer, db.ForeignKey('caronas.id'), nullable=False)
    nota         = db.Column(db.Float, nullable=False)
    comentario   = db.Column(db.String(300), default='')
    tipo         = db.Column(db.String(20), nullable=False)
    criado_em    = db.Column(db.DateTime, default=datetime.utcnow)
    avaliador    = db.relationship('Usuario', foreign_keys=[avaliador_id])
    avaliado     = db.relationship('Usuario', foreign_keys=[avaliado_id])
