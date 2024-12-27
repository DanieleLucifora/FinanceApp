import smtplib
import json
from confluent_kafka import Consumer
from email.message import EmailMessage

consumer_config = {
    'bootstrap.servers': 'kafka-broker:9092',
    'group.id': 'group1',  #gruppo di competing consumers
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

consumer = Consumer(consumer_config)
topic = 'to-notifier'
consumer.subscribe([topic])

def manda_email(ticker, email, condizione):
    messaggio = EmailMessage()
    messaggio.set_content(condizione)
    messaggio['From'] = "alert.notifier.system@gmail.com"
    messaggio['To'] = email
    messaggio['Subject'] = ticker

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("alert.notifier.system@gmail.com", "vhcq imvk jbvq wbcs")
    server.send_message(messaggio)
    server.quit()

while True:
    messaggio = consumer.poll(3.0)
    if messaggio is None:
        continue
    if messaggio.error():
        print(f"Errore: {messaggio.error()}")
        continue

    dati = json.loads(messaggio.value().decode('utf-8'))    #email: email, ticker: ticker, condizione: condizione 
                                                            #dati è un dizionario
    manda_email(dati["ticker"], dati["email"], dati["condizione"])