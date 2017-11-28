FROM resin/rpi-raspbian:latest  
ENTRYPOINT []

RUN apt-get update && \  
    apt-get -qy install curl \
                build-essential python \
                ca-certificates

ADD ./test.py ./test.py


CMD ["python", "test.py"]
