FROM openvcloud/cb_master:2.4.0

RUN mkdir -p /root/.ssh && echo "$PRIVATEKEY" > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
RUN curl "${MANIFESTURL:-https://raw.githubusercontent.com/0-complexity/devmanifests/master/manifests/}/${VERSION}.yml" > /root/manifest.yml
RUN jspython /opt/code/github/0-complexity/openvcloud/scripts/versions/makerelease -m /root/manifest.yml
