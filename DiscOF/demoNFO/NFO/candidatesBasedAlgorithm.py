import dataWorkshop
import abstractGroupEvaluation

from numpy import *
import copy as copymodule
import new
import utils

#from decimal import Decimal
#Inf = Decimal("Inf")
#NaN = Decimal("NaN")

#def printMatrix(matrix):
    #maxcol = 0
    #for row in matrix:
        #if (len(row)>maxcol):
            #maxcol=len(row)
    #str = "\t"
    #for j in range(maxcol):
        #str += "%02d\t"%j
    #print str
    #i=0    
    #for row in matrix:
        #str = "%02d [\t"%i
        #for cell in row:
            #str += "%.2f\t"%cell
        #str += " ]"
        #print str
        #i+=1


def calculateGBC(dataWorkshop,group):
    """
    (DataWorkshop,sequence of vertices)-> double
    calculates the Group Betweenness Centrality of group in O(|group|^3)
    """
    candidates = group#list(set(group))
    candidates.sort()
    cn = len(candidates)
    
    applicantsMap = {}
    for i in range(cn):
        applicantsMap[candidates[i]]=i
        print 'Candidates',candidates[i] 
    
    d =     ndarray.__new__(ndarray,shape=(cn,cn),dtype=integer,order='C')
    sigma = ndarray.__new__(ndarray,shape=(cn,cn),dtype=integer,order='C')
    PB =    ndarray.__new__(ndarray,shape=(cn,cn),dtype=float  ,order='C')
    for i in range(cn):
        for j in range(cn):
            d    [i,j]=dataWorkshop._d    [candidates[i],candidates[j]]
            sigma[i,j]=dataWorkshop._sigma[candidates[i],candidates[j]]
            PB   [i,j]=dataWorkshop._PB   [candidates[i],candidates[j]]

    newPB = PB.copy()     
    newSigma = sigma.copy();
    
    GB=0

    for v in candidates:
        v = applicantsMap[v]
        GB += PB[v,v]
        for x in candidates:
            x = applicantsMap[x]
            for y in candidates:
                y = applicantsMap[y]

                #does not work for digraphs. 
                dxvy = 0;dxyv = 0;dvxy = 0
                if not (sigma[x,y]==0 or sigma[x,v]==0 or sigma[y,v]==0):
                    if (d[x,v]==d[x,y]+d[y,v]):
                        dxyv = 1.0 * sigma[x,y]*sigma[y,v]/sigma[x,v]
                    if (d[x,y]==d[x,v]+d[v,y]):
                        dxvy = 1.0 * sigma[x,v]*sigma[v,y]/sigma[x,y]
                    if (d[v,y]==d[v,x]+d[x,y]):
                        dvxy = 1.0 * sigma[v,x]*sigma[x,y]/sigma[v,y]
                
                newSigma[x,y]  = sigma[x,y]*(1 - dxvy)                            
                newPB[x,y] = PB[x,y] - PB[x,y] * dxvy                
                if (y!=v): 
                    newPB[x,y] -= PB[x,v] * dxyv
                if (x!=v): 
                    newPB[x,y] -= PB[v,y] * dvxy
        tmp = PB
        PB = newPB
        newPB=tmp
        tmp = sigma
        sigma = newSigma
        newSigma = tmp
    print 'GBBB',GB
    return GB


