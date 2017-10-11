# generate the grpc proto python files
proto:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./api.proto

go-proto:
	# for details, see: https://grpc.io/docs/quickstart/go.html
	protoc -I . api.proto --go_out=plugins=grpc:.
