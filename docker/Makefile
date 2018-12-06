DOCKER_ID_USER=maxalex
DOC_BUILD=docker build --force-rm=true
DOC_TAG=docker tag
DOC_PUSH=docker push

@all:
	$(MAKE) clang
	$(MAKE) clang-server
	$(MAKE) clang-cmake-conan
	$(MAKE) clang-client

base: clang/Dockerfile
	docker build --force-rm=true -t clang clang/
	docker tag clang $(DOCKER_ID_USER)/clang

server: clang-server/Dockerfile
	$(DOC_BUILD) -t clang-server clang-server/
	$(DOC_TAG) clang-server $(DOCKER_ID_USER)/clang-server

builder: clang-cmake-conan/Dockerfile
	$(DOC_BUILD) -t clang-cmake-conan clang-cmake-conan/
	$(DOC_TAG) clang-cmake-conan $(DOCKER_ID_USER)/clang-cmake-conan

client: clang-client/Dockerfile
	$(DOC_BUILD) $@/
	$(DOC_TAG) $@ $(DOCKER_ID_USER)/$@

push:
	$(DOC_PUSH) $(DOCKER_ID_USER)/clang
	$(DOC_PUSH) $(DOCKER_ID_USER)/clang-server
	$(DOC_PUSH) $(DOCKER_ID_USER)/clang-cmake-conan
	$(DOC_PUSH) $(DOCKER_ID_USER)/clang-client

run-client:
	docker run -d --rm --name builder -p 2222:22 $(DOCKER_ID_USER)/build-client

stop-client:
	docker stop builder

run-server:
	docker run -d --rm --name build-server -p 3692:3692 $(DOCKER_ID_USER)/build-server