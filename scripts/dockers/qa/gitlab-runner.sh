RUNNERS=4
URL="http://git.gig.tech"

usage(){
    echo "Usage"
    echo "options:"
    echo "  --url: gitlab server url"
    echo "  --token: project token"
    echo "  --runners: number of runners"
}

while true; do
  case "$1" in
    --url) URL=${2}; shift ;;
    --token) TOKEN=${2}; shift ;;
    --runners) RUNNERS=${2}; shift ;;
    --help) usage shift ;;
    * ) break ;;
  esac
  shift
done

#configure gitlab runner
gitlab-runner install --user=root --working-directory=/root
gitlab-runner start
gitlab-runner run &> /etc/gitlab-runner/logs.txt &
sed -i "s/concurrent = 1/concurrent = ${RUNNERS}/g" /etc/gitlab-runner/config.toml

# extract environment name
script="""
from JumpScale import j
scl = j.clients.osis.getNamespace('system');
env = scl.grid.get(j.application.whoAmI.gid)
print(env.name)
"""
ENVNAME=$(jspython -c "${script}")

# register runners
for i in $(eval echo {1..$RUNNERS})
do
   gitlab-runner register --non-interactive --url "${URL}" --registration-token "${TOKEN}" --executor "shell" --description "${ENVNAME}-runner-${i}" --tag-list "${ENVNAME}"
   gitlab-runner start "${ENVNAME}-runner-${i}"
done
