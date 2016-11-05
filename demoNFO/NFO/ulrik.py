import random
import utils
from  numpy import *
import abstractGroupEvaluation
import candidatesBasedAlgorithm
from networkx.readwrite import json_graph

class WeightedUlrik:
    """
    Betweenness calculation based on
    Ulrik Brandes' "Faster Algorithm for Betweenness Centrality" 2001.
    Algorithm was modified to inlude end points in path counting
    Algorithm was modified to compute Group Betweenness Centrality of a given group.
    Algorithm was generalized to accomodate "Communication Weights" (network usage habits).
    """
    
    def __init__(self, graph, CW=utils.DefaultCommMatrix(), statusBar=False, group=set([])):
        #assert isinstance(graph,Graph) #TODO
        self._group=group
        self._GB = 0
        
        #n = graph.getNumberOfVertices()


        n=len(graph.nodes())
        
        m=len(graph.edges())
        #m = graph.getNumberOfEdges()
        
        
        V = range(n)
        print 'V',V
        self._G = graph
        self._distance=      ndarray.__new__(ndarray,shape=(n,n),dtype=integer,order='C')
        self._deltaDot=      ndarray.__new__(ndarray,shape=(n,n),dtype=float  ,order='C')
        self._sigma=         ndarray.__new__(ndarray,shape=(n,n),dtype=integer,order='C')
        self._routingTable = ndarray.__new__(ndarray,shape=(n,n),dtype=object ,order='C')
        
        mapsV={}
        counter=0
        for ro in self._G:
           mapsV[ro] = counter
           counter=counter+1

           
            
            
        
        Successors=[]

        for switch in self._G.nodes():
            Successors.append(len(self._G.neighbors(switch)))
        
        print 'successors',Successors
        progressCount = 0
        for s in V:
            if statusBar:
                progressCount+=1
                statusBar.updateStatus("%d %%"%(100.0*progressCount/n))
    
            S = []
            #P = array([None for w in V],object,order='C');
            P = ndarray.__new__(ndarray,shape=(n),dtype=object,order='C');
            for i in xrange(n):P[i]=[];
            sigma = array([0 for t in V],integer,order='C') 
            #sigma = ndarray.__new__(ndarray,shape=(n),dtype=integer,order='C');
            #sigma.fill(0);
            sigma[int(s)] = 1
            d = array([NaN for t in V],float,order='C')
            #d = ndarray.__new__(ndarray,shape=(n),dtype=float,order='C')
            #d.fill(NaN)
            d[int(s)]=0
            delta = array([0.0 for t in V],float,order='C')
            #delta = ndarray.__new__(ndarray,shape=(n),dtype=float,order='C')
            #delta.fill(0)
            Q = []
            
            #Phase 1 BFS
            Q.append(s)
            while(len(Q)>0):
                v = Q.pop(0)
                S.append(v)
                
                #for w in Successors[v]:
                #for w in self._G.getVertex(v).getSuccessors():
                    #w=int(w)
                
                for vv in self._G:
                    
                    if(mapsV[vv]==v):
                        print 'VV',vv,v,mapsV[vv]
                        for ww in self._G[vv]:
                            print 'WW',ww
                            w=mapsV[ww]
                            print 'w',w
            
                                #w found for the first time?
                            if (isnan(d[w])) :
                                Q.append(w)
                                d[w] = d[v] + 1
                                #shortest path to w via v?
                            if d[w]==d[v]+1 :
                                assert(d[w]<Inf)
                                sigma[w] += sigma[v]
                                P[w].append(v)
                        
            #Phase 2
            #The algorithm heart
            #S returns vertices in order of non-increasing distance from s
            while(len(S)>0):
                w = S.pop()
                
                #update routing table of w to s 
                if (s==w):
                    self._routingTable[w,s] = [s]
                else:
                    self._routingTable[w,s] = P[w]
                
                #update deltaDot                    
                delta[w]+=CW[s,w]
                for v in P[w] :
                    if w not in self._group :
                        delta[v] += delta[w]*sigma[v]/sigma[w]
                    else :                            
                        delta[v] += 0  #customization point
                        
                #Group calculations    
                if (s not in self._group) and (w in self._group) :
                    #Dana's group betweenness
                    self._GB+=delta[int(w)]
                    
                if (s in self._group) and (w in self._group) and (s!=w):
                    #source and one another vertex are in the group
                    self._GB+=delta[int(w)]
                   
                if (s in self._group) and (w in self._group) and (s==w):
                    #only the source is in group
                    self._GB+=delta[int(w)]
                        
            self._sigma[s]=sigma
            self._distance[s]=d
            self._deltaDot[s]=delta
    def getDistanceMatrix(self):
        return self._distance
    def getDeltaDotMatrix(self):
        return self._deltaDot
    def getSigmaMatrix(self):
        return self._sigma
    def getRoutingTable(self):
        return self._routingTable
    def getGB(self):
        return self._GB
        

    
    
################################################################################
class StaticSet(abstractGroupEvaluation.AbstractGroupEvaluation,abstractGroupEvaluation.BasicSet):
            """
            Object of this class is NOT instance of set!
            However it supports methods add() and remove()
            from python set interface.
            
            In later versions it is expected to have all set's
            functionality and actualy extend Set class
            """                

            def __init__(self,G,members=set([])):
                self._G = G
                self._members = set([])
                self._gb = 0
                self._parties = {}
                for m in members:
                    self.add(m)
                
            def getGB(self,G):
                if self._gb<0:
                    ##update group betweenness value                        
                    gbalg = WeightedUlrik(G,group=self._members)
                    self._gb = gbalg.getGB() 
                    self._updated = True
                return self._gb
            def getUtility(self):
                return self.getGB()
            def getMembers(self):
                return self._members
            def add(self,party):
                self._gb=-1
                if "__iter__" in dir(party):
                    self._members.update(party)
                else:
                    self._members.add(party)
            def remove(self,party):
                self._gb=-1
                if "__iter__" in dir(party):
                    self._members.difference_update(party)
                else:
                    self._members.remove(party)                    
            def getUtilityOf(self,party):
                """
                (list of potential members)->float
                Calculates the exact contribution of party to GBC of current set.
                """
                ##if party is a single element make a list from it
                if "__iter__" not in dir(party):
                    party = [party]
                ##transform party into hashable object 
                party = tuple(sorted(party))
                
                if not self._parties.has_key(party):
                    s = party
                    ##update group betweenness value
                    cbalg = candidatesBasedAlgorithm.CandidatesBasedAlgorithm(self._dw,s)
                    for x in s:
                        cbalg.addMember(x)
                    self._parties[party] = cbalg.getGB()
                return self._parties[party]
            def getCost(self):
                return len(self.getMembers())
            def getCostOf(self,party):
                if not "__iter__" in dir(party):
                    party = [party]
                return len(party)
################################################################################