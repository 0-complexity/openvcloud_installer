import subprocess
import yaml
import click
import json
import copy
import jinja2
import random
import os
from baldur.remote import Remote

REPO_PATH = "/opt/code/github/0-complexity/openvcloud_installer"
with open("specs.yaml", "r") as spcs:
    specs = yaml.load(spcs)
nodes_specs = specs["nodes"]
disks_specs = specs["disks"]
sizes_specs = specs["sizes"]
large_ssd = sizes_specs["large_ssd"]
small_ssd = sizes_specs["small_ssd"]
hdd = sizes_specs["hdd"]


def prepare_config(config_path):
    with open(config_path, "r") as cfg:
        config = yaml.load(cfg)

    cmd = ["ssh-keygen", "-y", "-f", "/dev/stdin"]
    key = config["ssh"]["private-key"]
    public_key = subprocess.run(
        cmd, stdout=subprocess.PIPE, input=key.encode("utf-8")
    ).stdout.decode("utf-8")
    config["ssh"]["public-key"] = public_key
    return config


def render(context, loader, filename):
    data = jinja2.Environment(loader=loader).get_template(filename).render(context)
    os.makedirs("output", exist_ok=True)
    with open("output/{}".format(filename), "w") as f:
        f.write(data)


def is_mounted(disk):
    if disk.get("mountpoint"):
        return True
    for child in disk.get("children", []):
        if is_mounted(child):
            return True
    return False


def get_node_disks(nodeip, config):
    remote = Remote(nodeip, username="root", pkey=config["ssh"]["private-key"])
    res = remote.run("lsblk -b -J -o name,size,rota,mountpoint", check=False)
    disks = []
    if res.exit_status == 0:
        disks = json.loads(res.stdout)["blockdevices"]
        for disk in disks:
            disk["mounted"] = is_mounted(disk)
            disk["size"] = float(disk["size"]) / (1024 ** 3)
            if disk["rota"] == "1":
                disk["type"] = "hdd"
            elif disk["name"].startswith("nvme"):
                disk["type"] = "nvme"
            else:
                disk["type"] = "ssd"
    return disks


def validate_node_disks(nodename, disks_specs, disks):
    if nodename.startswith("cpu"):
        specs = disks_specs["cpu"]
    else:
        specs = disks_specs["storage"]
    large_ssd_count = 0
    small_ssd_count = 0
    hdd_count = 0
    nvme_count = 0
    for disk in disks:
        if disk["type"] == "nvme":
            nvme_count += 1
        if disk["type"] == "ssd":
            if disk["size"] >= large_ssd:
                large_ssd_count += 1
                continue
            if disk["size"] >= small_ssd:
                small_ssd_count += 1
        else:
            if disk["size"] >= hdd:
                hdd_count += 1
    if specs.get("large_ssd", {}).get("num", 0) > large_ssd_count:
        raise Exception(
            "Not enough large ssd disks on {}, found {}, required {}".format(
                nodename, large_ssd_count, specs.get("large_ssd", {}).get("num", 0)
            )
        )
    if specs.get("small_ssd", {}).get("num", 0) > small_ssd_count:
        raise Exception(
            "Not enough small ssd disks on {}, found {}, required {}".format(
                nodename, small_ssd_count, specs.get("small_ssd", {}).get("num", 0)
            )
        )
    if specs.get("hdd", {}).get("num", 0) > hdd_count:
        raise Exception(
            "Not enough hdd disks on {}, found {}, required{}".format(
                nodename, hdd_count, specs.get("hdd", {}).get("num", 0)
            )
        )
    if specs.get("nvme", {}).get("num", 0) > nvme_count:
        raise Exception(
            "Not enough nvme disks on {}, found {}, required {}".format(
                nodename, nvme_count, specs.get("nvme", {}).get("num", 0)
            )
        )


def get_nodes(config, role="cpu"):
    nodes = []
    for node in config["nodes"]:
        if role in node["roles"]:
            nodes.append(node)
    return nodes

def get_ovs_config():
    with open("/etc/ovscred/edgeuser", "r") as f:
        username = f.read()
    with open("/etc/ovscred/edgepassword", "r") as f:
        password = f.read()
    return {'edgeuser': username, 'password': password}

