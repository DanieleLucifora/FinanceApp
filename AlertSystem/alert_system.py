import mysql.connector
import json
from confluent_kafka import Consumer, Producer

consumer_config = {
    'bootstrap.servers': 'kafka-broker:9092',
    'group.id': 'group2',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
}
producer_config = {'bootstrap.servers': 'kafka-broker:9092'}

consumer = Consumer(consumer_config)
producer = Producer(producer_config)
topic_consumer = 'to-alert-system'
topic_producer = 'to-notifier'
consumer.subscribe([topic_consumer])

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

def soglia_superata():
    try:
        connection = connessione_db()
        cursor = connection.cursor()
        query = "SELECT email, ticker, high_value, low_value FROM utenti"
        cursor.execute(query)
        righe = cursor.fetchall()
        for email, ticker, high_value, low_value in righe:
            query = "SELECT valore FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(query, (email,))
            valore = cursor.fetchall()
            if high_value and valore[0][0] >= high_value:
                return (email, ticker, "Soglia superiore raggiunta")
            elif low_value and valore[0][0] <= low_value:
                return (email, ticker, "Soglia inferiore raggiunta")
            else:
                return ("", "", "")
    except mysql.connector.Error as errore:
        print(f"Errore durante il recupero dal database: {errore}")
        return ("", "", "")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

def produce_sync(value):
    global topic_producer
    try:
        producer.produce(topic_producer, value)
        producer.flush()
        print(f"Synchronously produced message to {topic_producer}: {value}")
    except Exception as e:
        print(f"Failed to produce message: {e}")

while True:
    messaggio = consumer.poll(3.0)
    if messaggio is None:
        continue
    if messaggio.error():
        print(f"Errore: {messaggio.error()}")
        continue

    email, ticker, condizione = soglia_superata()

    if email and ticker and condizione:
        dati = {
            "email": email,
            "ticker": ticker,
            "condizione": condizione
        }
        produce_sync(json.dumps(dati))