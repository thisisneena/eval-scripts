import math
import sys
import time
import subprocess as sh

tcp_algs = ["ccp", "reno"]
NUM_SERVERS = 1000
EMPIRICAL_TRAFFIC_GEN = "../fct_scripts/empiricial-traffic-gen/"
client_config_params = {"load": "1000000Mbps", "fanout": "1 100", "num_reqs": "10000", "req_size_dist": EMPIRICAL_TRAFFIC_GEN + "BIG_CDF"}
CLIENT_BINARY = EMPIRICAL_TRAFFIC_GEN + "bin/client"
tmp_file = "a.txt"
NUM_EXPTS = 1
PLOTTING_SCRIPT = "../plot/fct.r"

# for server - spawn process to listen at specific port
def port(server_num):
    return str(5000 + server_num)

def write_client_config(ip_address, config_filename, params):
    f = open(config_filename, "w")
    for i in range(NUM_SERVERS):
        f.write("server {} {}\n".format(ip_address, port(i)))
    for key in params:
        f.write("{} {}\n".format(key, params[key]))

def spawn_clients(exp_config, logname):
    sh.run("{} -c {} -l {} -s {}".format(CLIENT_BINARY, exp_config, logname, 123), shell=True)

def get_log(logname, impl):
    # TODO: access logfile
    awk_command = "awk '{{print $1,$2}}' {}_flows.out | egrep -o '[0-9]+' | paste -d ' ' - - | awk '{{print $1,$2,\"{}\"}}' > {}.fct".format(logname, impl, logname)
    sh.check_output(awk_command, shell=True)

def setup_ccp():
    try:
        sh.check_output("sudo pkill reno", shell=True)
    except:
        # run portus
        sh.Popen(["sudo ./../portus/ccp_generic_cong_avoid/target/debug/reno > ccp.log 2>&1 --ipc netlink"], shell=True)
def get_logname(algname, it):
    return "{}-{}-{}-{}-{}".format(algname, it, client_config_params['load'], client_config_params['num_reqs'], "CAIDA_CDF")

def make_graph_file(outfile):
    sh.check_output("echo 'Size FctUs Impl' > {}".format(outfile), shell=True)
    for it in range((NUM_EXPTS)):
        for alg in tcp_algs:
            algname = 'reno-{}'.format(alg) if 'ccp' in alg else alg
            logname = get_logname(algname, it)
            sh.check_output("cat {}.fct >> {}".format(logname, outfile), shell=True)
            # sh.check_output("rm {}_flows.out".format(logname), shell=True)
            # sh.check_output("rm {}_reqs.out".format(logname), shell=True)
            # sh.check_output("rm {}.fct".format(logname), shell=True)


def main():
    client_config_name = "clientConfig"
    outfile = "fct-{}-{}.log".format(NUM_SERVERS, NUM_EXPTS)
    write_client_config("172.31.22.106", client_config_name, client_config_params)

    #TODO : SETTABLE PARAMS
    alg = "ccp" # ccp or reno

    for it in range((NUM_EXPTS)):
        algname = 'reno-{}'.format(alg) if 'ccp' in alg else alg
        logname = get_logname(algname, it)
        print("Starting experiment for {}".format(logname))
        spawn_clients(client_config_name, logname)
        time.sleep(2)

        if 'ccp' in alg:
            get_log(logname, "ccp_plain")
        else:
            get_log(logname, "kernel_plain")
    
    # make_graph_file(outfile)
    # sh.check_output("{} {}".format(PLOTTING_SCRIPT, outfile), shell=True)

    # shell = true
    # sh.check_output("rm {}".format(client_config_name), shell=True)
    # sh.check_output("rm ccp.log", shell=True)
    # sh.check_output("rm {}".format(outfile), shell=True)

if __name__ == "__main__":
    main()