@click.command()
@click.option(
    "--config_path", default="system-config.yaml", help="Path to system-config"
)
def main(config_path):
    config = prepare_config(config_path)
    env_type = config["environment"]["type"]
    ovs_config = get_ovs_config()
    loader = jinja2.FileSystemLoader("./templates/{}".format(env_type))
    nodes_ips = {}
    nodes = []
    storage_nodes = get_nodes(config, "storage")
    cpu_nodes = get_nodes(config, "cpu")
    cpucount = specs["nodes"][env_type]["cpu"]
    storagecount = specs["nodes"][env_type]["storage"]
    cachebackendcount = specs["disks"]["cpu"]["large_ssd"]["num"]
    backendcount = specs["disks"]["storage"]["hdd"]["num"]
    # validate nodes number
    if len(storage_nodes) < storagecount:
        raise Exception("Number of storage nodes is not enough")
    if len(cpu_nodes) < cpucount:
        raise Exception("Number of cpu nodes is not enough")

    for idx, node in enumerate(storage_nodes):
        node_number = idx + 1
        node["alias"] = "storage_%02d" % node_number
    for idx, node in enumerate(cpu_nodes):
        node_number = idx + 1
        node["alias"] = "cpu_%02d" % node_number

    nodes.extend(storage_nodes)
    nodes.extend(cpu_nodes)
    for node in nodes:
        # get nodes disks and validate them
        node_disks = get_node_disks(
            node["management"]["ipaddress"].split("/")[0], config
        )
        validate_node_disks(node["alias"], disks_specs, node_disks)
        # get nodes ips
        node_ip_key = "{}_ip".format(node["alias"])
        ip = node["storage"]["ipaddress"].split("/")[0]
        nodes_ips[node_ip_key] = ip
        node["ip"] = ip
        node["disks"] = node_disks

    render(
        {"storage_nodes": storage_nodes, "cpu_nodes": cpu_nodes, "cpucount": cpucount},
        loader,
        "inventory",
    )
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    data = {}
    data["env_name"] = config["environment"]["subdomain"]
    data["edgeuser"] = ovs_config['edgeuser']
    data["password"] = ovs_config['edgepassword']
    data["ovs_repo_url"] = config["environment"]["ovs_repo_url"]
    data["ovs_version"] = config["environment"]["ovs_version"]

    data.update(nodes_ips)
    render(data, loader, "all")

    with open("./templates/{}/setup.json".format(env_type)) as fd:
        setup = json.load(fd)

    setup["ci"]["grid_ip"] = storage_nodes[0]["ip"]
    # storage backends
    for backend in setup["setup"]["backends"]:
        if backend["name"].startswith("cachebackend"):
            # cachecbakcend01 takes first half of the large ssd on cpu nodes
            osds = {}
            backend["osds"] = osds
            for cpunode in cpu_nodes[:cpucount]:
                # disk count
                disks = {}
                useabledisks = list(
                    filter(
                        lambda x: not x["mounted"] and x["type"] == "ssd",
                        cpunode["disks"],
                    )
                )
                if backend["name"].endswith("01"):
                    # first half
                    useabledisks = useabledisks[: int(cachebackendcount / 2)]
                else:
                    # second half
                    useabledisks = useabledisks[
                        int(cachebackendcount / 2) : cachebackendcount
                    ]
                osds[cpunode["ip"]] = disks
                for disk in useabledisks:
                    disks[disk["name"]] = 2
        elif backend["name"] in ("backend01", "backend02"):
            # cachecbakcend01 takes first half of the large ssd on cpu nodes
            osds = {}
            backend["osds"] = osds
            for storagenode in storage_nodes[:storagecount]:
                # disk count
                disks = {}
                useabledisks = list(
                    filter(
                        lambda x: not x["mounted"] and x["type"] == "hdd",
                        storagenode["disks"],
                    )
                )
                if backend["name"].endswith("01"):
                    # first half
                    useabledisks = useabledisks[: int(backendcount / 2)]
                else:
                    # second half
                    useabledisks = useabledisks[int(backendcount / 2) :]
                osds[storagenode["ip"]] = disks
                for disk in useabledisks:
                    disks[disk["name"]] = 1
    # storagerouters
    storagerouters = {}
    storageroutertemplate = list(setup["setup"]["storagerouters"].values())[0]
    setup["setup"]["storagerouters"] = storagerouters
    for storagenode in storage_nodes:
        storagerouter = copy.deepcopy(storageroutertemplate)
        storagerouters[storagenode["ip"]] = storagerouter
        storagerouter["hostname"] = storagenode["name"]
        # configure roles
        disks = {}
        storagerouter["disks"] = disks
        writeroles = 0
        scrub = 0
        db = 0
        for disk in storagenode["disks"]:
            if disk["mounted"] and scrub == 0:
                disks[disk["name"]] = {"roles": ["SCRUB"]}
                scrub += 1
            elif not disk["mounted"] and disk["type"] == "ssd" and writeroles < 2:
                disks[disk["name"]] = {"roles": ["WRITE"]}
                writeroles += 1
            elif disk["type"] == "nvme" and db == 0:
                disks[disk["name"]] = {"roles": ["DB", "DTL"]}
                db += 1

        for name, vpool in storagerouter["vpools"].items():
            vpool["storage_ip"] = storagenode["ip"]

    with open("output/setup.json", "w") as f:
        json.dump(setup, f)


if __name__ == "__main__":
    main()