class CandidatesBasedAlgorithm():        
        """
        Dinamic DataWorkshop for a single Group of vertices.
        
        Information held by this DS describes all candidates
        that may join the Set. From this info we are able to
        calculate Groups's GBC for every new member of the group.

        No queries are allowed on vertices which are not candidates.
        (Impl. Notes: Consider implicit candidate insertion)

        definitions:
        same definitions as in DataWorkshop
        GB - Group Betweenness centrality of current set.
        c_B(x) - contribution of "candidate x" to current Set GBC
        c_sigma - number of shortest pathes between x and y which has no vertices from S
        c_delta(x,w,y) = c_sigma(x,w) * c_sigma(w,y) / sigma(x,y)
        c_delta(x,w,.) = sum of c_delta(x,w,y) for all y in V
        c_PB{x,y} - sum of c_delta(v,x,y,u) for all v,u in V
        
        You can avoid multiple initialization by deepcopying and reseting
        previously created algorithm.

        In this class applicants and candidates are synonims.
        Different naming is for the sake of future extensions.
        """
        def __init__(self,dataWorkshop,candidates):
            """
            @param dataWorkshop - Initialized DataWorkshop object to work with. Behaviour undefined if
                                  it's content is modified during operation of this algorithm.
            @param candidates - Only members of candidates collection may join the group later on. 
                                Every member must be hashable (better integer)
                                all members must be distinct
            
            declares the following data members:
            _originalData   //the parameter DataWorkshop object
            _cn             //number of candidates
            _applicantsMap  //map of vertices vs. their candidate index {vertex:index}
            _candidates     //list of distinct vertices. Imposes order on all data matrices
            _GB             //Group Betweenness Centrality of currentSet
            _members        //the subject group of vertices of this algorithm
            _currentSet     //wrapping object for members with add/remove methods
            
            members inherited from DataWorkshop (semanticaly changed!)
            _n              //number of candidates
            _B              //c_B(x) 
            _d              //distance matrix
            _sigma          //c_sigma(x,y) number of shortest paths that does not pass through members
            _deltaDot       //c_delta(x,y,.)
            _PB             //c_PB(x,y)
            """
            assert isinstance(dataWorkshop,dataWorkshop.DataWorkshop)
            ##self._originalData = dataWorkshop
            candidates = list(set(candidates))
            candidates.sort()
            cn = len(candidates)
            self._candidates = candidates
            self._cn = cn
            
            self._applicantsMap = {}
            for i in range(self._cn):
                self._applicantsMap[candidates[i]]=i
            
            #is not persistant !!
            self._algorithmListeners = []
            
            self._n = cn

            #self._d = array([[dataWorkshop._d[x,y] for y in candidates] for x in candidates],integer,ndmin=2,order='C')
            #self._sigma = array([[dataWorkshop._sigma[x,y] for y in candidates] for x in candidates],integer,ndmin=2,order='C')
            #self._PB = array([[dataWorkshop._PB[x,y] for y in candidates] for x in candidates],float,ndmin=2,order='C')            
            self._d =     ndarray.__new__(ndarray,shape=(cn,cn),dtype=integer,order='C')
            self._sigma = ndarray.__new__(ndarray,shape=(cn,cn),dtype=integer,order='C')
            self._PB =    ndarray.__new__(ndarray,shape=(cn,cn),dtype=float  ,order='C')
            for i in range(cn):
                for j in range(cn):
                    self._d    [i,j]=dataWorkshop._d    [candidates[i],candidates[j]]
                    self._sigma[i,j]=dataWorkshop._sigma[candidates[i],candidates[j]]
                    self._PB   [i,j]=dataWorkshop._PB   [candidates[i],candidates[j]]

            self._newPB = self._PB.copy()     
            self._newSigma = self._sigma.copy();

            
            
            self._members = set([])
            self._GB=0
            
        def __repr__(self):
            return str(self)
    
        def __str__(self):
            result = "<Candidates Contribution: c="+ str(self._n) + " GBC=" + str(self._GB) + "\n"
            result += "Candidates= " + str(self._candidates) + "\n"
            result += "Members= " + str(self._members) + "\n"
            result += "Distance= \n"
            result += utils.matrixStr(self._d) + "\n"
            result += "Sigma= \n"
            result += utils.matrixStr(self._sigma) + "\n"
            result += "Path betweenness= \n"
            result += utils.matrixStr(self._PB) + "\n"
            result += ">"
            return result


        #def __deepcopy__(self,memo,_nil=[]):
            #"""
            #only phase specific data is copied.
            #can be used to undo member additions.
            #it is not safe to modify applicants,dataWorkshop or graph specific data
            #if maintaining copies of this class. 
            #"""
            #k = id(self)
            #y = memo.get(k, _nil)
            #if y is not _nil:
                #return y
            #y = new.instance(CandidatesBasedAlgorithm)
            #memo[k] = y
            
            #d = {}

            #persistantFields = ["_currentSet",
                                #"_candidates",
                                #"_GB",
                                #"_members",
                                #"_B",
                                #"_d",
                                #"_sigma",
                                #"_deltaDot",
                                #"_PB"]
            #commonFields = ["_originalData"]
            #for x in self.__dict__.items():
                #if (x[0] not in persistantFields):
                    #d[x[0]] = x[1]
                #else:
                    #d[x[0]] = copy.deepcopy(x[1],memo)               
            #y.__dict__.update(d)
            #return y
            
        #def getPairBetweenness(self,s0,s1):
            #assert (self._PB[s0,s1]>=0) 
            #return DataWorkshop.getPairBetweenness(self,s0,s1)
        
        def getCandidates(self):
            """ reference escaping """
            return self._candidates

        def getMembers(self):
            """ reference escaping """
            return self._members

        def getGB(self):
            return self._GB            
        
        def getOriginalDataWorkshop(self):
            """ reference escaping """
            return self._originalData
        
        def getDelta(self,u,w,v):
            """
            (int,int[,int])->double
            Overrides getDelta in DataWorkshop to avoid division by zero when c_sigma(u,v) becomes 0            
            and also does not support delta(u,w,*) values
            """
            if (self._d[u,v]==self._d[u,w]+self._d[w,v]):
                #return 1.0 * self._sigma[u][w]*self._sigma[w][v]/self._originalData._sigma[u][v]
                if (self._sigma[u,w]==0 or self._sigma[w,v]==0 or self._sigma[u,v]==0):
                    return  0.0
                else:
                    return  1.0 * self._sigma[u,w]*self._sigma[w,v]/self._sigma[u,v]
            else:
                return 0.0
            

        def addAlgorithmListener(self,listener):
            """
            (CandidatesBasedAlgorithm,(CandidatesBasedAlgorithm,locals)->None) -> None
            registers a listening function that will be called at key points of
            algorithm execution. 
            Please refer to comments in body of addMember(..) for more information
            Copies of this class share same list of listeners !
            """
            self._algorithmListeners.append(listener)
        def removeAlgorithmListener(self,listener):
            """
            (CandidatesBasedAlgorithm,(CandidatesBasedAlgorithm,locals)->None) -> None
            removes a previosly registered listening function.
            Copies of this class share same list of listeners!
            """
            self._algorithmListeners.remove(listener)
            
        def addMember(self,v):
            #59.5, 35.87, 20.64
                if v not in self._members:
                    self._members.add(v)
                    #translate v to be used in small candidates matrix
                    v = self._applicantsMap[v]
                    self._GB += self.getB(v)
                    
                    d = self.getDistanceMatrix() 
                    # tmp. copy PB,sigma.
                    for x in self._candidates:
                        x = self._applicantsMap[x]
                        for y in self._candidates:
                            y = self._applicantsMap[y]
                            
                            #as implemented here does not work for digraphs. 
                            dxvy = 0;dxyv = 0;dvxy = 0
                            if not (self._sigma[x,y]==0 or self._sigma[x,v]==0 or self._sigma[y,v]==0):
                                if (self._d[x,v]==self._d[x,y]+self._d[y,v]):
                                    dxyv = 1.0 * self._sigma[x,y]*self._sigma[y,v]/self._sigma[x,v]
                                if (self._d[x,y]==self._d[x,v]+self._d[v,y]):
                                    dxvy = 1.0 * self._sigma[x,v]*self._sigma[v,y]/self._sigma[x,y]
                                if (self._d[v,y]==self._d[v,x]+self._d[x,y]):
                                    dvxy = 1.0 * self._sigma[v,x]*self._sigma[x,y]/self._sigma[v,y]
                            
                            self._newSigma[x,y]  = self._sigma[x,y]*(1 - dxvy)                            
                            self._newPB[x,y] = self._PB[x,y]
                            self._newPB[x,y] -= self._PB[x,y] * dxvy
                            if (y!=v): 
                                self._newPB[x,y] -=self._PB[x,v] * dxyv
                            if (x!=v): 
                                self._newPB[x,y] -=self._PB[v,y] * dvxy
                            #######################################
                            ## Notify listeners
                            #for l in self._algorithmListeners: l(self,locals())
                            #######################################
                    ##apply changes
                    tmp = self._PB
                    self._PB = self._newPB
                    self._newPB=tmp
                    tmp = self._sigma
                    self._sigma = self._newSigma
                    self._newSigma = tmp


