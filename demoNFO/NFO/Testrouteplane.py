'''
Created on May 17, 2014

@author: lucky
'''
'''
Created on Apr 26, 2014

@author: lucky Nacshon
'''
import os
import json
import string
import netaddr
import ipaddr
from netaddr import *
from ipaddr import *
import re
import copy
from collections import OrderedDict,defaultdict
import httplib
import datetime
import csv
import time
import math
import ComputeFlowentriesMain
import os.path
import timeit

from netaddr import IPNetwork, IPAddress


class Routing(object):

    def __init__(self):
        self.ingress_egressRouters = [] #ingress egress routers to compute the route path
        self.hosts = {} #for every incoming packet we will know the output port for computing the route
        self.roters = [] 
        self.NER_routing = [] #The all routers only in NER's routing path
        self.NER_fp_routers = []
        self.NER_routerswithfpandcr = []
        self.routingMap = []
        self.counters = 1
        self.flowmod=0
        self.allRouters = []
        self.fp_wasInstalled = []
        self.prevassigment = []
        self.time  = 0
        self.fpwithfpa = []
        self.meu=0
        self.alg=''
        self.allFps = {}
        self.allFpsPrev = {}
        self.mulinemax = 0
        self.fpnames = {}
        self.router_number_fp_fa_cr = defaultdict(list)
        self.alpha = 0
        self.all_routers_cr = {}
        self.fpnamesnumber = 1
    
    def add_fpandItsfpasize(self,fp_fpa): 
        self.fpwithfpa.append(fp_fpa)
        
    def add_fponGreedy(self,list):
        self.fp_wasInstalled.append(list)
        
    def add_allrouters(self,router):
        self.allRouters.append(router)

    def add_hosts(self, ipv4,to_port,to_router,mac):

        self.hosts[ipv4] = {}
        self.hosts[ipv4]['mac'] = mac
        self.hosts[ipv4]['to_router'] = to_router
        self.hosts[ipv4]['to_port'] = to_port
        
    def add_inegrouters(self,to_router, to_port):
        new_set = [to_router,to_port]
        self.ingress_egressRouters.append(new_set)
         
    def add_routingPath_foringressegress(self,singleRlist):
        self.roters.append(singleRlist)
        
    def add_NERroutingpath(self,rotes): #be able to get output for install flow entry
        self.NER_routing.append(rotes)
    def add_NERfprouter(self,slist):
        self.NER_fp_routers.append(slist)
        
        
        
routing = Routing()

def get_json(command):
    try:
       data  = os.popen(command).read()
       res = json.loads(data)
       return res
    except Exception as err:
       print "Error in Json "+str(err)
       return {}


def get_number_of_links():
    print "get_number_of_links"
    command = 'curl -s http://localhost:8080/wm/topology/links/json'
    links={}
    links=get_json(command)
    return (len(links))



def get_userArgs(AggMethod,Algo,list_ofNERs,runID,serial,meu,alpha):
    routing.meu=meu
    routing.alpha = alpha
    getAllrouters(Algo)
    #ComputeFlowentriesMain.Compute_freeflowentries(runID,0,Algo,AggMethod)
    computeRourting()
    compute_iegressroutingPath()
    checkNERs(list_ofNERs)
    Compute_freeflowentries_setup()

    if(int(AggMethod)==1):
        Compute_fps_maximalMaximla()
 
#     elif(int(AggMethod)==2):
#         Compute_fps_MaximalAggregationOnDST()
     
    elif(int(AggMethod)==3):
        Compute_fps_MinimalMinimal()
    
    if(int(Algo)==1):
        routing.alg='NER'
        start_add_installed_Fp = timeit.default_timer()
        installFp_onNERs(list_ofNERs)
        end_add_installed_Fp = timeit.default_timer()
        add_installed_Fp_runtime = end_add_installed_Fp - start_add_installed_Fp 
        
        
    elif(int(Algo)==2):
        routing.alg='Greedy'
        compute_ca_t()
        compute_fpa_size()
        findGreegyrouters_fp()
        start_add_installed_Fp = timeit.default_timer()
        installFp_OngreedyAlgorithm(routing.fp_wasInstalled)
        end_add_installed_Fp = timeit.default_timer()
        add_installed_Fp_runtime = end_add_installed_Fp - start_add_installed_Fp 
        
    return add_installed_Fp_runtime   
        

        

