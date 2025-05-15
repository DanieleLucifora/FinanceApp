# Finance Application - Distributed Systems and Big Data - UNICT - AA 2024-2025
- Fernando Riccioli
- Daniele Lucifora

## Descrizione
Il progetto riguarda lo sviluppo di un'applicazione per la gestione delle informazioni finanziarie che utilizza un'**architettura a microservizi** e la comunicazione tramite **gRPC**. L'applicazione permette agli utenti di registrarsi e gestire i propri dati, aggiornare i ticker finanziari e raccogliere informazioni sui valori azionari.<br>
L'applicazione usa un database **MySQL** e i microservizi sono divisi in due categorie principali: una per la gestione degli utenti e una per la gestione delle informazioni sui ticker azionari. La comunicazione tra client e server avviene tramite chiamate gRPC, utilizzando i protocolli di serializzazione Protobuf.<br>
L'applicazione offre un sistema di notifiche tramite **Kafka**, che consente agli utenti di impostare soglie minime e massime per i ticker e ricevere notifiche via email al raggiungimento di tali soglie. Inoltre, viene implementato il pattern **CQRS** (Command Query Responsibility Segregation) per gestire in modo indipendente le operazioni di lettura e scrittura sul Server gRPC. <br>
I microservizi vengono distribuiti su una piattaforma **Kubernetes** utilizzando **Minikube** e viene integrato **Prometheus** per il monitoraggio del Server gRPC e del Data Collector.<br>
Il progetto implementa anche un sistema di cache per garantire l'unicità delle operazioni (at-most-once), evitando chiamate duplicate per le stesse operazioni. L'applicazione supporta operazioni di registrazione utente, aggiornamento dei ticker, eliminazione degli utenti e recupero dei valori storici e media degli ultimi valori selezionati.

## Build & Deploy
### Prerequisiti
- Python3
- Git
- Docker
- Kubectl e Minikube

### Prerequisiti Windows
Per avviare il makefile su Windows è stato scelto di utilizzare `GnuWin32`. Per installarlo dal terminale:
- Digitare `winget install GnuWin32.Make`
- Digitare `winget install GnuWin32.GetText` <!-- Necessario per envsubst -->
- Aggiungere `C:\Program Files (x86)\GnuWin32\bin` come variabile di ambiente al PATH di sistema. 

### Passi introduttivi
1. Avviare Docker Desktop
2. Aprire il terminale e selezionare una directory per clonare la repository.
3. Digitare `git clone https://github.com/danielux86/Homework-3`
4. Digitare `minikube start --driver=docker` per avviare Minikube.
5. Digitare `minikube docker-env` e il comando successivo fornito dal terminale.

### Makefile
6. Recuperare il proprio username su Docker Hub.
7. Spostarsi all'interno della cartella clonata e digitare.
    - Mac/Linux: `export IMAGE_REPO=usernameDockerHub` <!-- Definiamo una variabile d'ambiente IMAGE_REPO -->
    - Windows: `$env:IMAGE_REPO = "usernameDockerHub"`
8. Digitare `make build` <!-- per creare le immagini Docker, effettuare il tagging delle immagini ed il push alla repository remota. -->
9. Digitare `make prepare` <!-- per caricare le immagini Docker nel Minikube ed applicare i manifest. -->
10. Attendere che i pod siano in stato _running_, per controllare è possibile utilizzare il comando `kubectl get pods`. Questo passaggio può richiedere qualche minuto. 

### Port Forwarding
11. Tramite `kubectl get pods` ottenere il name del pod server e del pod prometheus
12. Digitare `kubectl port-forward pod/nome_server 50051:50051` sostituendo `nome_server` con il nome ottenuto.
13. Aprire un'altra finestra di terminale e digitare `kubectl port-forward pod/nome_prometheus 9090:9090` sostituendo `nome_prometheus` con il nome ottenuto.
14. Aprire un'altra finestra di terminale, spostarsi all'interno della directory gRPC e digitare `python client.py`
15. Eseguire le istruzioni visualizzate nel terminale

### Eliminazione 
Per eliminare Minikube e le immagini Docker eseguire i seguenti comandi in sequenza:
- `minikube delete`
- `eval $(minikube docker-env --unset)` 
- `docker rmi -f $(docker images -q)` 
