#!/usr/bin/env python3
import sys
sys.path.append('/opt/code/github/0-complexity/openvcloud_installer/scripts/')
from buildlib.helper import build, clone_github_repo

clone_github_repo('0-complexity', 'openvcloud')
build()
