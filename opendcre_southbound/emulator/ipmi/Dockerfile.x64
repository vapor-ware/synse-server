FROM vaporio/vapor-endpoint-base-x64:1.0
MAINTAINER Erick Daniszewski <erick@vapor.io>

RUN pip install -I \
    pycrypto

ADD . /emulator
WORKDIR /emulator

EXPOSE 623/udp

ENTRYPOINT ["python",  "-u", "ipmi_emulator.py"]