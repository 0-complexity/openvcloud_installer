from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

CONFIG = """
reporting-disabled = false

[meta]
  dir = "$vardir/influxdb/meta"
  hostname = "localhost"
  bind-address = ":8088"
  retention-autocreate = true
  election-timeout = "1s"
  heartbeat-timeout = "1s"
  leader-lease-timeout = "500ms"
  commit-timeout = "50ms"
  cluster-tracing = false
  raft-promotion-enabled = true

[data]
  dir = "$vardir/influxdb/data"
  engine = "bz1"
  max-wal-size = 104857600
  wal-flush-interval = "10m0s"
  wal-partition-flush-delay = "2s"
  wal-dir = "$vardir/influxdb/wal"
  wal-logging-enabled = true
  wal-ready-series-size = 30720
  wal-compaction-threshold = 0.5
  wal-max-series-size = 1048576
  wal-flush-cold-interval = "5s"
  wal-partition-size-threshold = 52428800
  wal-flush-memory-size-threshold = 5242880
  wal-max-memory-size-threshold = 104857600
  index-compaction-age = 60000000000
  index-min-compaction-interval = 60000000000
  index-compaction-min-file-count = 5
  index-compaction-full-age = 300000000000
  query-log-enabled = true
  retention-auto-create = true
  retention-check-enabled = true
  retention-check-period = "10m0s"
  retention-create-period = "45m0s"

[cluster]
  force-remote-mapping = false
  write-timeout = "5s"
  shard-writer-timeout = "5s"
  shard-mapper-timeout = "5s"

[retention]
  enabled = true
  check-interval = "10m0s"

[registration]
  enabled = false
  url = "https://enterprise.influxdata.com"
  token = ""
  stats-interval = "1m0s"

[shard-precreation]
  enabled = true
  check-interval = "10m0s"
  advance-period = "30m0s"

[admin]
  enabled = true
  bind-address = ":8083"

[monitor]
  store-enabled = false
  store-database = "_internal"
  store-interval = "10s"

[subscriber]
  enabled = true

[http]
  enabled = true
  bind-address = ":8086"
  auth-enabled = false
  log-enabled = true
  write-tracing = false
  pprof-enabled = false

[[graphite]]
  bind-address = ":2003"
  database = "graphite"
  enabled = false
  protocol = "tcp"
  batch-size = 0
  batch-timeout = "0"
  consistency-level = "one"
  separator = "."

[collectd]
  enabled = false
  bind-address = ":25826"
  database = "collectd"
  retention-policy = ""
  batch-size = 5000
  batch-pending = 10
  batch-timeout = "10s"
  read-buffer = 0
  typesdb = "$vardir/influxdb/types.db"

[opentsdb]
  enabled = false
  bind-address = ":4242"
  database = "opentsdb"
  retention-policy = ""
  consistency-level = "one"
  tls-enabled = false
  certificate = "/etc/ssl/influxdb.pem"
  batch-size = 1000
  batch-pending = 5
  batch-timeout = "1s"

[continuous_queries]
  log-enabled = true
  enabled = true
  recompute-previous-n = 2
  recompute-no-older-than = "10m0s"
  compute-runs-per-interval = 10
  compute-no-more-than = "2m0s"

[hinted-handoff]
  enabled = false
  dir = "$vardir/influxdb/hh"
  max-size = 1073741824
  max-age = "168h0m0s"
  retry-rate-limit = 0
  retry-interval = "1s"
  retry-max-interval = "1m0s"
  purge-interval = "1h0m0s"


"""


class Actions(ActionsBase):

    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """

        j.system.fs.createDir('/opt/influxdb/')
        if j.do.TYPE.lower().startswith("ubuntu64"):
            j.system.platform.ubuntu.downloadInstallDebPkg(
                "https://s3.amazonaws.com/influxdb/influxdb_0.9.5_amd64.deb", minspeed=50)

        return True

    def configure(self, service):
        cfg = j.dirs.replaceTxtDirVars(CONFIG, additionalArgs={})
        j.do.writeFile("/opt/influxdb//cfg/config.toml", cfg)

    def build(self, serviceObj):

        # to reset the state use ays reset -n ...

        j.system.platform.ubuntu.check()
        # @todo
