DOCKER_ID_USER=maxalex
DOC_BUILD=docker build --force-rm=true
DOC_TAG=docker tag
DOC_PUSH=docker push

@all: build
build: client server

base: gcc-clang/Dockerfile
	$(DOC_BUILD) -t gcc-clang gcc-clang/
	$(DOC_TAG) gcc-clang $(DOCKER_ID_USER)/gcc-clang

server: base build-server/Dockerfile
	$(DOC_BUILD) -t build-server build-server/
	$(DOC_TAG) build-server $(DOCKER_ID_USER)/build-server

builder: base gcc-clang-cmake-conan/Dockerfile
	$(DOC_BUILD) -t gcc-clang-cmake-conan gcc-clang-cmake-conan/
	$(DOC_TAG) gcc-clang-cmake-conan $(DOCKER_ID_USER)/gcc-clang-cmake-conan

client: builder build-client/Dockerfile
	$(DOC_BUILD) -t build-client build-client/
	$(DOC_TAG) build-client $(DOCKER_ID_USER)/build-client

push:
	$(DOC_PUSH) $(DOCKER_ID_USER)/gcc-clang
	$(DOC_PUSH) $(DOCKER_ID_USER)/build-server
	$(DOC_PUSH) $(DOCKER_ID_USER)/gcc-clang-cmake-conan
	$(DOC_PUSH) $(DOCKER_ID_USER)/build-client

run-client:
	docker run -d --rm --name build-client -p 2222:22 $(DOCKER_ID_USER)/build-client

stop-client:
	docker stop build-client

run-server:
	docker run -d --rm --name build-server -p 3692:3692 $(DOCKER_ID_USER)/build-server