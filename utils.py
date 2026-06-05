import json
import os
import shutil
from models import Surfista, CaronaSurf, Passageiro

def salvar_dados(lista_caronas, arquivo='caronas.json'):
    temp_arquivo = arquivo + '.tmp'
    try:
        dados = []
        for c in lista_caronas:
            dados.append({
                'motorista': {
                    'nome': c.motorista.nome,
                    'nivel': c.motorista.nivel,
                    'telefone': c.motorista.telefone,
                    'avaliacao': c.motorista.avaliacao,
                    'soma_notas': c.motorista.soma_notas,
                    'qtd_avaliacoes': c.motorista.qtd_avaliacoes
                },
                'ponto_partida': c.ponto_partida,
                'destino': c.destino,
                'vagas_totais': c.vagas_totais,
                'tipo_prancha_max': c.tipo_prancha_max,
                'horario_queda': c.horario_queda,
                'data': c.data,
                'passageiros': [
                    {
                        'nome': p.nome,
                        'contacto': p.contacto,
                        'timestamp': p.timestamp
                    }
                    for p in c.passageiros
                ]
            })
        with open(temp_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        shutil.move(temp_arquivo, arquivo)
    except Exception as e:
        if os.path.exists(temp_arquivo):
            os.remove(temp_arquivo)
        print(f"Erro ao salvar: {e}")

def carregar_dados(arquivo='caronas.json'):
    if not os.path.exists(arquivo):
        return []
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            lista = []
            for d in dados:
                m = d['motorista']
                motorista = Surfista(
                    m['nome'], m['nivel'], m['telefone'],
                    m['avaliacao'], m['soma_notas'], m['qtd_avaliacoes']
                )
                passageiros = [
                    Passageiro(
                        nome=p['nome'],
                        contacto=p['contacto'],
                        timestamp=p['timestamp']
                    )
                    for p in d.get('passageiros', [])
                ]
                carona = CaronaSurf(
                    motorista,
                    d['ponto_partida'],
                    d['destino'],
                    d['vagas_totais'],
                    d['tipo_prancha_max'],
                    d['horario_queda'],
                    d.get('data', ''),
                    passageiros
                )
                lista.append(carona)
            return lista
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        return []

def ler_numero_inteiro(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um numero inteiro valido.")