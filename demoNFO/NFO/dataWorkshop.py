import ulrik
import copy
import utils
from numpy import *

    

class DataWorkshop:
    """
    version 1.0
    
    A set of data structures and algorithms required for betweenness calculations.
    given:
    G=(V,E) - undirected unweighted graph n = |V|, m = |E|

    O(1) retrieved data:
    B(x) - individual vertex betweenness
    d{x,y} - distance between vertices x and y
    sigma{x,y} - number of shortest pathes between x and y
    delta(x,w,y) - sigma{x,w}*sigma{w,y}/sigma{x,y}
    delta(x,w,.) - sum of delta(x,w,y) for all y in V
    PB{x,y} - sum of delta(v,x,y,u) for all v,u in V
    
    {} - curly braces indicate unknown/unimportant order of arguments

    other data:
    AverageSigma
    AverageDistance
    PathDispersion
    
    """
    
    
    
    '''
    try:
        import matplotlib.pyplot as plt  # package to draw graphs
    except Exception:
        print "Please install matplotlib and try again"
        sys.exit()
    '''

    def __init__(self, graph, WC=utils.DefaultCommMatrix(),statusBar=False):
        
        """
        (GroupBasedAlgorithm, Graph) -> GroupBasedAlgorithm
        Performs precomputation O(n^3 + nm)
        Why +nm ? may be it works on multigraphs too :)

        (impl: consider just-in-time calculation of PB values)
        """
        
        #self._n = graph.getNumberOfVertices()
        #self._subsets = set(range(0))

        #single Ulrik traversal O(nm)
        nodesn=0

        nodesn=len(graph.nodes())
        print 'number nodes',nodesn
        self._n = nodesn
        GB = ulrik.WeightedUlrik(graph,WC,statusBar)
        print 'GB1',GB
        #the graph itself is never referenced after this line
        self._d = GB.getDistanceMatrix()
        self._deltaDot = GB.getDeltaDotMatrix()
        self._sigma = GB.getSigmaMatrix()
        self._routingTable = GB.getRoutingTable()
        
        #todo delay create PathBetweenness matrix 
        self._PB = ndarray.__new__(ndarray,shape=(self._n,self._n),dtype=float,order='C');
        self._PB.fill(nan)
        progressCount = 0
        for s0 in range(self._n):
            if statusBar:
                progressCount+=1
                statusBar.updateStatus("%d %%"%(100.0*progressCount/self._n))
            for s1 in range(self._n):
                self.getPairBetweenness(s0,s1)
                
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        result = "<DataWorkshop: n="+ str(self._n) +"\n"
        result += "Distance: \n"
        result += utils.matrixStr(self._d) + "\n"
        result += "Routing table: \n"
        result += utils.matrixStr(self._routingTable) + "\n"
        result += "Sigma: \n"
        result += utils.matrixStr(self._sigma) + "\n"
        result += "Path betweenness: \n"
        result += utils.matrixStr(self._PB) + "\n"
        result += ">"
        return result
    
    def getNumberOfVertices(self):
        return self._n

    def getBMatrix(self):
        """ no reference escaping """
        return utils.VirtualList(self._n,lambda i:self.getPairBetweenness(i,i))

    def getDistanceMatrix(self):
        """ reference escaping """
        return self._d

    def getDeltaDotMatrix(self):
        """ reference escaping """
        return self._deltaDot

    def getSigmaMatrix(self):
        """ reference escaping """
        return self._sigma

    def getPBMatrix(self):
        """ reference escaping """
        return self._PB
        #return utils.DelayedMDMatrix(lambda indices:self.getPairBetweenness(indices[0],indices[1]),self._PB,nan,True)
        #return utils.VirtualList(lambda indices:self.getPairBetweenness(indices[0],indices[1]))
        #return UnmutableList(
            #lambda : len(self._PB),
            #lambda s0: UnmutableList(
                #lambda : len(self._PB[s0]),
                #lambda s1 : self.getPairBetweenness(s0,s1)
                #)
            #)
        #return self._PB
    
    def getRoutingTable(self):
        return self._routingTable
    
    def getB(self,v):        
        return self.getPairBetweenness(v,v)

    def getDistance(self,u,v):        
        return self._d[u,v]

    def getSigma(self,u,v):
        return self._sigma[u,v]

    def getPairBetweenness(self,s0,s1):
        if (isnan(self._PB[s0,s1])):
                    #calculate PB
                    #Note that PB(u,v)=PB(v,u)
                    #Every path is counted only once for s0!=s1 because :
                    #delta(v,s0,s1)>0 => delta(v,s1,s0)=0
                    #delta(v,s1,s0)>0 => delta(v,s0,s1)=0
                    self._PB[s0,s1] = 0.0
                    for u in range(self._n):
                        #calculate Delta(u,{s0,s1},*)
                        dd1 = self._deltaDot[u,s1] * self.getDelta(u,s0,s1)
                        #paths from s0 and s1 already counted in deltaDot matrix
                        self._PB[s0,s1]+= dd1
                    #when s0=s1 every path is counted twice (in both directions)
                    #if s0==s1: self._PB[s0][s1] /= 2
                    return self._PB[s0,s1] 
        else:
            return self._PB[s0,s1]

    def getDelta(self,u,w,v=None):
        """
        (GroupBasedAlgorithm, int,int,int) -> float
        @return - percentage of shortest paths from u to v passing throug w
        @time - O(1)
        """
        if v==None :
            return self._deltaDot[u,w]
        elif self._sigma[u,v]==0 or self._sigma[u,w]==0 or self._sigma[w,v]==0:
            return 0.0
        elif (self._d[u,v]==self._d[u,w]+self._d[w,v]):
            return 1.0 * self._sigma[u,w]*self._sigma[w,v]/self._sigma[u,v]
        else:
            return 0.0

    def getAverageSigma(self,sourceGroup = None, targetGroup = None, filterFunction = lambda x,y : x!=y):
        if (sourceGroup==None):
            sourceGroup = range(self._n)
        if (targetGroup==None):
            targetGroup = range(self._n)
        s = 0.0
        c = 0.0
        for i in sourceGroup:
            for j in targetGroup:
                if(filterFunction(i,j)):
                    c+=1
                    s+=self.getSigma(i,j)
        return s/c
    def getAverageDistance(self,sourceGroup = None, targetGroup = None, filterFunction = lambda x,y : x!=y):
        if (sourceGroup==None):
            sourceGroup = range(self._n)
        if (targetGroup==None):
            targetGroup = range(self._n)
        s = 0.0
        c = 0.0
        for i in sourceGroup:
            for j in targetGroup:
                if(filterFunction(i,j)):
                    c+=1
                    s+=self.getDistance(i,j)
        return s/c                    
    def getPathDispersion(self,middleGroup = None,sourceGroup = None,targetGroup=None,filterFunction = lambda x,y : x!=y):
        if (sourceGroup==None):
            sourceGroup = range(self._n)
        if (targetGroup==None):
            targetGroup = range(self._n)
        if (middleGroup==None):
            middleGroup = range(self._n)
        fragmented = 0
        recoverable = 0
        for v in sourceGroup:
            for u in targetGroup:
                s = 0
                for w in middleGroup:
                    if 0<self.getDelta(v,w,u)<1:
                        s+=self.getDelta(v,w,u)
                fragmented += s
                if s==1:
                    recoverable += s
        return (fragmented, recoverable)
    

        