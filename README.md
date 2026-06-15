# 🌊 OndaGo

**Plataforma de caronas para quem vive o mar.**

---

## A história por trás do app

Cresci no José Walter, em Fortaleza. Surfista desde jovem, sem carro, sem praia perto.

Todo fim de semana era a mesma história: prancha debaixo do braço, ônibus lotado, sol na cabeça. Nunca desisti de surfar por causa disso — mas aquela dificuldade ficou guardada.

Quando comecei a surfar, uma das coisas que mais admirava era a comunidade. Amizades verdadeiras, estímulos para melhorar, dicas de spots, histórias. O surf sempre teve uma essência diferente — um lugar de pertencimento onde você chegava estranho e saía com amigos.

Com o tempo, senti que a tecnologia foi afastando as pessoas dessa essência. Todo mundo no telefone, menos conversa no lineup.

Hoje moro em Lagos, Portugal, dou aula de surf na Salty Wave e estou no primeiro semestre de ADS. Aqui o problema é outro: Uber não aceita prancha. A dificuldade mudou de continente mas não desapareceu.

Foi aí que nasceu o OndaGo. Não pensei só na carona — pensei na vontade de recriar aquela comunidade. Um app onde você resolve o transporte e no caminho faz novas amizades, descobre novos spots, volta a sentir que o surf é mais do que um esporte. É um lugar de pertencimento.

Um app que eu mesmo precisaria ter tido — em Fortaleza aos 18 anos e em Lagos hoje.

---

## O que é o OndaGo

O OndaGo conecta surfistas que precisam de carona com quem tem espaço no carro e vai para o mesmo spot.

- 📋 Publica a tua barca com destino, data, hora e vagas
- 🔍 Vê as barcas disponíveis no mural
- ✅ Reserva uma vaga e cancela se precisares
- ⭐ Avalia o motorista ou os passageiros após a carona
- 👤 Perfil com foto, nível de surf e histórico de viagens
- ⏱️ Caronas expiradas saem automaticamente do mural

---

## Funcionalidades

- Login e registo com password encriptada (Werkzeug)
- Foto de perfil com upload e redimensionamento automático
- Sistema de avaliações mútuas — motorista avalia passageiro e vice-versa
- Cancelar reserva (enquanto a carona não expirou)
- Editar barca (destino, data, hora, vagas, tipo de prancha)
- Dark mode com preferência guardada no browser
- Design mobile-first responsivo
- Rate limiting contra ataques de força bruta (Flask-Limiter)
- Variáveis de ambiente para dados sensíveis (.env)

---

## Tecnologias

- **Python 3** — lógica e backend
- **Flask** — servidor web
- **SQLite + SQLAlchemy** — base de dados relacional
- **Flask-Login** — gestão de sessões autenticadas
- **Werkzeug** — hash seguro de passwords
- **Pillow** — processamento de imagens de perfil
- **Flask-Limiter** — rate limiting por IP
- **python-dotenv** — variáveis de ambiente
- **HTML/CSS** — interface

---

## Como rodar localmente

```bash
# Clonar o repositório
git clone https://github.com/joaogtec/ondago.git
cd ondago

# Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Instalar dependências
pip install flask flask-sqlalchemy flask-login werkzeug pillow python-dotenv flask-limiter

# Criar o ficheiro .env
echo SECRET_KEY=coloca_aqui_uma_chave_aleatoria > .env

# Rodar o app
python app.py
```

Abre o browser em `http://127.0.0.1:5000`

---

## Estrutura do projeto

```
ondago/
├── app.py
├── models.py
├── .env
├── static/uploads/
└── templates/
    ├── base.html
    ├── index.html
    ├── nova_carona.html
    ├── reservar.html
    ├── login.html
    ├── registro.html
    ├── minha_conta.html
    ├── avaliar.html
    └── editar_carona.html
```

---

## Próximos passos

- [ ] Notificações via WhatsApp
- [ ] Deploy online
- [ ] Expansão para outros desportos de natureza
- [ ] Sistema de comunidade — spots favoritos, conquistas, perfis

---

## Sobre o projeto

Desenvolvido por João Gabriel — instrutor de surf, estudante de ADS e empreendedor.

Começou como ideia de projeto em paralelo a faculdade e Virou algo maior.


