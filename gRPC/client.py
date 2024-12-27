import logging
import grpc
import finance_app_pb2
import finance_app_pb2_grpc

def ottieni_soglia():
    print("Inserisci i valori di soglia per la notifica: lasciare vuoto per non impostare la soglia.")

    high_value = input("Valore massimo: ")
    try:
        high_value = float(high_value)
    except ValueError:
        print("Soglia non impostata.")
        high_value = 0.0

    low_value = input("Valore minimo: ")
    try:
        low_value = float(low_value)
    except ValueError:
        print("Soglia non impostata.")
        low_value = 0.0

    return high_value, low_value

def registra_utente(stub):
    try:
        email = input("Inserisci email: ")
        ticker = input("Inserisci ticker: ")
        high_value, low_value = ottieni_soglia()
        risposta = stub.RegistraUtente(finance_app_pb2.DatiUtente(email = email, ticker = ticker, high_value = high_value, low_value = low_value), timeout = 5)
        print("Conferma registrazione: " + str(risposta.conferma) + ". " + risposta.messaggio)
    except grpc.RpcError as error:
        print(error)

def aggiorna_utente(stub):
    try:
        email = input("Inserisci email: ")
        ticker = input("Inserisci ticker: ")
        high_value, low_value = ottieni_soglia()
        risposta = stub.AggiornaUtente(finance_app_pb2.DatiUtente(email = email, ticker = ticker, high_value = high_value, low_value = low_value), timeout = 5)
        print("Conferma aggiornamento: " + str(risposta.conferma) + ". " + risposta.messaggio)
    except grpc.RpcError as error:
        print(error)

def cancella_utente(stub):
    try:
        email = input("Inserisci email: ")
        risposta = stub.CancellaUtente(finance_app_pb2.Email(email = email), timeout = 5)
        print("Conferma eliminazione: " + str(risposta.conferma) + ". " + risposta.messaggio)   
    except grpc.RpcError as error:
        print(error)

def recupera_valore(stub):
    try:
        email = input("Inserisci email: ")
        risposta = stub.RecuperaValore(finance_app_pb2.Email(email = email), timeout = 5)
        print(f"Valore ottenuto: {round(risposta.valore, 2)}")
    except grpc.RpcError as error:
        print(error)

def calcola_media_valori(stub):
    try:
        email = input("Inserisci email: ")
        numeroDati = input("Inserisci il numero di dati: ")
        try:
            numeroDati = int(numeroDati)
        except ValueError:
            print("Valore non valido.")
            numeroDati = 1
        risposta = stub.CalcolaMediaValori(finance_app_pb2.DatiMediaValori(email = email, numeroDati = numeroDati), timeout = 5)
        print(f"Media valori ottenuta: {round(risposta.valore, 2)}")
    except grpc.RpcError as error:
        print(error)

def visualizza_menu():
    print("\nScegli un'opzione:")
    print("1. Registra utente")
    print("2. Aggiorna utente")
    print("3. Cancella utente")
    print("4. Recupera valore")
    print("5. Recupera media valori")
    print("0. Esci")

def run():
    with grpc.insecure_channel('localhost:50051') as channel:

        stub_utente = finance_app_pb2_grpc.ServizioUtenteStub(channel)
        stub_stock = finance_app_pb2_grpc.ServizioStockStub(channel)

        while True:
            visualizza_menu()
            scelta = input("Inserisci il numero della funzione: ")

            if scelta == '1':
                registra_utente(stub_utente)
            elif scelta == '2':
                aggiorna_utente(stub_utente)
            elif scelta == '3':
                cancella_utente(stub_utente)
            elif scelta == '4':
                recupera_valore(stub_stock)
            elif scelta == '5':
                calcola_media_valori(stub_stock)
            elif scelta == '0':
                print("Uscita dal programma.")
                break
            else:
                print("Scelta non valida, riprova.")

if __name__ == '__main__':
    logging.basicConfig()
    run()
