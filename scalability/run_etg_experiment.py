#!/usr/bin/python3
from run_etg_client import write_client_config, spawn_clients
import os 
import subprocess as sh
import time
import argparse

parser = argparse.ArgumentParser(description='Run empirical traffic generator client experiment.')
parser.add_argument('num_clients_start', metavar='N', type=int)
parser.add_argument('num_clients_end', metavar='M', type=int)
parser.add_argument('iterations', metavar='i', type=int,
                    help='how many iterations')
parser.add_argument('impl', type=str,
                    help='kernel ccp_netlink_per_10ms or ccp_netlink_per_ack')

CCP_10MS_DATA = {0: [4459.917882, 3561.992472, 3198.279326, 3222.463146, 4688.510044], 1: [3976.714349, 4686.44738, 3986.757983, 4626.114532, 4388.139736], 2: [4344.180753, 5100.973776, 5079.44248, 5105.736614, 4980.123084], 3: [5052.568821, 5084.488307, 5117.294793, 5090.577278, 5100.791643], 4: [33.158277, 4130.855164, 5110.534472, 4299.764534, 4977.548147], 5: [2334.679179, 4464.397822, 3673.61577, 3669.441988, 3343.324301], 6: [187.129198, 2490.274699, 1964.968058, 3721.317942, 854.19427], 7: [49.216013, 594.683235, 238.469308, 267.625793, 2556.783771], 8: [506.214415, 206.055221, 469.475716, 678.085341, 59.003858]}
CCP_ACK_DATA = {0: [2096.159482, 2224.258716, 2288.83986, 2215.864415, 2812.977008], 1: [3417.208429, 3579.51588, 3498.179504, 3545.726487, 3635.015541], 2: [4196.037619, 4146.685904, 4048.818836, 3943.799477, 4103.015013], 3: [4087.581335, 4116.554477, 4223.867959, 4240.258562, 4159.408283]}
KERNEL_DATA = {0: [4373.962892, 4733.360905, 4280.201234, 4511.650491, 4808.417616], 1: [4948.259759, 4902.375323, 5021.939599, 4824.383399, 4479.496505], 2: [5050.489108, 4928.557479, 4782.080588, 4761.79422, 4743.245174], 3: [5117.010029, 5117.222781, 5107.187089, 5116.80384, 5087.485676], 4: [5106.157004, 5117.183502, 5117.383175, 5117.334074, 5115.782958], 5: [5117.753102, 5114.451843, 5117.733458, 5117.753102, 5117.501022], 6: [5117.707267, 5117.298067, 5117.47156, 5117.370081, 5117.432277], 7: [5116.87584, 5117.409363, 5117.111493, 5117.563221, 5117.284973], 8: [5116.977299, 5117.036213, 5116.610757, 5116.951116, 5116.787476]}
# ITERATIONS = 5
# CLIENTS_START = 8
# CLIENTS_END = 11

def write_plottable(dest, data, impl, ipc, alg):
    if not os.path.exists("./{}/tputs-retry.log".format(dest)):
        with open("./{}/tputs-retry.log".format(dest), 'w') as f:
            f.write("Scenario Impl IPC Algorithm NumFlows Iteration Throughput\n")

    with open("./{}/tputs-retry.log".format(dest), 'a') as f:
        for x in range(CLIENTS_START, CLIENTS_END):
            numflows = 2**x
            print(x)
            for i in range(ITERATIONS):
                if len(data[x]) > i:
                    f.write("{0}-{1}-{2} {0} {1} {2} {3} {4} {5}\n".format(impl, ipc, alg, numflows, i, data[x][i] * 10**6))

def write_plottable_row(dest, data, impl, ipc, alg, numflows, i):
    with open("./{}/tputs-retry.log".format(dest), 'a') as f:
        f.write("{0}-{1}-{2} {0} {1} {2} {3} {4} {5}\n".format(impl, ipc, alg, numflows, i, data * 10**6))

# plot converts data into a plottable format and then plots it
def plot(dest, data, impl, ipc, alg):
    # impl = "kernel" or "ccp_per_ack" or "ccp_per_10ms"
    # ipc = "netlink" or "chardev" or "kernel"
    # alg = "reno" or "cubic"
    print("Throughput Plot")
    print("=========================")
    
    # write_plottable(dest, data, impl, ipc, alg)

    # if os.path.exists("./{}/tputs.pdf".format(dest)):
    #     print("> ./{}/tputs.pdf done".format(dest))
    # else:
    sh.run("../plot/num-flows-tput.r ./{0}/tputs-retry.log ./{0}/tputs.pdf {1}".format(dest, 'light'), shell=True)

def bulk(start, end, iters, impl):
    data = {}

    for i in range(start, end):
        data[i] = []
        num_clients = 2**i
        print("Running experiment with {} clients...".format(num_clients))

        # generates config file 
        write_client_config("config", "172.31.22.106", num_clients, "empiricial-traffic-gen/BIG_CDF")

        for j in range(0, iters):
            print("Iteration {}".format(j))
            # runs client binary with config 
            output = spawn_clients("config", "log")
            for l in output.splitlines():
                if l[0:20] == "Total RX Throughput:":
                    write_plottable_row(".", float(l[21:-4]), impl, "netlink", "reno", num_clients, j)
                    data[i].append(float(l[21:-4]))
            time.sleep(2)
    
    print(data)

    plot(".", data, impl, "netlink", "reno")

if __name__ == "__main__":
    args = parser.parse_args()
    print("{}...{}".format(2**args.num_clients_start, 2**args.num_clients_end))
    bulk(args.num_clients_start, args.num_clients_end, args.iterations, args.impl)

    # data = 0
    # write_client_config("config", "172.31.22.106", args.num_clients, "empiricial-traffic-gen/BIG_CDF")
    # output = spawn_clients("config", "log")
    # for l in output.stdout.decode('utf-8').splitlines():
    #     if l[0:20] == "Total RX Throughput:":
    #         data = float(l[21:-4])
    
    # write_plottable_row(".", data, "ccp_netlink_per_10ms", "netlink", "reno", args.num_clients, args.iter)
