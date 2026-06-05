from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Passageiro:
    nome: str
    contacto: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Surfista:
    nome: str
    nivel: str
    telefone: str
    avaliacao: float = 0.0
    soma_notas: float = 0.0
    qtd_avaliacoes: int = 0

    @property
    def avaliacao_display(self):
        if self.qtd_avaliacoes == 0:
            return "Novo"
        return f"estrela {self.avaliacao:.1f}"

@dataclass
class CaronaSurf:
    motorista: Surfista
    ponto_partida: str
    destino: str
    vagas_totais: int
    tipo_prancha_max: str
    horario_queda: str
    data: str = ""
    passageiros: list = field(default_factory=list)

    @property
    def vagas_disponiveis(self):
        return self.vagas_totais - len(self.passageiros)

    @property
    def lotado(self):
        return self.vagas_disponiveis == 0

    @property
    def expirada(self):
        try:
            dt = datetime.strptime(f"{self.data} {self.horario_queda}", "%d/%m/%Y %H:%M")
            return datetime.now() > dt
        except:
            return False