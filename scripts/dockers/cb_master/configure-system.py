from JumpScale import j
import yaml
import argparse


def get_config():
    with open("/opt/cfg/system/system-config.yaml") as file_discriptor:
        data = yaml.load(file_discriptor)
    return data


def configure(roles, machineguid, controller_addr, ssh):
    """
    configures the js7 node.
    """
    if ssh:
        j.system.fs.remove("/etc/service/sshd/down")
    config = get_config()
    gid = int(config["environment"]["grid"]["id"])
    print("[+] set gid to: %s" % gid)
    roles = roles.split(",")
    j.application.config["grid"]["id"] = gid
    j.application.config["grid"]["node"]["id"] = ""
    j.application.config["grid"]["node"]["roles"] = roles

    if config.get("alerta"):
        system = j.application.config["system"]
        system["alerta"] = {}
        system["alerta"]["api_key"] = config["alerta"]["api_key"]
        system["alerta"]["api_url"] = config["alerta"]["api_url"]
        j.core.config.set("system", "system", system)
    if machineguid:
        j.application.config["grid"]["node"]["machineguid"] = machineguid

    j.core.config.set("system", "grid", j.application.config["grid"])

    j.system.fs.copyDirTree("/opt/jumpscale7/cfg/system/", "/opt/cfgdir/system/")
    password = config["environment"]["password"]
    portal_instances = j.core.config.list("portal_client")
    agentcontroller_client = j.core.config.get("agentcontroller_client", "main")
    osis_service = j.core.config.get("osis", "main")
    osis_client = j.core.config.get("osis_client", "main")
    portal_service = j.core.config.get("portal", "main")

    for portal_instance in portal_instances:
        portal_client = j.core.config.get("portal_client", portal_instance)
        portal_client["secret"] = password
        j.core.config.set("portal_client", portal_instance, portal_client)

    agentcontroller_client["passwd"] = password
    if controller_addr:
        agentcontroller_client["addr"] = controller_addr
    j.core.config.set("agentcontroller_client", "main", agentcontroller_client)
    osis_service["passwd"] = password
    j.core.config.set("osis", "main", osis_service)
    osis_client["passwd"] = password
    j.core.config.set("osis_client", "main", osis_client)
    portal_service["rootpasswd"] = password
    portal_service["secret"] = password
    j.core.config.set("portal", "main", portal_service)
    if "master" in roles:
        scl = j.clients.osis.getNamespace("system")
        scl.health.deleteSearch({})

    j.system.fs.copyDirTree("/opt/jumpscale7/cfg/", "/opt/cfgdir/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--roles", default="node")
    parser.add_argument("--machineguid", default=None)
    parser.add_argument("--controller-addr", dest="controller_addr", default=None)
    parser.add_argument("--ssh", default=False, action="store_true")
    args = parser.parse_args()
    configure(args.roles, args.machineguid, args.controller_addr, args.ssh)
