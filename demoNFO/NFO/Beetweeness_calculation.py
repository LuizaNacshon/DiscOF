'''
Created on Aug 12, 2014

@author: Luiza Nacshon 
'''
import os                 # OS Calls
import sys                 # System Calls
import json                # To convert to and fro from json to python objects
import heapq
import random
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


##### Fetch data From Controller using REST API ############################

######################## get list of all switches ##########################
try:
    command = 'curl -s http://localhost:8080/wm/core/controller/switches/json'

except Exception:
    print "make sure that the controller is running"
    sys.exit()

data  = os.popen(command).read()
switches = json.loads(data)

for i in range(len(switches)):
    switch_dpid = switches[i]['dpid']
    topology.add_switch(switch_dpid)
#################################end #######################################

####################### get list of end devices ############################
command = 'curl -s http://localhost:8080/wm/device/'
data  = os.popen(command).read()
hosts = json.loads(data)
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
data  = os.popen(command).read()
links = json.loads(data)


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

# print all edges and links
verticesn=0
f = open("/home/lucky/test37.txt","a")

for src, dst in G.edges():
    
    verticesn=verticesn+1
    print "Edge/link  {} <==> {} ".format(src,dst)
    f.write(format(mapsV[src]) + ' ' + format(mapsV[dst]) + ' '+ format(1) + '\n')

#create topology .txt

f.close()

# Successors=[]
# u=0
# for switch in G.nodes():
#     Successors.append(G.neighbors(switch))


# WC=[]
# statusBar=False
# dw=dataWorkshop.DataWorkshop(G)
# print dw
# alg=candidatesBasedAlgorithm.calculateGBC(dw,[0,0])
# print alg
# for v in G:
#     print 'V',v
#     for w in G[v]:
#         print 'W',w


__all__ = ['betweenness_centrality',
           'edge_betweenness_centrality',
           'edge_betweenness']
k=None
normalized=True
weight=None
endpoints=True
seed=None



def betweenness_centrality(ners):
    k=None 
    normalized=True
    weight=None
    endpoints=False 
    seed=None
   
    betweenness=dict.fromkeys(G,0.0) # b[v]=0 for v in G
    if k is None:
        nodes = G
    else:
        random.seed(seed)
        nodes = random.sample(G.nodes(), k)
    for s in nodes:
        # single source shortest paths
        if weight is None:  # use BFS
            #S,P,sigma=_single_source_shortest_path_basic(G,s)
        #else:  # use Dijkstra's algorithm
            S,P,sigma=_single_source_dijkstra_path_basic(G,s,weight)
        # accumulation
        if endpoints:
            betweenness=_accumulate_endpoints(betweenness,S,P,sigma,s)
        else:
            betweenness=_accumulate_basic(betweenness,S,P,sigma,s)
    # rescaling
    betweenness=_rescale(betweenness, len(G),
                         normalized=normalized,
                         directed=G.is_directed(),
                         k=k)
    #print 'betweenness ',betweenness
    #ners=['00:00:00:00:00:00:00:01']
    beetresult=[]
    for t in range(0,len(ners)):
        #print 'NERS',ners,t,betweenness
        beetresult.append(betweenness[ners[t]])
    #print 'beetresult',beetresult
    #return betweenness
    return beetresult

# helpers for betweenness centrality

def _single_source_shortest_path_basic(G,s):
    S=[]
    P={}
    for v in G:
        P[v]=[]
    sigma=dict.fromkeys(G,0.0)    # sigma[v]=0 for v in G
    D={}
    sigma[s]=1.0
    D[s]=0
    Q=[s]
    while Q:   # use BFS to find shortest paths
        v=Q.pop(0)
        S.append(v)
        Dv=D[v]
        sigmav=sigma[v]
        for w in G[v]:
            if w not in D:
                Q.append(w)
                D[w]=Dv+1
            if D[w]==Dv+1:   # this is a shortest path, count paths
                sigma[w] += sigmav
                P[w].append(v) # predecessors 
    return S,P,sigma



def _single_source_dijkstra_path_basic(G,s,weight='weight'):
    # modified from Eppstein
    S=[]
    P={}
    for v in G:
        P[v]=[]
    sigma=dict.fromkeys(G,0.0)    # sigma[v]=0 for v in G
    D={}
    sigma[s]=1.0
    push=heapq.heappush
    pop=heapq.heappop
    seen = {s:0}
    Q=[]   # use Q as heap with (distance,node id) tuples
    push(Q,(0,s,s))
    while Q:
        (dist,pred,v)=pop(Q)
        if v in D:
            continue # already searched this node.
        sigma[v] += sigma[pred] # count paths
        S.append(v)
        D[v] = dist
        for w,edgedata in G[v].items():
            vw_dist = dist + edgedata.get(weight,1)
            if w not in D and (w not in seen or vw_dist < seen[w]):
                seen[w] = vw_dist
                push(Q,(vw_dist,v,w))
                sigma[w]=0.0
                P[w]=[v]
            elif vw_dist==seen[w]:  # handle equal paths
                sigma[w] += sigma[v]
                P[w].append(v)
    return S,P,sigma

def _accumulate_basic(betweenness,S,P,sigma,s):
    delta=dict.fromkeys(S,0)
    while S:
        w=S.pop()
        coeff=(1.0+delta[w])/sigma[w]
        for v in P[w]:
            delta[v] += sigma[v]*coeff
        if w != s:
            betweenness[w]+=delta[w]
    return betweenness

def _accumulate_endpoints(betweenness,S,P,sigma,s):
    betweenness[s]+=len(S)-1
    delta=dict.fromkeys(S,0)
    while S:
        w=S.pop()
        coeff=(1.0+delta[w])/sigma[w]
        for v in P[w]:
            delta[v] += sigma[v]*coeff
        if w != s:
            betweenness[w] += delta[w]+1
    return betweenness

def _accumulate_edges(betweenness,S,P,sigma,s):
    delta=dict.fromkeys(S,0)
    while S:
        w=S.pop()
        coeff=(1.0+delta[w])/sigma[w]
        for v in P[w]:
            c=sigma[v]*coeff
            if (v,w) not in betweenness:
                betweenness[(w,v)]+=c
            else:
                betweenness[(v,w)]+=c
            delta[v]+=c
        if w != s:
            betweenness[w]+=delta[w]
    return betweenness

def _rescale(betweenness,n,normalized,directed=False,k=None):
    if normalized is True:
        if n <=2:
            scale=None  # no normalization b=0 for all nodes
        else:
            scale=1.0/((n-1)*(n-2))
    else: # rescale by 2 for undirected graphs
        if not directed:
            scale=1.0/2.0
        else:
            scale=None
    if scale is not None:
        if k is not None:
            scale=scale*n/k
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness

def _rescale_e(betweenness,n,normalized,directed=False):
    if normalized is True:
        if n <=1:
            scale=None  # no normalization b=0 for all nodes
        else:
            scale=1.0/(n*(n-1))
    else: # rescale by 2 for undirected graphs
        if not directed:
            scale=1.0/2.0
        else:
            scale=None
    if scale is not None:
        for v in betweenness:
            betweenness[v] *= scale
    return betweenness

#betweenness_centrality(G, k, normalized, weight, endpoints, seed)