from __future__ import print_function
import sys
import libvirt
import time
import socket
from xml.dom import minidom

print("Monitor running...........")

conn = libvirt.open('qemu:///system')
if conn==None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)

domainsID = ['lubuntu_vm1', 'lubuntu_vm2']
domainIPs = ['192.168.122.5', '192.168.122.9']
domainObj = []
for domainID in domainsID:
    domain = conn.lookupByName(domainID)
    if domain == None:
        print('Failed to get the domain object', file=sys.stderr)
    elif domain.name().startswith('lubuntu_vm'):
        domainObj.append(domain)

vm_IP_index = 0
vm_util_index = 0
stress_counter = 0

def getIP():
    global vm_IP_index
    print("Getting IP for "+domainObj[vm_IP_index].name())
    dom_ip=domainIPs[vm_IP_index]
    vm_IP_index+=1
    return dom_ip

def getCpuUtil():
    global vm_util_index
    global stress_counter
    flag = domainObj[vm_util_index+1].isActive()
    cpuStats = domainObj[vm_util_index].getCPUStats(True)
    cpuTime1 = cpuStats[0]['cpu_time']
    cpuTime1B = 0
    if flag:
        cpuStats = domainObj[vm_util_index+1].getCPUStats(True)
        cpuTime1B = cpuStats[0]['cpu_time']
    time.sleep(1)
    cpuStats = domainObj[vm_util_index].getCPUStats(True)
    cpuTime2 = cpuStats[0]['cpu_time']
    cpuTime2B = 0
    if flag:
        cpuStats = domainObj[vm_util_index+1].getCPUStats(True)
        cpuTime2B = cpuStats[0]['cpu_time']
    cpuUtil = (cpuTime2-cpuTime1)/10000000
    print('CPU Utilization for '+domainObj[vm_util_index].name()+' is '+str(round(cpuUtil,2))+'%')
    if flag:
        cpuUtil2 = (cpuTime2B-cpuTime1B)/10000000
        print('CPU Utilization for '+domainObj[vm_util_index+1].name()+' is '+str(round(cpuUtil2,2))+'%')
    if cpuUtil > 80:
        stress_counter+=1
    else:
        stress_counter=0
    print()
    return cpuUtil

def activateDomain():
    if domainObj[vm_IP_index].isActive():
        print(domainObj[vm_IP_index].name()+" is active")
    else:
        print(domainObj[vm_IP_index].name()+" is inactive. Activating....")
        id = domainObj[vm_IP_index].create()
        if id < 0:
            print('Unable to create guest ', file=sys.stderr)

monitor_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
monitor_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
monitor_server.bind(('', 5050))
monitor_server.listen()
conn_obj, client_addr = monitor_server.accept()
print(str(client_addr) +" connected")
format = 'utf-8'
while True:
    msg = conn_obj.recv(100).decode(format)
    if msg == "fetchIP":
        res = getIP()
        conn_obj.send(str(res).encode(format))
    else:
        while True:
            try:
                cpuUtil = getCpuUtil()
                if cpuUtil > 80 and vm_IP_index < 2 and stress_counter > 4:
                    stress_counter = 0
                    activateDomain()
                    print("Activation Done")
                    time.sleep(10)
                    res = getIP()
                    conn_obj.send(str(res).encode(format))
                else:
                    conn_obj.send("".encode(format))
            except KeyboardInterrupt:
                print("Closing Monitor")
                conn_obj.close()
                conn.close()
                exit()