def setup():
    routing.fpwithfpa = []    
    routing.fp_wasInstalled = []
    
def compute_potential_flow_assigment(all_routers_cr):
    routing.prevassigment = copy.copy(routing.fp_wasInstalled)
    setup()
    compute_ca_t()
    compute_freeflowentries_before_potential_assigment(all_routers_cr)
    compute_fpa_size()
    findGreegyrouters_fp()
    list_of_values = compute_freeflowentries_after_potential_assigment()
    ginipotentialvalue = potential_gini(list_of_values)
    return ginipotentialvalue

def no_change():
    routing.fp_wasInstalled = copy.copy(routing.prevassigment)
    for arr in routing.fpwithfpa:
        
        routing.allFpsPrev[arr[0],arr[1]] = arr[2]

def inbalance_rechange():
    to_remove=[]
    to_install = []
    for curr_deployment in routing.fp_wasInstalled:
        for prev_deployment in routing.prevassigment:
            if(curr_deployment[1][0] == prev_deployment[1][0] and curr_deployment[1][1] == prev_deployment[1][1]):
                if(curr_deployment[0]!=prev_deployment[0]):
                    temp=[]
                    temp2=[]
                    
                    temp.append(curr_deployment[0])
                    temp2.append(curr_deployment[1][0])
                    temp2.append(curr_deployment[1][1])
                    temp.append(temp2)
                    to_install.append(temp)
                    fpname = routing.fpnames[curr_deployment[1][0],curr_deployment[1][1]]
                    to_remove.append(fpname)
                

                    
                    
    for arr in routing.fpwithfpa:
        routing.allFpsPrev[arr[0],arr[1]] = arr[2]
    numberofremovedFp = len(to_remove)
    numberofnewinstalled = len(to_install)
    
    start_delete_installed_Fp = timeit.default_timer()
    delete_installed_Fp_runtime = 0 
    if(len(to_remove)>0):
        delete_installed_Fp(to_install[0],to_remove)
        end_delete_installed_Fp = timeit.default_timer()
        delete_installed_Fp_runtime = end_delete_installed_Fp - start_delete_installed_Fp
    
    start_add_installed_Fp = timeit.default_timer()
    add_installed_Fp_runtime =0
    if(len(to_install)>0):
        installFp_OngreedyAlgorithm(to_install)
        end_add_installed_Fp = timeit.default_timer()
        add_installed_Fp_runtime = end_add_installed_Fp - start_add_installed_Fp   
    
    return numberofremovedFp,numberofnewinstalled,delete_installed_Fp_runtime,add_installed_Fp_runtime
    
def compute_freeflowentries_before_potential_assigment(all_routers_cr):
    
        for i in range(0,len(routing.NER_routerswithfpandcr)):
            routers_arr = routing.NER_routerswithfpandcr[i]
    
        #for routers_arr in routing.NER_routerswithfpandcr:
            
            for router_arr in range(0,len(routers_arr[-1])):
                

                for prev_routers in routing.prevassigment:
                    if(prev_routers[0] == routers_arr[router_arr][0]):
                        
                        if((prev_routers[1][0]==routers_arr[-1][router_arr][0]) and (prev_routers[1][1]==routers_arr[-1][router_arr][1])):

                                all_routers_cr[prev_routers[0]] = all_routers_cr[prev_routers[0]] - (1 + routing.allFps[prev_routers[1][0],prev_routers[1][1]])
                                
                                
                                routing.NER_routerswithfpandcr[i][router_arr][1] = all_routers_cr[prev_routers[0]]
                               
            
        routing.all_routers_cr = copy.copy(all_routers_cr)
        
def compute_freeflowentries_after_potential_assigment():

    list_of_values=[]
    for prev_routers in routing.prevassigment:

        routing.all_routers_cr[prev_routers[0]] = routing.all_routers_cr[prev_routers[0]] + routing.allFps[prev_routers[1][0],prev_routers[1][1]] + 1
        
    for router in routing.all_routers_cr:
        list_of_values.append(routing.all_routers_cr[router])
    
    return list_of_values  
        

