FROM openvcloud/cb_master

RUN useradd test

RUN apt update && apt-get install -y python-dev build-essential libssl-dev \
libxml2-dev libxslt1-dev zlib1g-dev python-pip \
python3-pip iputils-ping tmux wget unzip xvfb chromium-chromedriver s3cmd

COPY code/github/0-complexity/openvcloud/ /opt/code/github/0-complexity/openvcloud/
RUN cd /opt/code/github/0-complexity/openvcloud/tests && \
pip install -r requirements.txt && pip3 install -r ovc_master_hosted/Portal/requirements.txt

RUN ln -fs /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
RUN ln -fs /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver