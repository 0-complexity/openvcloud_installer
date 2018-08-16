from js9 import j


def install(job):
    """
    - create deployment for syncthing.
    - attach mount location to pods at
      - /var/ovc/billing
      - /var/ovc/influx
    """
