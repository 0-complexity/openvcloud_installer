from JumpScale import j
import requests
import json

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def prepare(self, serviceObj):
        j.system.fs.createDir("/opt/grafana")
        j.system.fs.createDir("/opt/grafana/conf")
        j.system.fs.createDir("/opt/grafana/public")

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        influx_instance = serviceObj.hrd.get("instance.param.influxdb.connection")
        hrd = j.application.getAppInstanceHRD("influxdb_client", influx_instance)
        host = hrd.getStr("instance.param.influxdb.client.address")
        port = hrd.getInt("instance.param.influxdb.client.port")
        login = hrd.getStr("instance.param.influxdb.client.login")
        passwd = hrd.getStr("instance.param.influxdb.client.passwd")
        dbname = hrd.getStr("instance.param.influxdb.client.dbname")

        data = {
            "type": "influxdb",
            "access": "proxy",
            "database": dbname,
            "name": "influxdb_main",
            "url": "http://%s:%u" % (host, port),
            "user": login,
            "password": passwd,
            "default": True,
        }

        # need to start the grafana backend server to enable http api
        serviceObj.start()

        # check if the datasource already exists
        configured_password = serviceObj.hrd.get("instance.param.password")
        grafanaclient = j.clients.grafana.get(username="admin", password="admin")
        if not grafanaclient.isAuthenticated():
            grafanaclient = j.clients.grafana.get(
                username="admin", password=configured_password
            )
        else:
            grafanaclient.changePassword(configured_password)

        datasources = grafanaclient.listDataSources()
        present = False
        for ds in datasources:
            if (
                ds["url"] == data["url"]
                and ds["user"] == data["user"]
                and ds["password"] == data["password"]
                and ds["access"] == data["access"]
            ):
                present = True

        if not present:
            # create the datasource for influxdb
            try:
                grafanaclient.addDataSource(data)
            except Exception as e:
                j.events.opserror_critical(e.message)
