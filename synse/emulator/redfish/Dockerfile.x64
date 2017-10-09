FROM vaporio/vapor-endpoint-base-x64:1.0

ADD . /emulator
WORKDIR /emulator

EXPOSE 5040

CMD [ "python", "rf_emulator.py" ]