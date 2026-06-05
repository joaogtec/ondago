from models import Surfista, CaronaSurf, Passageiro
from utils import salvar_dados, carregar_dados, ler_numero_inteiro

def main():
    lista_de_caronas = carregar_dados()
    while True:

        # Filtra caronas activas e expiradas
        activas   = [c for c in lista_de_caronas if not c.expirada]
        expiradas = [c for c in lista_de_caronas if c.expirada]

        # Se houve expiracao, guarda sem as antigas
        if len(activas) != len(lista_de_caronas):
            lista_de_caronas = activas
            salvar_dados(lista_de_caronas)

        print("\n--- MURAL DE CARONAS BOAT FRIENDS ---")
        if not activas:
            print("Nenhuma barca disponivel no momento.")
        else:
            for i, c in enumerate(activas, 1):
                status = "LOTADA" if c.lotado else f"{c.vagas_disponiveis}/{c.vagas_totais} vagas"
                print(f"{i}. {c.motorista.nome} [{c.motorista.avaliacao_display}] -> {c.destino} em {c.data} as {c.horario_queda} [{status}]")

        print("\n[1] Cadastrar Nova Barca")
        print("[2] Ver Detalhes / Passageiros")
        print("[3] Reservar Vaga")
        print("[4] Sair")

        opcao = input("\nEscolha uma opcao: ")

        if opcao == "1":
            nome    = input("Seu nome: ")
            nivel   = input("Seu nivel: ")
            tel     = input("WhatsApp: ")
            origem  = input("Partida: ")
            destino = input("Destino: ")
            vagas   = ler_numero_inteiro("Total de vagas: ")
            prancha = input("Prancha max: ")

            # Data e hora com validacao
            while True:
                data = input("Data (DD/MM/AAAA): ")
                try:
                    from datetime import datetime
                    datetime.strptime(data, "%d/%m/%Y")
                    break
                except:
                    print("Formato invalido. Use DD/MM/AAAA. Ex: 25/06/2025")

            while True:
                hora = input("Hora (HH:MM): ")
                try:
                    from datetime import datetime
                    datetime.strptime(hora, "%H:%M")
                    break
                except:
                    print("Formato invalido. Use HH:MM. Ex: 14:30")

            perfil = Surfista(nome, nivel, tel)
            nova   = CaronaSurf(perfil, origem, destino, vagas, prancha, hora, data)
            lista_de_caronas.append(nova)
            salvar_dados(lista_de_caronas)
            print("Barca lancada!")

        elif opcao == "2":
            if not activas:
                print("Nenhuma barca disponivel.")
                continue
            escolha = ler_numero_inteiro("Numero da barca: ")
            if 1 <= escolha <= len(activas):
                c = activas[escolha - 1]
                print(f"\nBarca para {c.destino}")
                print(f"Partida: {c.ponto_partida} em {c.data} as {c.horario_queda}")
                print(f"Motorista: {c.motorista.nome} | {c.motorista.telefone}")
                print(f"Prancha max: {c.tipo_prancha_max}")
                print(f"Vagas: {c.vagas_disponiveis}/{c.vagas_totais}")
                if c.passageiros:
                    print("Passageiros:")
                    for p in c.passageiros:
                        print(f"  - {p.nome} ({p.contacto})")
                else:
                    print("Passageiros: apenas o motorista por enquanto")
            else:
                print("Numero invalido.")

        elif opcao == "3":
            if not activas:
                print("Nenhuma barca disponivel.")
                continue
            escolha = ler_numero_inteiro("Numero da barca: ")
            if 1 <= escolha <= len(activas):
                c = activas[escolha - 1]
                if c.lotado:
                    print("Barca lotada!")
                else:
                    nome     = input("Seu nome: ")
                    contacto = input("Seu WhatsApp: ")
                    ja_reservou = any(p.contacto == contacto for p in c.passageiros)
                    if ja_reservou:
                        print("Este numero ja tem reserva nesta barca.")
                    else:
                        c.passageiros.append(Passageiro(nome=nome, contacto=contacto))
                        salvar_dados(lista_de_caronas)
                        print(f"Reserva feita! Fala com {c.motorista.nome}: {c.motorista.telefone}")
            else:
                print("Numero invalido.")

        elif opcao == "4":
            salvar_dados(lista_de_caronas)
            print("Ate a proxima!")
            break

        else:
            print("Opcao invalida.")

if __name__ == "__main__":
    main()