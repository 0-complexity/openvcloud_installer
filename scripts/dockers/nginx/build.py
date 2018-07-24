#!/usr/bin/env python3
import sys
sys.path.append('/opt/code/github/0-complexity/openvcloud_installer/scripts/')
from buildlib.helper import clone_repo, build, clone_github_repo

clone_github_repo('0-complexity', 'g8vdc')
clone_github_repo('0-complexity', 'openvcloud_installer')
clone_repo("https://docs.greenitglobe.com/binary/web_python", "master")
build()
