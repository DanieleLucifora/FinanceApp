# Homework 3 - Distributed Systems and Big Data - UNICT - AA 2024-2025
- Fernando Riccioli
- Daniele Lucifora

## Descrizione
Il progetto riguarda lo sviluppo di un'applicazione di gestione delle informazioni finanziarie, basata su un'architettura a microservizi e comunicazione tramite gRPC. 
L'applicazione consente la registrazione e gestione degli utenti, l'aggiornamento dei ticker finanziari e la raccolta di dati relativi ai valori azionari. 
Utilizzando un database MySQL, i microservizi sono separati in due categorie principali:
- gestione degli utenti 
- gestione delle informazioni sui ticker azionari

La comunicazione tra client e server avviene tramite chiamate gRPC, sfruttando i protocolli di serializzazione Protobuf.
Inoltre, il progetto implementa un sistema di cache per garantire l'unicità delle operazioni (at-most-once), evitando chiamate duplicate per le stesse operazioni.
L'applicazione supporta operazioni di registrazione utente, aggiornamento dei ticker, eliminazione degli utenti e recupero dei valori storici e media degli ultimi valori selezionati.
Per la gestione del database viene utilizzato il pattern CQRS(Command and Query Responsability Segregation), che separa i comandi dalle query.
È stata inoltre implementata la notifica asincrona agli utenti, i quali riceveranno una email ogni volta che il loro ticker supererà le soglie predefinite high value e low value.
Il sistema di notifica asincrona si basa su Apache Kafka. Tale sistema ascolta continuamente uno specifico topic in un broker Kafka e non appena viene pubblicato un nuovo messaggio sul topic, il sistema lo recupera ed elabora. Se il messaggio contiene informazioni come il ticker e l'email, il sistema invia una notifica via email.

## Build & Deploy
Prerequisiti:
- Python 3
- Docker e Docker Compose

1. Avviare Docker Desktop
2. Aprire il terminale e selezionare una directory per clonare il progetto
3. Digitare `git clone https://github.com/Fernando-Riccioli/Homework-2`
4. Spostarsi all'interno della cartella clonata e digitare `docker compose up -d`
5. Spostarsi all'interno della directory gRPC e digitare `python client.py`
6. Eseguire le istruzioni visualizzate nel terminale

