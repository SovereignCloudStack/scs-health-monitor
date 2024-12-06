FROM ubuntu:latest

USER 0
RUN apt-get update && \
       apt-get upgrade -y && \
       apt-get dist-upgrade -y && \
       apt-get install python3-dev libpython3-dev libldap2-dev libsasl2-dev \
         python3-minimal python3-venv gcc -y && \
       mkdir -p /installation/ && \
       chown 1001:1001 /installation/ && \
       chmod 755 /installation/ && \
       useradd -u 1001 scs-health-monitor
ADD scs-health-monitor /installation/scs-health-monitor
ADD requirements.txt /installation/requirements.txt
RUN /installation/scs-health-monitor deps
# up to here the steps are splitted to have efficent container build times using the cache layers
ADD --chown=1001:1001 . /installation/

RUN apt-get remove gcc python3-dev libpython3-dev libldap2-dev libsasl2-dev -y && \
   apt-get autoremove -y && \
   apt-get clean

USER 1001

WORKDIR /installation
ENTRYPOINT ["/installation/scs-health-monitor"]
