# OpenvCloud network setup
![image](https://docs.google.com/drawings/d/e/2PACX-1vTVm5VstLyfsevlecNHkPjH2JencQbqKqTH767EsbG_Mvs0aV5juH6kXwGpu_bm10BD7Lzvle0S2iry/pub?w=1580&h=722)
[edit image here](https://docs.google.com/drawings/d/1LXH7eJQNU9i0RqO13yo-8z0_rx3cyeO498wA23N7q8o/edit)

## Environment network configuration files
```yaml
cisco:
  credentials: # Credentials to manage the switch
    username: admin
    password: 123login
  provider:
    port: 48 # Switch port that will be cabled to the internet provider
    vlan: 23 # Vlan to internet provider network. 0 for untagged
  management-network:
    vlan: 2311 # Vlan on which the management network lives
    port-ranges: # Switch ports on which the management network vlan must be applied
      - 1 - 10
      - 15 - 26
  pxe-boot-network: # Untagged network ports for pxe boot
    port-ranges:
      - 44 - 47
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