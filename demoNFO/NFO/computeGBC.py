
'''
Created on Aug 12, 2014

@author: Luiza Nacshon 
'''
import os                 # OS Calls
import sys                 # System Calls
import json                # To convert to and fro from json to python objects
import heapq
import random
import time
try:
    import networkx as nx           # package to do graph manipulations
except Exception:
    #print "Please install networkX and try again"
    sys.exit()
from networkx.readwrite import json_graph
import dataWorkshop,candidatesBasedAlgorithm,utils
'''
try:
    import matplotlib.pyplot as plt  # package to draw graphs
except Exception:
    print "Please install matplotlib and try again"
    sys.exit()
'''
controllerIP = 'localhost'         
cport = '8080'

class MyTopology(object):

    def __init__(self):
        self.endDevices = {}
        self.switches = []
        self.switches_adj = {}
        self.links = {}


    def add_endDevice(self, ip, mac, to_switch, to_port):
        #Method to add End Devides. ex: hosts """
        self.endDevices[ip] = {}
        self.endDevices[ip]['mac'] = mac
        self.endDevices[ip]['to_switch'] = to_switch
        self.endDevices[ip]['to_port'] = to_port    
        
    def add_switch(self, dpid):
        #Method to add switches based on their dpid"""
        self.switches.append(dpid)


    def add_link(self, src, dst, src_port, dst_port, weight = 1):
        #Method to add link and it's attributes """
        if src not in self.switches_adj:
            self.switches_adj[src] = []
        self.switches_adj[src].append(dst)    


        #add link and it's attributes
        if src not in self.links:
            self.links[src] = {}
        self.links[src][dst] = {}
        self.links[src][dst]['src_port'] = src_port
        self.links[src][dst]['dst_port'] = dst_port
        self.links[src][dst]['weight'] = weight 

        

topology = MyTopology() # Created an empty instance of Mytopology 

def get_json(command):
    try:
       data  = os.popen(command).read()
       res = json.loads(data)
       return res
    except Exception as err:
       print "Error in Json "+str(err)
       return {}

def return_GBC(GBCval):
##### Fetch data From Controller using REST API ############################
    
    ######################## get list of all switches ##########################
    
    
    command = 'curl -s http://localhost:8080/wm/core/controller/switches/json'
    switches={}
    while True:
      if(len(switches)>0):
          break
      switches  = get_json(command)
      if(len(switches)==0):
         time.sleep(65)
    
    for i in range(len(switches)):
        switch_dpid = switches[i]['dpid']
        topology.add_switch(switch_dpid)
    #################################end #######################################
    
    ####################### get list of end devices ############################
    command = 'curl -s http://localhost:8080/wm/device/'
    
    hosts={}
    while True:
      if(len(hosts)>0):
         break
      hosts  = get_json(command)
      if(len(hosts)==0):
        time.sleep(65)
    for i in range(len(hosts)):
        if len(hosts[i]['attachmentPoint']) > 0:
                    try:
                        ipv4 = hosts[i]['ipv4'][0]
                        #print "IPV4" + " " + ipv4
                        mac = hosts[i]['mac'][0]
                        to_switch = hosts[i]['attachmentPoint'][0]['switchDPID']
                                    #print "IPV4" + " " + to_switch
                        to_port = hosts[i]['attachmentPoint'][0]['port']
                        topology.add_endDevice(ipv4, mac, to_switch, to_port)
                    except Exception:
                        print ''
                        #print 'Please do pingall so that controller will know'+ \
                      #' all host\'s ipv4 address'
                #sys.exit()
    ################################end ########################################
    print "The Network Topology:"
    print "--------------------------------------------------------"
    #for router in topology.endDevices:
        #print "Endpoint Router MAC address  {}  ".format(router)
    
        
    
    
    ################## get list of links #######################################
    command = 'curl -s http://localhost:8080/wm/topology/links/json'
    links={}
    while True:
      if(len(links)>0):
         break
      links  = get_json(command)
      if(len(links)==0):
         time.sleep(65)
    
    
    for i in range(len(links)):
        src_switch = links[i]['src-switch']
        dst_switch = links[i]['dst-switch']
        src_port = links[i]['src-port']
        dst_port = links[i]['dst-port']
        topology.add_link(src_switch,dst_switch,src_port,dst_port)
           
    
            
    ############################# end ##########################################
    
    
    ###### Create Graph from the above topoly using networkX ###################
    G = nx.Graph(name='Mininet topo of only switches') #Empty undirected graph
    # add switches
    for i in range(len(switches)):
        G.add_node(switches[i]['dpid'])
    
    #print the registered switches
    if len(G.nodes()) == 0:
        print 'No switches present'
        sys.exit()
    
    print "The Network Routers : "
    for switch in G.nodes():
        print 'Switch ==> ',switch
    
    
    mapsV={}
    counter=0
    for ro in G:
        mapsV[ro] = counter
        counter=counter+1
    
    # add links / edges 
    # networkx will take care of the two half duplex links
    for src in topology.links:
        for dst in topology.links[src]:
            G.add_edge(src,dst)
    
    Successors=[]
    
    switches_indexes = {}
    for index,switch in enumerate(G.nodes()):
        switches_indexes[switch] = index
        
    for switch in G.nodes():
        
        Successors = G.neighbors(switch) + [switch]
        indexes = []
        for switch_id in Successors:
            indexes.append(switches_indexes[switch_id])

        dw=dataWorkshop.DataWorkshop(G)
        print "Successors ",Successors
        GBCresult=candidatesBasedAlgorithm.calculateGBC(dw,indexes)
        GBCresult=  GBCresult/((len(G.nodes())-1)*1.0)
        if(GBCresult > GBCval):
            print "GBCresult",GBCresult
            return GBCresult,Successors
