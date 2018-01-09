from JumpScale import j


def get_dependencies(template):
    hrd = template.getHRD()
    dependencies = [template]
    for dependency in hrd.getListFromPrefixEachItemDict('dependencies'):
        for deptemplate in j.atyourservice.findTemplates(name=dependency['name'], domain=dependency.get('domain', '')):
            dependencies += get_dependencies(deptemplate)
    return dependencies


def replace_vars(path):
    return path.replace('$(instance.portal.instance)', 'main') \
           .replace('$(system.paths.base)', '/opt/jumpscale7') \
           .replace('$(service.instance)', 'main') \
           .replace('$(system.paths.python.lib.js)', '/opt/jumpscale7/lib/JumpScale') \
           .replace('$(system.paths.python.lib.ext)', '/opt/jumpscale7/libext')


class ServiceMigration:
    def __init__(self):
        pass

    def services(self):
        data = {}
        j.do.execute('git config --global user.email "builder@greenitglobe.com"')
        j.do.execute('git config --global user.name "GreenItGlobe Builder"')
        metarepos = j.application.config.getDictFromPrefix('atyourservice.metadata').values()
        for repo in metarepos:
            j.do.pullGitRepo(url=repo['url'], branch=repo['branch'], ignorelocalchanges=True, reset=True)
        masteraio = j.atyourservice.findTemplates(name='cb_master_aio')[0]

        for service in get_dependencies(masteraio):
            for export in service.getHRD().getListFromPrefix("git"):
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
            'ignorelocalchanges': True,
            'reset': True,
            'tag': service.get('tag')
        }

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


        for src, dest, link in items:
            dest = replace_vars(dest)
            print(dest)
            if '$' in dest:
                raise RuntimeError('forgot to adjust {}'.format(dest))
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
