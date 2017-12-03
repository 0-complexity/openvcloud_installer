from JumpScale import j
import os
import base64

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        j.system.fs.createDir("/opt/jumpscale7/apps/oauthserver")
        return True

    def configure(self, serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the jpackage if anything needs to be started
        """
        binarysecret = os.urandom(256)
        cookie_store_secret = base64.b64encode(binarysecret)
        serviceObj.hrd.set("instance.oauth.cookie_store_secret", cookie_store_secret)
        serviceObj.hrd.applyOnFile("/opt/jumpscale7/apps/oauthserver/settings.toml")

        binarysecret = os.urandom(32)
        clientsecret = base64.urlsafe_b64encode(binarysecret)
        serviceObj.hrd.set("instance.oauth.clients.ovs.secret", clientsecret)

        binarysecret = os.urandom(32)
        clientsecret = base64.urlsafe_b64encode(binarysecret)
        serviceObj.hrd.set("instance.oauth.clients.portal.secret", clientsecret)

        serviceObj.hrd.applyOnFile("/opt/jumpscale7/apps/oauthserver/clients.toml")

        return True
