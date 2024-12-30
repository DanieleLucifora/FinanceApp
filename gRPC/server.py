import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../CQRS')))

import grpc
from command_service import CommandService
import finance_app_pb2_grpc
from concurrent import futures
from query_service import QueryService
import sys
import os
import prometheus_client
import socket
import time

HOSTNAME = socket.gethostname()

ContatoreRegistrazioni = prometheus_client.Counter(
    'Numero_Registrazioni',
    'Numero di chiamate alla funzione di registrazione del server', #non necessariamente registrazioni effettive
    ['hostname', 'app'] # labels
)

GaugeTempoRecupero = prometheus_client.Gauge(
    'Tempo_Recupero_Valore', 
    'Tempo di esecuzione della funzione di recupero ultimo valore del Query Service', 
    ['hostname', 'app']
)


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../CQRS')))

class ComandoRegistraUtente:
    def __init__(self, email, ticker, high_value, low_value):
        self.email = email
        self.ticker = ticker
        self.high_value = high_value
        self.low_value = low_value

class ComandoAggiornaUtente:
    def __init__(self, email, ticker, high_value, low_value):
        self.email = email
        self.ticker = ticker
        self.high_value = high_value
        self.low_value = low_value

class ComandoCancellaUtente:
    def __init__(self, email):
        self.email = email

class ServizioUtente(finance_app_pb2_grpc.ServizioUtenteServicer):

    def RegistraUtente(request, context):
        print("Aumento il contatore Numero_Registrazioni per prometheus.")
        ContatoreRegistrazioni.labels(hostname=HOSTNAME, app="Server").inc()

        comando = ComandoRegistraUtente(request.email, request.ticker, request.high_value, request.low_value)
        return CommandService.handle_registrazione_utente(comando)

    def AggiornaUtente(request, context):
        comando = ComandoAggiornaUtente(request.email, request.ticker, request.high_value, request.low_value)
        return CommandService.handle_aggiornamento_utente(comando)
    
    def CancellaUtente(request, context):
        comando = ComandoCancellaUtente(request.email)
        return CommandService.handle_cancellazione_utente(comando)

class ServizioStock(finance_app_pb2_grpc.ServizioStockServicer):

    def RecuperaValore(request, context):
        tempo_inizio = time.time()
        Valore = QueryService.get_ultimo_valore(request)
        tempo_fine = time.time()
        print("Produco la metrica Tempo_Recupero_Valore per prometheus")
        GaugeTempoRecupero.labels(hostname=HOSTNAME, app="Server").set(tempo_fine - tempo_inizio)
        return Valore   #messaggio Valore del .proto

    def CalcolaMediaValori(request, context):
        return QueryService.get_media_valori(request)

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    finance_app_pb2_grpc.add_ServizioUtenteServicer_to_server(ServizioUtente, server)
    finance_app_pb2_grpc.add_ServizioStockServicer_to_server(ServizioStock, server)
    print("Servizio Utente avviato.")
    print("Servizio Stock avviato.")

    print("Condivido le metriche prometheus sulla porta 9200.")
    prometheus_client.start_http_server(9200)

    print(f"Server in ascolto sulla porta {port}...")
    server.add_insecure_port('[::]:' + port)
    server.start()
    server.wait_for_termination()
    
if __name__ == '__main__':
    serve()