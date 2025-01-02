.PHONY: build prepare run delete

# Importante!!! settare IMAGE_REPO del proprio docker registry attraverso il comando:
# export IMAGE_REPO=nomeutenteDockerHub

ifdef IMAGE_REPO
IMAGE_REPO := $(IMAGE_REPO)
else
IMAGE_REPO := localhost
endif


build:
	@echo "Creazione immagini Docker in corso..."
	@docker build -t server-app -f ./gRPC/Dockerfile.server . 
	@docker build -t datacollector-app -f ./DataCollector/Dockerfile.data_collector .
	@docker build -t alertnotifier-app -f ./AlertNotifier/Dockerfile.alert_notifier_system .
	@docker build -t alertsystem-app -f ./AlertSystem/Dockerfile.alert_system .
	@echo "Tagging immagini Docker in corso..."
	@docker tag server-app $(IMAGE_REPO)/server-app
	@docker tag datacollector-app $(IMAGE_REPO)/datacollector-app
	@docker tag alertnotifier-app $(IMAGE_REPO)/alertnotifier-app
	@docker tag alertsystem-app $(IMAGE_REPO)/alertsystem-app 
	@echo "Pushing immagini Docker a $(IMAGE_REPO) in corso..."
	@docker push $(IMAGE_REPO)/server-app
	@docker push $(IMAGE_REPO)/datacollector-app
	@docker push $(IMAGE_REPO)/alertnotifier-app
	@docker push $(IMAGE_REPO)/alertsystem-app

prepare:
	@echo "Caricamento immagini Docker nel Minikube in corso..."
	@minikube image load ${IMAGE_REPO}/server-app
	@minikube image load ${IMAGE_REPO}/datacollector-app
	@minikube image load ${IMAGE_REPO}/alertnotifier-app
	@minikube image load ${IMAGE_REPO}/alertsystem-app
	@echo "Applicazione manifests Kubernetes in corso..."
	@envsubst < manifests/prometheus.yaml | kubectl apply -f -
	@envsubst < manifests/mysqldb.yaml | kubectl apply -f -
	@envsubst < manifests/zookeeper.yaml | kubectl apply -f -
	@envsubst < manifests/kafka_broker.yaml | kubectl apply -f -
	@envsubst < manifests/server.yaml | kubectl apply -f -
	@envsubst < manifests/data_collector.yaml | kubectl apply -f -
	@envsubst < manifests/alert.yaml | kubectl apply -f -	