def potential_gini(list_of_values):
  sorted_list = sorted(list_of_values)
  height, area = 0, 0
  for value in sorted_list:
    height += value
    area += height - value / 2.
  fair_area = height * len(list_of_values) / 2
  return (fair_area - area) / fair_area
        

    
        
def getAllroutersPrerun(Algo):
     print "getAllroutersPrerun"
     command = 'curl -s http://localhost:8080/wm/core/controller/switches/json'
     switches={}
     while True:
       if(len(switches)>0):
          break
       switches  = get_json(command)
       if(len(switches)==0):
          time.sleep(60)
     for i in range(len(switches)):
         switch_dpid = switches[i]['dpid']
         routing.add_allrouters(switch_dpid)
     if(int(Algo)==1):
         try:
             os.remove(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt")  
         except:
             print "" 
         file = open(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt", "a")
     elif(int(Algo)==2):
         try:
             os.remove(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt")  
         except:
             print "" 
         file = open(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt", "a")

     for i in routing.allRouters:
         file.write(i+'\n')
     file.close()

def getAllrouters(Algo):
     print "getAllrouters"
     command = 'curl -s http://localhost:8080/wm/core/controller/switches/json'
     switches={}
     while True:
       if(len(switches)>0):
          break
       switches  = get_json(command)
       if(len(switches)==0):
          time.sleep(60)
     for i in range(len(switches)):
         switch_dpid = switches[i]['dpid']
         routing.add_allrouters(switch_dpid)
     if(int(Algo)==1):
         try:
             os.remove(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt")  
         except:
             print "" 
         file = open(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt", "a")
     elif(int(Algo)==2):
         try:
             os.remove(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt")  
         except:
             print "" 
         file = open(os.getcwd() + '/' +   "Greedy_NER/allrouters.txt", "a")

     for i in routing.allRouters:
         file.write(i+'\n')
     file.close()

def computeRourting():
    print "computeRourting"

    command = 'curl -s http://localhost:8080/wm/device/'
    hosts={}
    while True:
      if(len(hosts)>0):
        break
      hosts  = get_json(command)
      if(len(hosts)==0):
        time.sleep(60)
    template = "{0:30}    {1:2}    {2:15}" # column widths: 8, 10, 15, 7, 10
    print template.format("Endpoint_MAC_Address","Port","Subnets") # header
    print "---------------------------------------------------------"
    print '\r'
    for i in range(len(hosts)):
        if len(hosts[i]['attachmentPoint']) > 0:
                    try:
                        ipv4 = hosts[i]['ipv4'][0]
                        mac = hosts[i]['mac'][0]
                        to_router= hosts[i]['attachmentPoint'][0]['switchDPID']
                        to_port = hosts[i]['attachmentPoint'][0]['port']
                        if ((to_port > 0) and (len(ipv4)>0)):

                            print template.format(to_router,to_port,ipv4)
                            
                            routing.add_hosts(ipv4,to_port,to_router,mac)
                            routing.add_inegrouters(to_router, to_port)
                        
                    except Exception:
                        continue
                    
#Now we will find the routing path 
def compute_iegressroutingPath():
    
    for i in routing.ingress_egressRouters:
        
        k = 0 
        for z in i:
            if k == 0:
                src_router=z
                k=k+1
            else:
                src_port=z
                k=0
        
        for j in routing.ingress_egressRouters:
            if i <> j:
                for z in j:
                    if k == 0:
                        dst_router=z
                        k=k+1
                    else:
                        dst_port=z
                        k=0
                if src_router<>dst_router:
                    print "ingress egress"  
                    command = "curl -s http://localhost:8080/wm/topology/route/%s/%s/%s/%s/json" % (src_router, src_port, dst_router, dst_port)
                    routpathset = []
                    parsedResult={}
                    while True:
                       print "while"
                       if(len(parsedResult)>0):
                          print "break"
                          break
                       parsedResult=get_json(command)
                       if(len(parsedResult)==0):
                          time.sleep(60)
                    for i in range(len(parsedResult)):
                        print "starting loop"
                        l=0
                        if i % 2 == 0:
                            singlerouterlist = []
                            router = parsedResult[i]['switch']
                            inputport = parsedResult[i]['port']
                            a = router
                            singlerouterlist.append(a)
                            a = inputport
                            singlerouterlist.append(a)
                            
                        else:
                            l=l+1
                            router = parsedResult[i]['switch']
                            outputport = parsedResult[i]['port']
                            a = outputport
                            singlerouterlist.append(a)
                            routpathset.append(singlerouterlist)
                   
                    routing.add_routingPath_foringressegress(routpathset)
                    #routing.add_NERfprouter(routpathset)

     
        
def checkNERs(NERs):
    #print "routing.roters!!!!!!!!!!!!!!!",routing.roters
    temp = []
    temp2 = []
    for l in routing.roters:
        temp = []
        
        count = 0
        for u in l:
            
            temp.append(u[0])
        if (temp not in temp2):
            temp2.append(temp)
    #print temp2,"temp"
       
    path = 0
    for l in NERs:
        for i in temp2:
        
            
            routepath = []
            for j in i:
                n=0
                
                if (n == 0):
                    if (j == l):
                        path=1
                    n = 1
                #print "jjj",j
                routepath.append(j)
            if (path==1):
                path = 0
                #print "routepath",routepath
                if (routepath not in routing.NER_routing):
                    routing.add_NERroutingpath(routepath) 

    routing.NER_fp_routers = copy.copy(routing.NER_routing)  
           
def compute_routepathOnlyrouters(): #with fp and Cr
    
    
    routing.NER_fp_routers = copy.copy(routing.NER_routing)
    for i in routing.NER_fp_routers:
        k=0
        for j in i[0]: # route list
            if (k==0):
                k=1
                p = j
        k=0
        for v in i[-1]:
            if (k == 0) :
                k=1
                n = v  
        for w in routing.NER_fp_routers:
            if (w<>i):

                k=0
                for l in w[0]:
                    if(k==0):
                        p1 = l
                        k=1
                k=0
                for g in w[-1]:
                    if (k==0):
                        n1 = g
                        k=1
                if((p==p1) and (n==n1)):
                    routing.NER_fp_routers.remove(w)
                  
    routing.NER_fp_routers.remove(routing.NER_fp_routers[-1])
    
#     for k in routing.NER_fp_routers:
#         for j in k:
#             j.remove(j[1])
#             j.remove(j[1])

            
                        
def compute_ca_t():
   if os.path.exists(os.getcwd() + '/' +   "Greedy_NER/Computemu.csv") ==True:
       #routing.meu
       i=0
       if(routing.mulinemax==0): #first time
           for src_dst in routing.allFps:
               routing.allFps[src_dst] = 0
       src_dst_counter = {}
       with open(os.getcwd() + '/' +   "Greedy_NER/Computemu.csv") as f:
            for line in f:
                i+=1
                
                if(i<=routing.mulinemax):
                    continue
                tokens = [t.strip() for t in line.split(';')]
                try:
                    src=str(tokens[0])
                    dst=str(tokens[1])
                    value = int(tokens[2])
        
                except:

                    continue
                for src_dst in routing.allFps:
                    try:
                        if(IPAddress(src) in IPNetwork(src_dst[0]) and IPAddress(dst) in IPNetwork(src_dst[1])):
                           routing.allFps[src_dst] += value#adding mu
                           print "value ",value
                           print "routing.allFps[src_dst] ",src_dst,routing.allFps[src_dst]
                           break
                    except:
                        print "invalid print to mue file"

           
       routing.mulinemax=i
       print "routing.mulinemax ",routing.mulinemax
#if IPAddress("192.168.0.1") in IPNetwork("192.168.0.0/24"):
   if os.path.exists(os.getcwd() + '/' +   "Greedy_NER/Computemu.csv") ==False:
       #routing.meu
       
       for src_dst in routing.allFps:
           routing.allFps[src_dst] = routing.meu


    
def Compute_fps_maximalMaximla():
    for i in routing.NER_routerswithfpandcr: #get routers between s and t
 
        s_hosts = []
        t_hosts = []
        fp_s_t = []
        temp=[]
        
        for ipv in routing.hosts:
            router = format(routing.hosts[ipv]['to_router'])
            #print "i[1][0][0],i[1][-1][0]",i[1]
            if (router==format(i[0][0])): #s
                s_hosts.append(ipv)
            if (router == i[-1][0]):#t
                t_hosts.append(ipv)
         
        fp_s = Compute_aggregationForIPs(s_hosts)
        fp_t = Compute_aggregationForIPs(t_hosts)
        fp_s_t.append(fp_s)
        fp_s_t.append(fp_t)
        n=format(fp_s_t[0])
        e=format(fp_s_t[1])
        routing.allFps[n,e] = 0
        i.sort(reverse=True,key = lambda row: row[1])
        temp.append(fp_s_t)
        i.append(temp)
    
def sort_byfpa():
    
    routing.fpwithfpa.sort(reverse=True,key = lambda row: row[2])
     
#compute potential active flow for each fp
#sort the ruters by C_r later -  install the fp with the highest 
def findGreegyrouters_fp():

    sort_byfpa()  
    #print "routing.fpwithfpa!!!!",routing.fpwithfpa
    try:
        os.remove(os.getcwd() + '/' +   "Greedy_NER/selectedrouters.txt")  
    except: 
        print ""   
    fp_wasInstalled = []
    temp = []
    temp2=[]
    fp_a=0
    
    for fp in routing.fpwithfpa:
        #print "!!!!!!! ,fpwithfpa" ,routing.NER_routerswithfpandcr
        found = False
        for i in routing.NER_routerswithfpandcr:
            #print "i[-1]",i[-1]
            for j in range(0,len(i[-1])):
                if((fp[0]==i[-1][j][0]) and (fp[1]==i[-1][j][1])):
                    found = True
                    #print "EQUALLLL!!!",fp[0],i[-1][j][0],fp[1],i[-1][j][1]
                    first=i[-1][j][0].split('/')
                    second = i[-1][j][1].split('/')
                    #fp_aandfp=(1+routing.meu*(math.pow(2, 32-int(first[1]))*math.pow(2, 32-int(second[1]))))
                    #print math.pow(2, 32-int(first[1])),math.pow(2, 32-int(second[1])),i[0][1] #cr
                    #print "sum  ", math.ceil(fp_aandfp),fp_aandfp,i[0][0]
                    highest_crRouter = i[0][0]
                    temp.append(i[0][0])
                    temp2.append(i[-1][j][0])
                    temp2.append(i[-1][j][1])
                    
                    temp.append(temp2)
                    routing.add_fponGreedy(temp)
                    temp=[]
                    temp2=[]
                    
                    file = open(os.getcwd() + '/' +   "Greedy_NER/selectedrouters.txt", "a")
                    file.write(highest_crRouter+'\n')
                    file.close() 
                    for l in routing.NER_routerswithfpandcr:
                        k=[]
                        if (l[0][0]==highest_crRouter):
                                k=l[-1][:]
                                l.remove(l[-1])
                                #print "l[0][0], highest_crRouter",l[0][0], highest_crRouter,l[0][1]
                                l[0][1] = l[0][1] - int(math.ceil(fp[2]))
                                
                                l.sort(key = lambda row: row[1],reverse=True)
                                l.append(k)
                                #except:
                    break
                                    #continue
            if(found==True):
                found  = False
                break
    #print "fp_wasInstalled!!!",routing.fp_wasInstalled

  
           
def compute_fpa_size():
    
    for src_dst_fp_pair in routing.allFps:
        
        srcMask=src_dst_fp_pair[0].split('/')
        dstMask = src_dst_fp_pair[1].split('/')
        if os.path.exists(os.getcwd() + '/' +   "Greedy_NER/Computemu.csv") ==False:
            fp_aandfp=(1+routing.meu*(math.pow(2, 32-int(srcMask[1]))*math.pow(2, 32-int(dstMask[1]))))
            try:
                routing.allFpsPrev[src_dst_fp_pair[0],src_dst_fp_pair[1]] = fp_aandfp
            except:
                print "no key "
                fp_aandfp = 0
            #routing.allFps[src_dst_fp_pair] = fp_aandfp
        else:
            try:
                fp_aandfp = routing.alpha * routing.allFpsPrev[src_dst_fp_pair] + (1-routing.alpha)*(routing.allFps[src_dst_fp_pair]+1)
            
                print "routing.allFps[src_dst_fp_pair] ",routing.allFps[src_dst_fp_pair]
                print "routing.allFpsPrev[src_dst_fp_pair] ",routing.allFpsPrev[src_dst_fp_pair]
            except:
                print "no key"
                fp_aandfp = 0
#t-prev time
#mue(t+1)  = alpha*(m(t))+ (1-alpha)*(c_at+1c_fp)
#fp_aandfp(t+1) = routing.alpha * routing.allFpsPrev[src_dst_fp_pair] + (1-routing.alpha)*(routing.allFps[src_dst_fp_pair]+1)

      
        temp2 = []
        temp2.append(src_dst_fp_pair[0])
        temp2.append(src_dst_fp_pair[1])
        temp2.append(math.ceil(fp_aandfp))
        routing.add_fpandItsfpasize(temp2)
        print "src_dst_fp_pair ",src_dst_fp_pair
        print "meu (t+1)",fp_aandfp
        
      
        #print "fpwithfpa!!",routing.fpwithfpa
        #print "router ingress and egress",i[0][0],i[-1][0]
        #print "s",s_hosts, "t", t_hosts
        #print fp_s,fp_t


def Compute_aggregationForIPs(ips): #calculates aggregation for splitting algorithm
                 
      #Look at larger and smaller IP addresses
      ips = [ipaddr.IPAddress(ip) for ip in ips]
      lowest_ip, highest_ip = min(ips), max(ips)
     
      mask_length = ipaddr._get_prefix_length(
        int(lowest_ip), int(highest_ip), lowest_ip.max_prefixlen)
      mask_length =  mask_length
      #Return the network
      network_ip = ipaddr.IPNetwork("%s/%d" % (lowest_ip, mask_length)).network
      network = ipaddr.IPNetwork("%s/%d" % (network_ip, mask_length), strict = True)
      return str(network)
  


#         with open(ros.getcwd() + '/' +   "PWorkspace/NFO/flowentries.csv", "a") as csv_file:
#             writer = csv.writer(csv_file, delimiter =",",quoting=csv.QUOTE_MINIMAL)
#             writer.writerow([now,routers,entries])
#         csv_file.close()
def find_minimalIP(ips):
    min = ips[0]
    min_octet = int(min.split('.')[-1])
    max = ips[0]
    max_octet = int(max.split('.')[-1])
    for i in ips:
        
        if (int(i.split('.')[-1]) < min_octet):
            min = i
            min_octet = int(i.split('.')[-1])
        if (int(i.split('.')[-1]) > max_octet):
            max = i
            max_octet = int(i.split('.')[-1])
    #print "!!!!!",min,max,min_octet,max_octet
    ip_range=max_octet - min_octet
    masklength = 32 - ip_range.bit_length()
    #print masklength 
    fp = min + "/" + str(masklength)
    return fp  
def Compute_split(txt): #for now will work only network mask 255.255.255.0
    #ips with different len will be calculated in a group
    return len(bin(int(txt.split('.')[-1]))[2:])

def check_equal_prefix(ip1,ip2):
    
    firstip = bin(int(ip1.split('.')[-1]))[2:]
    secondip = bin(int(ip2.split('.')[-1]))[2:]
    #print "first ip and second",firstip,secondip
    firstip = firstip[:-1]
    secondip= secondip[:-1]
    #print "after cut",firstip ,secondip
    if(secondip == firstip):
        
        return 1
    else:
        
        return 0
        
def Compute_splitfp(s):
    file = open(os.getcwd() + '/' +   "Greedy_NER/ipbetweenNER.txt", "a")
    #s = ['10.0.0.31','10.0.0.32','10.0.0.33','10.0.0.34','10.0.0.35','10.0.0.36','10.0.0.37','10.0.0.38','10.0.0.39','10.0.0.40']
    file.write("s!!"+ format(s) + '\n')
    w = []
    e = []
    for i in s:
        t=[]
        s1=copy.copy(s)
        
        file.write("s!!"+ format(s) + '\n')
        file.write("i!!"+ format(i) + '\n')
        for j in s1:
            
            if(i<>j):
                
                file.write("j!!"+ format(j) + '\n')
                #print "before",Compute_split(i),Compute_split(j)
                if (Compute_split(i) == Compute_split(j)):
                     #print "yes",Compute_split(i),Compute_split(j)
                     if(check_equal_prefix(i,j)==1):
                         t.append(j)
                         t.append(i)
                         s.remove(j)
                         s.remove(i)
                         break
                         
        #print "t",t
        #t.append(i)
        #s.remove(i)
    
        if(len(t)<>0):
            w.append(t)
        #print "s",s
    if(len(s)<>0):
        for i1 in s:
            x = [i1]
            w.append(x)
    file.write("WWWW!!"+ format(w) + '\n')
    #print w

    for i1 in w:
        x = find_minimalIP((i1))
        file.write("xxxx!!"+ format(x) + '\n')
        e.append(x)
    file.write("eee!!"+ format(e) + '\n')
    file.close() 
    return e


    
def Compute_fps_MinimalMinimal():
    
    
    for i in routing.NER_routerswithfpandcr: #get routers between s and t
        s_hosts = []
        t_hosts = []
        fp_s_t = []
        fp_s_t1 = []

        for ipv in routing.hosts:
            router = format(routing.hosts[ipv]['to_router']) 
            
            if (router==format(i[0][0])): #s
                s_hosts.append(ipv)
                
            if (router == i[-1][0]):#tif((i[0][0],i[-1][0]) not in ipvadded):
                t_hosts.append(ipv)
                

        #print "s_hosts!!",s_hosts

        #print "t_hosts!!",t_hosts
        setfp_s = Compute_splitfp(s_hosts)
        setfp_t = Compute_splitfp(t_hosts)
        
        
        for n in setfp_s:
            for e in setfp_t:
                fp_s_t1.append(n)
                fp_s_t1.append(e)
                fp_s_t.append(fp_s_t1)
                fp_s_t1=[]
                #print fp_s_t
                srcMask=n.split('/')
                dstMask = e.split('/')
                fp_aandfp=(1+routing.meu*(math.pow(2, 32-int(srcMask[1]))*math.pow(2, 32-int(dstMask[1]))))
                temp = []
                temp.append(n)
                temp.append(e)
                temp.append(math.ceil(fp_aandfp))
                routing.add_fpandItsfpasize(temp)
                #print "fpwithfpa!!",routing.fpwithfpa
        #print "router ingress and egress",i[0][0],i[-1][0]
        #print "s",s_hosts, "t", t_hosts
        #print fp_s_t
        i.sort(reverse=True,key = lambda row: row[1])
        i.append(fp_s_t)
    
    
def Compute_freeflowentries_setup():
        routers = ""
        entries=""
        #current Floodlight bug for every installed entry we have one extra 9 flows entries
        
        try:
            command = 'curl -s http://localhost:8080/wm/core/switch/all/table/json'
            tables={}
            while True:
              if(len(tables)>0):
                 break
              tables  = get_json(command)
              if(len(tables)==0):
                 time.sleep(60)
            
    
            for i in routing.NER_fp_routers:
                routersinrouting = []
                #print i
                for n in i:
                    #print n
                    singlerouter = []
                    for j in tables[n]:#read from the Json for each router
                        if (int(j['tableId']) == 0):
                            free_entries=(int(j['maximumEntries'])-(int(j['activeCount'])-9))
                            singlerouter.append(n)
                            routers=format(n) + "," + routers
                            singlerouter.append(free_entries)
                            entries = format(free_entries) + "," + entries
                    routersinrouting.append(singlerouter)
                    now = datetime.datetime.now()
                
                routing.NER_routerswithfpandcr.append(routersinrouting)   
        except:
            print "jason error setup"
            
def installFp_OngreedyAlgorithm(to_install):
     
     routing.counters = 1
     selectedRFp=[]
     #print "installFp_greedyalgorithm"
     for i in to_install:#routing.fp_wasInstalled:
         install_Fp(i[0],i[1][0],i[1][1],"fp"+format(routing.fpnamesnumber))
         routing.fpnamesnumber +=1
         routing.counters=routing.counters+1
         if not i[0] in selectedRFp:
             selectedRFp.append(format(i[0]))
     now = datetime.datetime.now()
     srfp = ('|').join(i for i in selectedRFp)
     with open(os.getcwd() + '/' +   "Greedy_NER/InstallStaticfp.csv", "w") as csv_file:
         writer = csv.writer(csv_file,delimiter = ',',quoting=csv.QUOTE_MINIMAL)
         writer.writerow([now,routing.counters-1,srfp,len(selectedRFp)])
     csv_file.close()

def installFp_onNERs(NERs):
     selectedRFp = []
     installedFlows = []
     installedpath = []
     temp = []
     #check if selected NERs on the same routing path
     #if(len(NERs)>1):
         #Check_If_NERS_on_the_same_path(NERs)
         
     #print "installFp_NERs"
     for l in NERs:
         for i in routing.NER_routerswithfpandcr:
             for n in i:
                 #print "NER",n[0],l
                 if (i not in installedpath):
                     if(l in n[0]):
                         #print "YES!!",i,"i","  ",installedpath
                         installedpath.append(i)
                         for j in range(0,len(i[-1])):
                             #if (([i[-1][j][0],i[-1][j][1]]) not in installedFlows):
                                 #print "installedflows",installedFlows,i[-1][j][0],i[-1][j][1]
                              temp.append(i[-1][j][0])
                              temp.append(i[-1][j][1])
                              installedFlows.append(temp)
                              temp=[]
                              #print "INSTALL NER",i[-1][j][0],i[-1][j][1]
                              install_Fp(l,i[-1][j][0],i[-1][j][1],"fp"+format(routing.counters))
                                 #routing.counters=routing.counters+1
                                 #install_Fp('00:00:00:00:00:00:00:01',i[-1][j][1],i[-1][j][0],"fp"+format(routing.counters))
                              routing.counters=routing.counters+1
                         if l not in selectedRFp:
                                 selectedRFp.append(format(l))
                     #break
     now = datetime.datetime.now()
     with open(os.getcwd() + '/' +   "Greedy_NER/InstallStaticfp.csv", "a") as csv_file:
         writer = csv.writer(csv_file, delimiter =";",quoting=csv.QUOTE_MINIMAL)
         writer.writerow([now,routing.counters-1,selectedRFp,len(selectedRFp)])
     csv_file.close()
                 

def delete_installed_Fp(routerID,to_remove):
    print "############3 in delete"
    for fpname in to_remove:
        command = 'curl -X  DELETE -d ' + '\'' + '{"name":' + '"' + fpname + '"' + "}"  + '\'' + '   http://localhost:8080/wm/staticflowentrypusher/json'
        #curl -X DELETE -d '{"name":"flow-mod-1"}' http://<controller_ip>:8080/wm/staticflowpusher/json         
        data  = os.popen(command)
    
        time.sleep(2)
        try:
	    s_name  = str(routerID).split(':')[-1]
	    s_id = int(s_name,16)
	    os.system("sudo ovs-vsctl del-flows " +  "s" + format(s_id))
	except:
            print "ERROR DELETE FLOWS!!!!!!!"
    
    
    
def install_Fp(routerID,src,dst,fpname):
    
    routing.fpnames[src,dst] = fpname
    #writer = csv.writer(open(os.getcwd() + '/' +   "PWorkspace/NFO/Controlmessages2.csv", "a"))
    try:
	s_name  = str(routerID).split(':')[-1]
	s_id = int(s_name,16)
	os.system("sudo ovs-vsctl del-flows " +  "s" + format(s_id))
    except:
        print "ERROR DELETE FLOWS!!!!!!!"
    command = 'curl -d  ' + '\'' + '{"switch":' + '"'+ routerID +  '"' + ', "name":' + '"' + fpname + '"' + ',' + \
                    '"cookie":"0",' + '"priority": "49",' + '"ether-type":"2048",' + \
                    '"src-ip":' + '"' + src + '"' + ','  \
                    '"dst-ip":' + '"' + dst + '"' + ','  \
                   + '"active"' + ':' + '"true"' + ',' + '"actions":"output=controller"}'  + '\'' \
                    + '   http://localhost:8080/wm/staticflowentrypusher/json'

     

    file = open(os.getcwd() + '/' +   "Greedy_NER/fps.txt", "a")
    file.writelines(src + ' ' + dst + '\n')
    file.close() 
    print "Install the flows which should be monitored"
    template = "{0:20}    {1:5}    {2:2}    {3:15}    {4:15}" # column widths: 8, 10, 15, 7, 10
    print template.format("Router-MAC","Flow-Name","Priority","src-IP","dst-IP") # header
    print "--------------------------------------------------------------------------------"
    print template.format(routerID,fpname,'49',src,dst)

    data  = os.popen(command)
    
    time.sleep(2)
   
    
'[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[-'    
            