################################################################################
class OptimizedDinamicSet(abstractGroupEvaluation.AbstractGroupEvaluation,abstractGroupEvaluation.BasicSet):
            """
            Object of this class is NOT instance of set!
            However it supports methods add() and remove()
            from python set interface.
            
            In later versions it is expected to have all set's
            functionality and actualy extend Set class

            """                

            def __init__(self,dw,candidates,members=set([])):
                assert isinstance(dw,dataWorkshop.DataWorkshop)
                self._dw = dw
                self._candidates = candidates
                self._cbalg = CandidatesBasedAlgorithm(self._dw,self._candidates)
                self._parties = {}
                for m in members:
                    self.add(m)
            def getGB(self):
                return self._cbalg.getGB() 
            def getUtility(self):
                return self._cbalg.getGB()
            def getMembers(self):
                return self._cbalg.getMembers()
            def add(self,party):
                self._parties = {}
                if "__iter__" in dir(party):
                    for x in party:
                        self._cbalg.addMember(x)
                else:
                    self._cbalg.addMember(party)
            def remove(self,party):
                self._parties = {}
                members = set(self.getMembers())
                if "__iter__" in dir(party):
                    for x in party:
                        members -= set(party)
                else:
                    if party in self.getMembers():
                        members.remove(party)
                self._cbalg = CandidatesBasedAlgorithm(self._dw,self._candidates)
                for x in members:
                    self._cbalg.addMember(x)
            def getUtilityOf(self,party):
                """
                (list of potential members)->float
                Calculates the exact contribution of party to GBC of current set.
                """
                if not "__iter__" in dir(party):
                    party = [party]
                party = tuple(sorted(set(party)))
                if not self._parties.has_key(party):
                    self._parties[party] = calculateGBC(self._cbalg,party)
                return self._parties[party]
            def getCost(self,):
                return len(self.getMembers())
            def getCostOf(self,party):
                if not "__iter__" in dir(party):
                    party = [party]
                return len(party)
                
