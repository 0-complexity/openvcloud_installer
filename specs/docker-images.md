# https://hub.docker.com/u/jumpscale/core/
- description: complete jumpscale
- ancestor:
  - url: https://hub.docker.com/_/ubuntu/
  - version: 16.04
- version: 7.2
  
# https://hub.docker.com/u/jumpscale/osis/
- ancestor: 
  - url: https://hub.docker.com/u/jumpscale/core/
  - version: 7.2
- version: 7.2

# https://hub.docker.com/u/openvcloud/portal/
- ancestor: 
  - url: https://hub.docker.com/u/jumpscale/core/
  - version: 7.2
- version: 2.3

# https://hub.docker.com/u/openvcloud/statscollector/
- ancestor: ??
- version: 2.3