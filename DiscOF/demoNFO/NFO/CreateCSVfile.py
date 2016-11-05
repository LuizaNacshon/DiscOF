'''
Created on May 8, 2014

@author: Luiza Nacshon
'''

import os
import csv
import glob
import os.path

def getUserAlgo(Algo):
    
    if((os.path.isfile(os.getcwd() + '/' +   "FinalResults/TotalControlPackets.csv"))==False):
        
        with open(os.path.join(os.getcwd() + '/' +   "FinalResults/", 'TotalControlPackets.csv'), 'a') as csvfile:
                        
     
     

     
    
            writer = csv.DictWriter(csvfile, fieldnames = ["AlgoRunTime","runID","serial","TimeStamp","alg","aggregationmethod",\
            "fp-flow-mod","fa-flow-mod","c-flow-mod-routing","c-flow-mod" ,"c-packet-in","c-packet-in-routing","c-packet-out",\
            "c-packet-out-routing","fp-packet-in","fa-flow-removed","full-flowTable-errors","R(Fp)","c-memory-usage",\
            "routers-for-Fp-count","NERsID","NERscount","NERsGBC","gini","total-free-entries","total-used-entries","d_max","d_min",\
            "hosts","routers","links","NetworkIdentifier","initial-flow-entries","pingschangeperiod",\
            "giniThreshold","potentialginiValue","alpha","lamda","beta",\
            "number_of_removed_Fp","number_of_new_installed_Fp","delete_installed_Fp_runtime",\
                         "add_installed_Fp_runtime"], delimiter = ',',quoting=csv.QUOTE_MINIMAL)
            
            
    
            writer.writeheader()
    if((os.path.isfile(os.getcwd() + '/' +   "FinalResults/flowentries.csv"))==False):       
        with open(os.path.join(os.getcwd() + '/' +   "FinalResults/", 'flowentries.csv'), 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = ["RunID","serial","TimeStamp","alg","aggregationmethod","routersID", "free-entries","Gini"], delimiter = ';')
            writer.writeheader()
        
    if(int(Algo)==1):#NER
        create_NERCsv()
    elif(int(Algo)==2):#Greedy
        CreateGreedyCSV()

def CreateGreedyCSV():

    
    files = glob.glob(os.getcwd() + '/' +   "Greedy_NER/*")
    #print "files",files
    try:
        for f in files:
            os.remove(f)
    except:
        print ""
        
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketdrop.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","drop"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cflowmod.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cflowmod"], delimiter = ';')
        writer.writeheader()
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cflowmodrouting.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cflowmod"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketin.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketin"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketinrouting.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketin"], delimiter = ';')
        writer.writeheader()
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketout.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketout"], delimiter = ';')
        writer.writeheader()
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketoutrouting.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketout"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'flowentries.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","routersID", "free-entries"], delimiter = ';')
        writer.writeheader()
          
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'InstallStaticfp.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","InstallStaticfp"], delimiter = ';')
        writer.writeheader()
          
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'Controlmessagespacketin.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","packet-in"], delimiter = ';')
        writer.writeheader()

          
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'Controlmessagesflowmod.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","flow-mod"], delimiter = ';')
        writer.writeheader()
          
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'Controlmessagesflowremoved.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","flow-removed"], delimiter = ';')
        writer.writeheader()
    
#**************************************************Chekcing for NER*************************************************************** 
def create_NERCsv():
        
    files = glob.glob(os.getcwd() + '/' +   "Greedy_NER/*")
    try:
        for f in files:
            os.remove(f)
    except:
        print ""
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'NERTotalControlPackets.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["fp-Flow-Mod","fa-Flow-Mod", "Packet-In","Flow-Removed","NumberOfNERs"], delimiter = ';')
        writer.writeheader()
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketdrop.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","drop"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cflowmod.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cflowmod"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketin.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketin"], delimiter = ';')
        writer.writeheader()
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketout.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketout"], delimiter = ';')
        writer.writeheader()
    
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cflowmodrouting.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cflowmod"], delimiter = ';')
        writer.writeheader()
        

        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketinrouting.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketin"], delimiter = ';')
        writer.writeheader()

    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'cpacketoutrouting.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","cpacketout"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'flowentries.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","routersID", "free-entries"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'InstallStaticfp.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","InstallStaticfp"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'Controlmessagespacketin.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","packet-in"], delimiter = ';')
        writer.writeheader()
    

    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'Controlmessagesflowmod.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","flow-mod"], delimiter = ';')
        writer.writeheader()
        
    with open(os.path.join(os.getcwd() + '/' +   "Greedy_NER/", 'Controlmessagesflowremoved.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = ["TimeStamp","flow-removed"], delimiter = ';')
        writer.writeheader()