################################################################################

################################################################################
class DinamicSet(abstractGroupEvaluation.AbstractGroupEvaluation,abstractGroupEvaluation.BasicSet):
            """
            Object of this class is NOT instance of set!
            However it supports methods add() and remove()
            from python set interface.
            
            In later versions it is expected to have all set's
            functionality and actualy extend Set class
            """                

            def __init__(self,dw,members=set([])):
                assert isinstance(dw,dataWorkshop.DataWorkshop)
                self._dw = dw
                self._members = set([])
                self._gb = 0
                self._parties = {}
                for m in members:
                    self.add(m)
                
            def getGB(self):
                if self._gb<0:
                    ##update group betweenness value
                    self._gb = calculateGBC(self._dw,self._members) 
                return self._gb
            def getUtility(self):
                return self.getGB()
            def getMembers(self):
                return self._members
            def add(self,party):
                self._gb=-1
                self._parties = {}
                if "__iter__" in dir(party):
                    self._members.update(party)
                else:
                    self._members.add(party)
            def remove(self,party):
                self._gb=-1
                self._parties = {}
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
                    s = self._members.union(party)
                    self._parties[party] = calculateGBC(self._dw,s) -  self.getGB()
                return self._parties[party]
            def getCost(self):
                return len(self.getMembers())
            def getCostOf(self,party):
                if not "__iter__" in dir(party):
                    party = [party]
                return len(party)
################################################################################
################################################################################
class StaticSet(abstractGroupEvaluation.AbstractGroupEvaluation,abstractGroupEvaluation.BasicSet):
            """
            Object of this class is NOT instance of set!
            However it supports methods add() and remove()
            from python set interface.
            
            In later versions it is expected to have all set's
            functionality and actualy extend Set class
            """                

            def __init__(self,dw,members=set([])):
                assert isinstance(dw,dataWorkshop.DataWorkshop)
                self._dw = dw
                self._members = set([])
                self._gb = 0
                self._parties = {}
                for m in members:
                    self.add(m)
                
            def getGB(self):
                if self._gb<0:
                    ##update group betweenness value
                    cbalg = CandidatesBasedAlgorithm(self._dw,self._members)
                    for x in self._members:
                        cbalg.addMember(x)
                        
                    self._gb = cbalg.getGB() 
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
                    cbalg = CandidatesBasedAlgorithm(self._dw,s)
                    for x in s:
                        cbalg.addMember(x)
                    self._parties[party] = cbalg.getGB()
                return self._parties[party]
            def getCost(self,party):
                return len(self.getMembers())
            def getCostOf(self,party):
                if not "__iter__" in dir(party):
                    party = [party]
                return len(party)
################################################################################
