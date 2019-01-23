#!/usr/bin/python3

import math
import sys
import time
import subprocess as sh
import argparse
from start_ccp import algs, start as ccp_start
import threading

server_binary = "../fct_scripts/empiricial-traffic-gen/bin/server"

def port(server_num):
    return str(5000 + server_num)

def spawn_servers(num, alg):
    for i in range(num):
        print(i)
        sh.Popen(["{} -t {} -p {} > /dev/null".format(server_binary, alg, port(i))], shell=True) 

def setup_ccp(ccp_mode):
    try:
        sh.check_output("sudo pkill reno", shell=True)
    except:
        if ccp_mode == "per_ack":
            flags = "--per_ack"
        elif ccp_mode == "per_10ms":
            flags = "-i 10"
        else:
            flags = ""
        # run portus
        threading.Thread(target=ccp_start, args=(".", "reno", "netlink", "etg", flags), daemon=True).start()
        time.sleep(1)
        # sh.Popen(["sudo ./../portus/ccp_generic_cong_avoid/target/debug/reno > ccp.log --ipc netlink"], shell=True)

def kill_processes(num, alg, ccp_mode):
    cmd = "for pid in $(ps -ef | grep {0} | awk '{{print $2}}'); do kill -9 $pid; done".format(server_binary)
    print(">", cmd)
    sh.run(cmd, shell=True)
    try:
        print("> sudo pkill reno")
        sh.call("sudo pkill reno", shell=True)
    except:
        return

    run_server(num, alg, ccp_mode)

def run_server(num, alg, ccp_mode):
    if num == 0:
        return

    print("Running {} servers with alg {}...".format(num, alg))

    # run ccp (or don't)
    if alg == "ccp":
        setup_ccp(ccp_mode)

    # run server(s) with desired params 
    spawn_servers(num, alg)

parser = argparse.ArgumentParser(description='Run empirical traffic generator server(s).')
parser.add_argument('number', metavar='N', type=int, nargs='?',
                    help='the number of servers to run (default: 0)', default=0)
parser.add_argument('--kill', dest='action', action='store_const',
                    const=kill_processes, default=run_server,
                    help='kill running server (default: run a new server)')
parser.add_argument('-alg', dest='alg', type=str, nargs='?', default='reno',
                    help='algorithm to use (ccp or reno)')
parser.add_argument('-ccp_mode', dest='ccp_mode', type=str, nargs='?', default='per_10ms')

if __name__ == "__main__":
    args = parser.parse_args()
    args.action(args.number, args.alg, args.ccp_mode)


