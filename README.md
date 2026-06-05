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
- ✅ Reserva uma vaga com o teu nome e WhatsApp
- ⏱️ Caronas expiradas saem automaticamente do mural

---

## Tecnologias

- **Python 3** — lógica e backend
- **Flask** — servidor web
- **HTML/CSS** — interface
- **JSON** — persistência de dados
- **Dataclasses** — modelagem de dados

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
pip install flask

# Rodar o app
python app.py
```

Abre o browser em `http://127.0.0.1:5000`

---

## Estrutura do projeto

```
ondago/
├── app.py              # Rotas Flask
├── models.py           # Modelos de dados
├── utils.py            # Leitura e escrita JSON
├── caronas.json        # Base de dados local
└── templates/
    ├── index.html      # Mural de caronas
    ├── nova_carona.html # Publicar barca
    └── reservar.html   # Reservar vaga
```

---

## Próximos passos

- [ ] Migrar para SQLite
- [ ] Sistema de login
- [ ] Cancelar reserva
- [ ] Notificação via WhatsApp
- [ ] Expandir para outros desportos de natureza
- [ ] Criar comunidade dentro do app — perfis, conquistas, spots favoritos

---

## Sobre o projeto

Desenvolvido por João Gabriel — instrutor de surf, estudante de ADS e empreendedor.

Começou como projeto da faculdade. Virou algo maior.

> *"Nunca deixei de surfar por falta de carro. Mas o que eu mais sinto falta não é só da onda — é da comunidade que o surf sempre teve."*