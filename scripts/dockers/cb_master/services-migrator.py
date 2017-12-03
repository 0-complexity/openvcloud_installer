from JumpScale import j
import json
import pprint
import os

class ServiceMigration:
    def __init__(self):
        pass

    def services(self):
        data = {}
        masteraio = j.atyourservice.get(name='cb_master_aio')

        for service in masteraio.getDependencyChain():
            for export in service.hrd.getListFromPrefix("service.git"):
                if not isinstance(export, dict):
                    continue

                if data.get(service.name):
                    data[service.name].append(export)
                    continue

                data[service.name] = [export]

        return data

    def fetch(self, services):
        for service in services:
            print("[+] service: %s" % service)

            for item in services[service]:
                print("[+]   fetching: %s" % item['url'])
                self.download(item)

    def download(self, service):
        settings = {
            'login': 'ssh',
            'url': service.get('url'),
            'depth': service.get('depth'),
            'branch': service.get('branch'),
            'revision': service.get('revision'),
            'dest': None,
            'tag': service.get('tag')
        }

        # FIXME
        if settings['branch'] == '7.1.7':
            settings['branch'] = '7.2.1'

        repo = j.do.pullGitRepo(**settings)

        src = "%s/%s" % (repo, service['source'])
        src = src.replace("//", "/")

        dest = service['dest']

        link = ("link" in service and str(service["link"]).lower() == 'true')
        nodirs = ("nodirs" in service and str(service["nodirs"]).lower() == 'true')

        if src[-1] == "*":
            src = src.replace("*", "")

            items = j.do.listFilesInDir(path=src, recursive=False, followSymlinks=False, listSymlinks=False)

            if nodirs is False:
                items += j.do.listDirsInDir(path=src, recursive=False, dirNameOnly=False, findDirectorySymlinks=False)

            items = [(item, "%s/%s" % (dest, j.do.getBaseName(item)), link) for item in items]

        else:
            items = [(src, dest, link)]

        # print(items)

        for src, dest, link in items:
            if dest[0] != "/":
                dest = "/%s" % dest

            else:
                if link:
                    if not j.system.fs.exists(dest):
                        j.system.fs.createDir(j.do.getParent(dest))
                        j.do.symlink(src, dest)

                else:
                    print("copy: %s -> %s" % (src, dest))

                    if j.system.fs.isDir(src):
                        j.system.fs.createDir(j.system.fs.getParent(dest))
                        j.system.fs.copyDirTree(src, dest, eraseDestination=False, overwriteFiles=False)

                    else:
                        j.system.fs.copyFile(src, dest, True, overwriteFile=False)


if __name__ == '__main__':
    migrator = ServiceMigration()

    print("[+] building services list")
    services = migrator.services()

    # print(json.dumps(services))

    print("[+] fetching files")
    migrator.fetch(services)
