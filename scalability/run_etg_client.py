#!/usr/bin/python3

import subprocess as sh
import argparse

client_binary = "../fct_scripts/empiricial-traffic-gen/bin/client"
client_config_params = {"load": "1000000Mbps", "fanout": "1 100", "num_reqs": "100000"}


def run_and_yield(command):
    process = sh.Popen(command, stdout=sh.PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        yield line

def run_and_print(command):
    out = ""
    for path in run_and_yield(command):
        print(path.decode('utf-8'))  
        out += path.decode('utf-8') + "\n" 
    return out

def port(server_num):
    return str(5000 + server_num)

def write_client_config(config_filename, server_ip, num, cdf):
    with open(config_filename, "w") as f:
        for i in range(num):
            f.write("server {} {}\n".format(server_ip, port(i)))

        # Write non-configurable params
        for key in client_config_params:
            f.write("{} {}\n".format(key, client_config_params[key]))

        # Write configurable params
        f.write("{} {}\n".format('req_size_dist', cdf))

def spawn_clients(config_filename, logname):
    return run_and_print("{} -c {} -l {} -s {}".format(client_binary, config_filename, logname, 123))
    # print(out.stdout.decode('utf-8'))
    # return out

if __name__ == "__main__":
    # takes a bunch of params
    parser = argparse.ArgumentParser(description='Run empirical traffic generator client(s).')
    parser.add_argument('ip', type=str, help='ip address of the server')
    parser.add_argument('number', metavar='N', type=int, nargs='?',
                        help='the number of servers to run (default: 1)', default=1)
    parser.add_argument('-config', type=str, dest='config',
                        help='destination for the config file (default: config)', default="config")
    parser.add_argument('-cdf', type=str, dest='cdf',
                        help='cdf file to use (default: empiricial-traffic-gen/BIG_CDF)', default="empiricial-traffic-gen/BIG_CDF")
    parser.add_argument('-logfile', type=str, dest='logfile',
                        help='logfile prefix (default: etg-log)', default="etg-log")
    args = parser.parse_args()
   
    # generates config file 
    write_client_config(args.config, args.ip, args.number, args.cdf)

    # runs client binary with config 
    spawn_clients(args.config, args.logfile)
