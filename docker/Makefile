DOCKER_ID_USER=maxalex

all:
	$(MAKE) base
	$(MAKE) server
	$(MAKE) client

base:
	docker build -t clang-base --force-rm=true clang-base/
	docker tag clang-base ${DOCKER_ID_USER}/clang-base

server:
	docker build -t build-server --force-rm=true build-server/
	docker tag build-server ${DOCKER_ID_USER}/build-server

client:
	docker build -t build-client --force-rm=true build-client/
	docker tag build-client ${DOCKER_ID_USER}/build-client

push:
	docker push ${DOCKER_ID_USER}/clang-base
	docker push ${DOCKER_ID_USER}/build-server
	docker push ${DOCKER_ID_USER}/build-client

run-client:
	docker run -d --rm --name builder -p 2222:22 ${DOCKER_ID_USER}/build-client

stop-client:
	docker stop builder

run-server:
	docker run -d --rm --name build-server -p 3692:3692 ${DOCKER_ID_USER}/build-server