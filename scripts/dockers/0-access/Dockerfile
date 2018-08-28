FROM phusion/baseimage:latest

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl python3 vim git python3-dev gcc

RUN curl https://bootstrap.pypa.io/get-pip.py | python3

RUN git clone https://github.com/0-complexity/0-access.git
RUN cp -r 0-access /opt/

RUN ln -s /opt/0-access/0-access.py /opt/0-access/zero_access.py
ADD 0-access-start.py /opt/0-access/

RUN cp /opt/0-access/lash /bin/
RUN chmod +x /bin/lash
RUN ssh-keygen -A
RUN service ssh restart
RUN pip3 install -r /opt/0-access/requirements.txt


ENTRYPOINT [ "/usr/bin/python3", "/opt/0-access/0-access-start.py" ]