# OpenvCloud network setup
![image](https://docs.google.com/drawings/d/e/2PACX-1vTVm5VstLyfsevlecNHkPjH2JencQbqKqTH767EsbG_Mvs0aV5juH6kXwGpu_bm10BD7Lzvle0S2iry/pub?w=1580&h=722)
[edit image here](https://docs.google.com/drawings/d/1LXH7eJQNU9i0RqO13yo-8z0_rx3cyeO498wA23N7q8o/edit)

## Environment network configuration file
```yaml
timezone: CET
network:
  vlans:
    management: 2311
    public: 2312
    vx-backend: 2313
    gateway: 2314
    storage: 2315
  providers:
    - name: interroute
      vlan: 23 # Vlan to internet provider network. 0 for untagged
  cisco:
    - name: 50 port switch
      password: H0ndebr0k3nZijnN44tL3kk3r
      hostname: littledavid
      provider-port: 48 # Switch port that will be cabled to the internet provider
      management: 
        switch-ip:
          address: 10.12.2.201
          netmask: 255.255.255.0
        ports:
          controllers:
            ipmi: 1-3 # Network connections to ipmi ports
            mgmt: 4-6 # Network connections to regular nic'ses
          cpunodes:
            ipmi: 7,8
            mgmt: 9,10
          stornodes:
            ipmi: 11-12
            mgmt: 13-14
          mellanox: 15,16
      trunk-ports: 
        controllers: 45-47
        mellanox: 49,50          
  mellanox:
    mellanox-1:
      provider:
          port: 46 # Switch port that will be cabled to the internet provider
          vlan: 23 # Vlan to internet provider network. 0 for untagged
      mlag:
        - 47
        - 48
      lacp-port-ranges:
        - 1 - 45
    mellanox-2:
      provider:
          port: 48 # Switch port that will be cabled to the internet provider
          vlan: 23 # Vlan to internet provider network. 0 for untagged
      mlag:
        - 1
        - 2
      lacp-port-ranges:
        - 3 - 48
```

## Applying cisco configuration
1. First install dependencies:
```bash
pip2 install -r requirements.txt
```

2. Run the cisco.py script
```bash
python cisco.py --help
usage: cisco.py [-h] [--port PORT] [--logfile LOGFILE] config switch

Provision configuration into the cisco router

positional arguments:
  config             OVC environment yaml configuration file
  switch             Name of the switch in the yaml configuration file

optional arguments:
  -h, --help         show this help message and exit
  --port PORT        Serial port to use to connect to the cisco.
  --logfile LOGFILE  Logfile to which all communication to the cisco is
                     written.
```