from mininet.topo import Topo
import itertools
class SampleTopo( Topo ):
    "Rocketfuel topology with 15 routers topology #1755"

    def __init__( self ):
       
        Topo.__init__( self )

        s1= self.addSwitch( 's1' )
        s2= self.addSwitch( 's2' )
        s3= self.addSwitch( 's3' )
        s4= self.addSwitch( 's4' )
        s5= self.addSwitch( 's5' )
        s6= self.addSwitch( 's6' )
        s7= self.addSwitch( 's7' )
        s8= self.addSwitch( 's8' )
        s9= self.addSwitch( 's9' )
        s10= self.addSwitch( 's10' )
        s11= self.addSwitch( 's11' )
        s12= self.addSwitch( 's12' )
        s13= self.addSwitch( 's13' )
        s14= self.addSwitch( 's14' )
        s15= self.addSwitch( 's15' )
        
        
         # Add links
        self.addLink( s1, s11 )
        self.addLink( s2, s15 )
        self.addLink( s3, s15 )
        self.addLink( s4, s11 )
        self.addLink( s5, s15 )
        self.addLink( s6, s13 )
        self.addLink( s7, s15 )
        self.addLink( s8, s14 )
        self.addLink( s9, s11 )
        self.addLink( s10, s11 )
        self.addLink( s11, s13 )
        self.addLink( s11, s14 )
        self.addLink( s12, s13 )
        self.addLink( s12, s14 )
        self.addLink( s13, s14 )
        self.addLink( s14, s15 ) 
        
        #numberofHosts=100
        numberofHostsPerRouter = 10
        # Initialize topology
        counter=1
        fourfirstbits=[]
        switches=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        for x in map(''.join, itertools.product('01', repeat=4)):
                    fourfirstbits.append(x)
        j=0 #for each prefix
        for l in switches:
            i=1
            fourflastbits=[]
            for x1 in map(''.join, itertools.product('01', repeat=4)):
                fourflastbits.append(x1)
             
            while i<11:
                
                
                
                self.addLink(self.addHost('h%s' % (counter),ip='10.0.0.'+format(int(format(fourfirstbits[j])+ format(fourflastbits[i]),2))), 's'+  str(l))
                counter=counter+1
                i=i+1
            j=j+1


topos = { 'Rocketfuel': ( lambda: SampleTopo() ) }