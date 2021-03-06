#!/usr/bin/python3

import subprocess as sh
import os

def setup(dest, startIperf=True, ipc='netlink'):
    print("setup")
    print("=========================")
    if not os.path.exists(dest):
        sh.run('mkdir -p {}'.format(dest), shell=True)
        print("> created output directory: {}".format(dest))

    ipc = 'ipc=1' if ipc is 'chardev' else 'ipc=0'
    sh.run('./scripts/setup.sh {} {}'.format(ipc, dest), shell=True, check=True)

    if startIperf:
        sh.Popen('./scripts/run-iperf-server.sh > {0}/iperf-server.log'.format(dest), shell=True)
        print("> started iperf server")

def reset():
    sh.run('./scripts/reset.sh', shell=True)
