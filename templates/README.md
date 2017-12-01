# Installation & configuration strategy

## Installation procedure
- Install 1st kubernetes host using usb key
  - Automatically install OS
  - Put disks into mirror
  - Do partitioning
    - / ==> /dev/sda1
      - 40GB
      - ext4
      - Os parts
    - /var ==> /dev/sda2
      - The rest of the space
      - btrfs (disable copy on write)
        - For informational purposes we add here which btrfs subvolumes will be created later on.
        - subvolumes
          - billing
            - mountpath: /var/ovc/billing
            - need to set quota from ays blueprint
            - replicated by synchting
          - influxdb
            - mountpath: /var/ovc/infuxdb
            - need to set quota from ays blueprint
            - replicated by synchting
          - mongodb
            - mountpath: /var/ovc/mongodb
            - need to set quota from ays blueprint
            - replicated by mongodb

