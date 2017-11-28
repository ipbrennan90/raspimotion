FROM resin/rpi-raspbian:latest  
ENTRYPOINT []

RUN apt-get update && \  
    apt-get -qy install curl \
                build-essential python \
                ca-certificates

ADD ./motion-detection.py ./motion-detection.py


CMD ["python", " motion-detection.py"]
