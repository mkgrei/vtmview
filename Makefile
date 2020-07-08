IMAGE=ikr.iij.jp/tools/vtmview
TAG=0.0.0

build:
	docker build . -t ${IMAGE}:${TAG}
	docker push ${IMAGE}:${TAG}
