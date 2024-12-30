import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../CircuitBreaker')))

import time
import mysql.connector
from confluent_kafka import Producer
import yfinance as yf
import prometheus_client
import socket
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../CircuitBreaker')))

from circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
                
circuit_breaker = CircuitBreaker()

producer_config = {
    'bootstrap.servers': 'kafka-broker:9092',
    'acks': 'all',
    'batch.size': 500,  # un batch è una collezione di messaggi. batch size dice quanti byte può essere un batch
    'max.in.flight.requests.per.connection': 1,
    'retries': 3
}

producer = Producer(producer_config)
topic = 'to-alert-system'

HOSTNAME = socket.gethostname()

ContatoreIterazioni = prometheus_client.Counter(
    'Iterazioni_DC',
    'Numero di iterazioni del data collector',
    ['hostname', 'app'] # labels
)

GaugeTempoRisposta = prometheus_client.Gauge(
    'Tempo_Risposta_YF', 
    'Tempo di risposta di YahooFinance', 
    ['hostname', 'app']
)

def connessione_db():
    try:
        connection = mysql.connector.connect(
            host = 'mysqldb', #TODO: mysqldb quando spostiamo su docker, localhost in locale
            user = 'server',
            password = '1234',
            database = 'finance_app'
        )
        return connection
    except mysql.connector.Error:
        print("Errore nella connessione al database.")
        return None
    
def recupera_righe_utenti():   #database utenti: | email | ticker |
    try:
        connection = connessione_db()
        cursor = connection.cursor()
        query = "SELECT email, ticker FROM utenti;"
        cursor.execute(query)
        righe = cursor.fetchall()
        return righe
    except mysql.connector.Error as errore:
        print(f"Errore durante il recupero dal database: {errore}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
                
def recupera_ultimo_valore(ticker):
    try:
        tempo_inizio = time.time()
        azione = yf.Ticker(ticker)
        tempo_fine = time.time()
        print("Produco la metrica Tempo_Risposta_YF per prometheus")
        GaugeTempoRisposta.labels(hostname=HOSTNAME, app="Data Collector").set(tempo_fine - tempo_inizio)

        dati_giornalieri = azione.history(period="1d", interval="1m") # dataframe con ingressi distanziati di 1m
        if not dati_giornalieri.empty:
            ultimo_valore = dati_giornalieri['Close'].iloc[-1] # valore di chiusura
            return ultimo_valore
        else:
            print(f"Nessun dato trovato per {ticker}")
            return None
    except Exception as e:
        print(f"Errore durante il recupero del ticker {ticker}: {e}")
    
def salva_stock_data(email, ticker, valore):
    try:
        connection = connessione_db()
        cursor = connection.cursor()
        query = """
                INSERT INTO data (email, ticker, valore, timestamp)
                VALUES (%s, %s, %s, NOW());
                """
        cursor.execute(query, (email, ticker, valore))
        connection.commit()
        print("Dati salvati correttamente.")
    except mysql.connector.Error as errore:
        print(f"Errore durante il salvataggio dei dati: {errore}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
                connection.close()

def delivery_report(err, msg):
    """Callback to report the result of message delivery."""
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def avvia_data_collector():
        
    print("Data collector avviato.")

    print("Condivido le metriche prometheus sulla porta 9100.")
    prometheus_client.start_http_server(9100)

    while True:
        try:
            righe = recupera_righe_utenti()
            for email, ticker in righe:
                print(f"Recupero dati per {ticker} associato a {email}")
                try:
                    ultimo_valore = circuit_breaker.call(recupera_ultimo_valore, ticker)  # Chiamata protetta dal CB
                    salva_stock_data(email, ticker, ultimo_valore)
                    message = "Database aggiornato."
                    producer.produce(topic, message, callback = delivery_report)
                    producer.flush()
                    print(f"Produced {message}")
                except CircuitBreakerOpenException:
                    print("Errore: il circuito è aperto.")
                except Exception as e:
                    print(f"Errore per {ticker} (utente: {email}): {e}")
        except:
            print("Errore durante il recupero degli utenti nel database.")

        print("Aumento il contatore Iterazioni_DC Prometheus.")
        ContatoreIterazioni.labels(hostname=HOSTNAME, app="Data Collector").inc()

        print("Attendo un minuto prima del prossimo ciclo...")
        time.sleep(60)
        
if __name__ == "__main__":  #per avviare "data_collector.py"
    avvia_data_collector()