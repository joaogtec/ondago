from flask import Flask, render_template, request, redirect, url_for
from models import Surfista, CaronaSurf, Passageiro
from utils import salvar_dados, carregar_dados
from datetime import datetime

app = Flask(__name__)
app.jinja_env.filters['enumerate'] = enumerate
@app.route('/')
def index():
    lista = carregar_dados()
    activas = [c for c in lista if not c.expirada]
    return render_template('index.html', caronas=activas)

@app.route('/nova', methods=['GET', 'POST'])
def nova_carona():
    if request.method == 'POST':
        nome    = request.form['nome']
        nivel   = request.form['nivel']
        tel     = request.form['telefone']
        origem  = request.form['origem']
        destino = request.form['destino']
        vagas   = int(request.form['vagas'])
        prancha = request.form['prancha']
        data    = request.form['data']
        hora    = request.form['hora']

        # Converte data de YYYY-MM-DD para DD/MM/YYYY
        dt = datetime.strptime(data, "%Y-%m-%d")
        data_formatada = dt.strftime("%d/%m/%Y")

        perfil = Surfista(nome, nivel, tel)
        nova   = CaronaSurf(perfil, origem, destino, vagas, prancha, hora, data_formatada)

        lista = carregar_dados()
        lista.append(nova)
        salvar_dados(lista)
        return redirect(url_for('index'))

    return render_template('nova_carona.html')

@app.route('/reservar/<int:idx>', methods=['GET', 'POST'])
def reservar(idx):
    lista = carregar_dados()
    activas = [c for c in lista if not c.expirada]

    if idx >= len(activas):
        return redirect(url_for('index'))

    carona = activas[idx]

    if request.method == 'POST':
        nome     = request.form['nome']
        contacto = request.form['contacto']
        ja_reservou = any(p.contacto == contacto for p in carona.passageiros)
        if not ja_reservou and not carona.lotado:
            carona.passageiros.append(Passageiro(nome=nome, contacto=contacto))
            salvar_dados(lista)
        return redirect(url_for('index'))

    return render_template('reservar.html', carona=carona, idx=idx)

if __name__ == '__main__':
    app.run(debug=True)