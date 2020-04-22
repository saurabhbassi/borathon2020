#!/usr/bin/env python

import pyVmomi
import argparse
import atexit
import itertools
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
import prettytable
import humanize

MBFACTOR = float(1 << 20)
KBFACTOR = float(1 << 10)

printVM = False
printDatastore = True
printHost = True

global host_res_table
datastore_res_table = {}

def GetArgs():

    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    args = parser.parse_args()
    return args


def printHostInformation(datacenter, host, cluster):
    global host_res_table
    try:
        datacenter_name = datacenter.name
        summary = host.summary
        name = host.name
        stats = summary.quickStats
        hardware = host.hardware
        TotalCpu = (summary.hardware.cpuMhz * summary.hardware.numCpuCores)/1000
        cpuUsage = stats.overallCpuUsage/1000
        FreeCpu = TotalCpu - cpuUsage
        memoryCapacity = hardware.memorySize
        memoryCapacityInMB = hardware.memorySize/MBFACTOR
        memoryUsage = stats.overallMemoryUsage
        FreeMemory = memoryCapacityInMB - memoryUsage
        freeCpuPercent = round(100 - ((float(cpuUsage) / TotalCpu) * 100), 2)
        freeMemoryPercentage = round(100 - ((float(memoryUsage) / memoryCapacityInMB) * 100),2)
        memoryCapacityInGB = round(memoryCapacityInMB/KBFACTOR,2)
        memoryUsage = round(memoryUsage/KBFACTOR,2)
        FreeMemory = round(FreeMemory/KBFACTOR,2)
        datastore = summary.host.datastore
        datastore_names = [x.name for x in datastore]
        for ds_name in datastore_names:
            Capacity = datastore_res_table[ds_name]['capacity']
            FreeDisk = datastore_res_table[ds_name]['free_space']
            if 'ssd' in ds_name.lower():
                ssd_or_hdd = 1
            else:
                ssd_or_hdd = 0
            host_res_table.add_row([datacenter_name, name, TotalCpu, cpuUsage, FreeCpu, memoryCapacityInGB, memoryUsage, FreeMemory,freeCpuPercent, freeMemoryPercentage, ds_name, Capacity, FreeDisk, ssd_or_hdd, cluster])
            TotalCpu = cpuUsage = FreeCpu = memoryCapacityInGB = memoryUsage = FreeMemory = freeCpuPercent = freeMemoryPercentage = '-'
    except Exception as error:
        print "Unable to access information for host: ", name
        print error
        pass


def printComputeResourceInformation(datacenter, computeResource):
    global host_res_table
    try:
        hostList = computeResource.host
        for host in hostList:
            printHostInformation(datacenter, host,computeResource.name)
    except Exception as error:
        print "Unable to access information for compute resource: ",
        computeResource.name
        print error
        pass


def printDatastoreInformation(datacenter, datastore):
    try:
        summary = datastore.summary
        capacity = summary.capacity
        freeSpace = summary.freeSpace
        uncommittedSpace = summary.uncommitted
        freeSpacePercentage = (float(freeSpace) / capacity) * 100
        datastore_res_table[summary.name] = {}
        datastore_res_table[summary.name]['capacity'] = humanize.naturalsize(capacity, binary=True)
        datastore_res_table[summary.name]['free_space'] = humanize.naturalsize(freeSpace, binary=True)
        if 0:
            print "##################################################"
            print "Datastore name: ", summary.name
            print "Capacity: ", humanize.naturalsize(capacity, binary=True)
            if uncommittedSpace is not None:
                provisionedSpace = (capacity - freeSpace) + uncommittedSpace
                print "Provisioned space: ", humanize.naturalsize(provisionedSpace,
                                                                  binary=True)
            print "Free space: ", humanize.naturalsize(freeSpace, binary=True)
            print "Free space percentage: " + str(freeSpacePercentage) + "%"
            print "##################################################"
    except Exception as error:
        print "Unable to access summary for datastore: ", datastore.name
        print error
        pass


def printVmInformation(virtual_machine, depth=1):
    maxdepth = 10
    if hasattr(virtual_machine, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = virtual_machine.childEntity
        for c in vmList:
            printVmInformation(c, depth + 1)
        return

    try:
        summary = virtual_machine.summary
        print "##################################################"
        print "Name : ", summary.name
        print "MoRef : ", summary.vm
        print "State : ", summary.runtime.powerState
        print "##################################################"
    except Exception as error:
        print "Unable to access summary for VM: ", virtual_machine.name
        print error
        pass


def main():
    args = GetArgs()
    global host_res_table
    f = open("/home/aviuser/vcenter_health_info.html","w+")
    try:
        si = SmartConnectNoSSL(host=args.host, user=args.user,
                          pwd=args.password, port=int(args.port))
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        headers = ["datacenter", "Host IP", "HostCpu (GHz)", "CpuUsage (GHz)", "FreeCpu (GHz)", "HostMem (GB)", "MemUsage (GB)", "FreeMem (GB)", "FreeCpuPercent", "FreeMemPercent", "DataStore Name", "Capacity", "FreeDisk", "SSD_or_HDD", "Cluster"]
        host_res_table = prettytable.PrettyTable(headers)
        host_res_table.format = True

        for datacenter in content.rootFolder.childEntity:
            print "##################################################"
            print "##################################################"
            print "### datacenter : " + datacenter.name
            print "##################################################"

            if printVM:
                if hasattr(datacenter.vmFolder, 'childEntity'):
                    vmFolder = datacenter.vmFolder
                    vmList = vmFolder.childEntity
                    for vm in vmList:
                        printVmInformation(vm)

            if printDatastore:
                #import pdb;pdb.set_trace()
                datastores = datacenter.datastore
                for ds in datastores:
                    printDatastoreInformation(datacenter, ds)

            if printHost:
                if hasattr(datacenter.vmFolder, 'childEntity'):
                    hostFolder = datacenter.hostFolder
                    computeResourceList = hostFolder.childEntity
                    for computeResource in computeResourceList:
                        printComputeResourceInformation(datacenter, computeResource)

        #host_res_table.sortby = "FreeCpuPercent"
        host_res_table.sortby = "Cluster"
        #host_res_table.reversesort = True
        print host_res_table
        f.write(host_res_table.get_html_string())
    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1
    return 0

if __name__ == "__main__":
    main()

