from mininet.topo import Topo
import itertools
import os
class SampleTopo( Topo ):
    "Rocketfuelbih topology"

    def __init__( self ):
       
        Topo.__init__( self )
        s='s'
        fourfirstbits=[]

        for x in map(''.join, itertools.product('01', repeat=8)):
                    fourfirstbits.append(x)
                # Switchesh13= self.addHost( 'h13' )
        allrouters=[]  
        allrouters.append(2)
        
        j=1
        while j<32:
            s='s%s' % (j)
            allrouters.append('s%s' % (j))
            vars() [s] = self.addSwitch( 's%s' % (j))
            j=j+1
            
 
        
        ins = open(os.getcwd() + "/netrocketbig", "r" )
        array = []
        for line in ins:
            
            line2=line.split(' ')
            
            temp=[]
            temp2=[]
            fromr = line2[0]
            tor=line2[1]
            temp.append( fromr )
            temp.append( tor )
            temp2.append( tor )
            temp2.append( fromr )
            
            
            if (temp2 not in array):
                array.append(temp)
            
        ins.close()
        
        for l in array:
            #print "l",l
            #print "l[0]",l[0]
            self.addLink( allrouters[int(l[0])], allrouters[int(l[1])] )
        
        
                #numberofHosts=100
        numberofHostsPerRouter = 11
        # Initialize topology
        counter=1
        #switches=[1,2,3,4,5,7,8,9,10,12,13,14,15]
        k=32
        hostscounter=1
        j=0
        while counter<k:
             
            i=1
            fourflastbits=[]
            for x1 in map(''.join, itertools.product('01', repeat=8)):
                fourflastbits.append(x1)
            while i<numberofHostsPerRouter:
                
                
                self.addLink(self.addHost('h%s' % (hostscounter),ip='10.0.'+format(int(format(fourfirstbits[j]),2))+ '.' + format(int(format(fourflastbits[i]),2))), 's'+  str(counter))
                i=i+1
                hostscounter=hostscounter+1
            j=j+1 
            counter=counter+1

topos = { 'Rocketfuelbig': ( lambda: SampleTopo() ) }
