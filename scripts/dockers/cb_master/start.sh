#! /bin/bash

eval `ssh-agent -s`
ssh-add
nohup /sbin/my_init&
ays install -n cb_master_aio --no-start --data "param.rootpasswd:rooter param.publicip.gateway:10.244.0.1 param.publicip.netmask:255.255.0.0 param.publicip.start:10.244.0.510 param.publicip.end:10.244.0.515 param.ovs.url:'https://clusterip' param.portal.url:'http://clusterip' param.oauth.url:'http://clusterip' param.defense.url:'http://clusterip' param.ovc.environment:'http://clusterip' param.itsyouonline.client_id: param.itsyouonline.client_secret: param.smtp.server: param.smtp.port: param.smtp.login: param.smtp.passwd: param.smtp.sender: param.grid.id:1"