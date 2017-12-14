import json
import os

template = "./templates"
target = "./build"
datasource = "influxdb_main"

for filename in os.listdir(template):
    print("[+] generating dashboard: %s" % filename)

    with open(os.path.join(template, filename), "r") as f:
        contents = f.read()

    db = json.loads(contents)

    db['id'] = None
    # db['title'] += " ({})".format(serviceObj.instance)

    for row in db['rows']:
        for panel in row['panels']:
            panel['datasource'] = datasource

    if 'templating' in db:
        for item in db['templating']['list']:
            item['datasource'] = datasource

    with open(os.path.join(target, filename), "w") as f:
        f.write(json.dumps(db))
