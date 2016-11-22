#!/usr/bin/env python

import math
import sys

if (len(sys.argv) != 2 ) :
    print "Usage: Wires.py wires.input"
    exit(1)

print 'Will read input file', sys.argv[1]
 
#Build the geometry for layers

inputmemorymodules = []
outputmemorymodules = []
processingmodules = []

def matchin(proc,mem):
    if "FT_L1L2" in proc:
        if "L3" in mem[8:10]:
            return "1"
        if "L4" in mem[8:10]:
            return "2"
        if "L5" in mem[8:10]:
            return "3"
        if "L6" in mem[8:10]:
            return "4"
        if "F1" in mem[8:10] or "B1" in mem[8:10]:
            return "5"
        if "F2" in mem[8:10] or "B2" in mem[8:10]:
            return "6"
        if "F3" in mem[8:10] or "B3" in mem[8:10]:
            return "7"
        if "F4" in mem[8:10] or "B4" in mem[8:10]:
            return "8"
        if "F5" in mem[8:10] or "B5" in mem[8:10]:
            return "9"
    if "FT_L3L4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "L5" in mem[8:10]:
            return "3"
        if "L6" in mem[8:10]:
            return "4"
        if "F1" in mem[8:10] or "B1" in mem[8:10]:
            return "5"
        if "F2" in mem[8:10] or "B2" in mem[8:10]:
            return "6"
    if "FT_L5L6" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "L3" in mem[8:10]:
            return "3"
        if "L4" in mem[8:10]:
            return "4"
    if "FT_F1F2" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "F3" in mem[8:10]:
            return "3"
        if "F4" in mem[8:10]:
            return "4"
        if "F5" in mem[8:10]:
            return "7"
    if "FT_B1B2" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "B3" in mem[8:10]:
            return "3"
        if "B4" in mem[8:10]:
            return "4"
        if "B5" in mem[8:10]:
            return "7"
    if "FT_F3F4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "F1" in mem[8:10]:
            return "3"
        if "F2" in mem[8:10]:
            return "4"
        if "F5" in mem[8:10]:
            return "7"
    if "FT_B3B4" in proc:
        if "L1" in mem[8:10]:
            return "1"
        if "L2" in mem[8:10]:
            return "2"
        if "B1" in mem[8:10]:
            return "3"
        if "B2" in mem[8:10]:
            return "4"
        if "B5" in mem[8:10]:
            return "7"
    if "FT_F1L" in proc:
        if "F2" in mem[8:10]:
            return "1"
        if "F3" in mem[8:10]:
            return "2"
        if "F4" in mem[8:10]:
            return "3"
        if "F5" in mem[8:10]:
            return "4"
    if "FT_B1L" in proc:
        if "B2" in mem[8:10]:
            return "1"
        if "B3" in mem[8:10]:
            return "2"
        if "B4" in mem[8:10]:
            return "3"
        if "B5" in mem[8:10]:
            return "4"
            
    print "Unknown in matchin : ",proc,mem,mem[8:10]
    return "0"



fi = open(sys.argv[1],"r")

lines = []

fp = open("processingmodules_inputs.dat","w")

for line in fi:
    if not ">" in line:
        continue
    substr = line.split(">")
    lines.append(line)
    if len(substr) != 3 :
        print substr
    inputmems = substr[0].split() 
    processing = substr[1]
    outputmems = substr[2].split()
    fp.write(processing+" has "+str(len(inputmems))+" inputs\n")
    for mems in inputmems :
        inputmemorymodules.append(mems)
    for mems in outputmems :
        outputmemorymodules.append(mems)
    processingmodules.append(processing)
print "Number of processing modules : ",len(processingmodules)
print "Number of input memories     : ",len(inputmemorymodules)
print "Number of output memories    : ",len(outputmemorymodules)

region = sys.argv[1].split('.')[-1]
fp = open("processingmodules_"+region+".dat","w")

for mem in outputmemorymodules :
    if not mem in inputmemorymodules :
        print mem," is not in inputmemorymodules"
        if "CT_" in mem:
            inputmemorymodules.append(mem)

for proc in processingmodules :
    proc=proc.strip()
    if "LR" in proc:
        fp.write("LayerRouter: "+proc+"\n")
    if "DR" in proc:
        fp.write("LayerRouter: "+proc+"\n")
    if "VMR" in proc:
        fp.write("VMRouter: "+proc+"\n")
    if "TE" in proc:
        fp.write("TrackletEngine: "+proc+"\n")
    if "TC_L" in proc:
        fp.write("TrackletCalculator: "+proc+"\n")
    if "TC_F" in proc:
        fp.write("TrackletCalculator: "+proc+"\n")
    if "TC_B" in proc:
        fp.write("TrackletCalculator: "+proc+"\n")
    if "PR" in proc:
        fp.write("ProjectionRouter: "+proc+"\n")
    if "PT_" in proc:
        fp.write("ProjectionTransceiver: "+proc+"\n")
    if "ME_" in proc:
        fp.write("MatchEngine: "+proc+"\n")
    if "MC_L" in proc:
        fp.write("MatchCalculator: "+proc+"\n")
    if "MC_F" in proc:
        fp.write("DiskMatchCalculator: "+proc+"\n")
    if "MC_B" in proc:
        fp.write("DiskMatchCalculator: "+proc+"\n")
    if "MT_" in proc:
        fp.write("MatchTransceiver: "+proc+"\n")
    if "FT_" in proc:
        fp.write("FitTrack: "+proc+"\n")
    if "PD" in proc:
        fp.write("PurgeDuplicate: "+proc+"\n")

fp = open("memorymodules_"+region+".dat","w")

inputmemcount=[]


IL_mem=0
SL_mem=0
SD_mem=0
AS_mem=0
VMS_short_mem=0
VMS_long_mem=0
SP_mem=0
TPROJ_mem=0
TPAR_mem=0
AP_mem=0
VMPROJ_mem=0
CM_mem=0
FM_mem=0
TF_mem=0
CT_mem=0

for mem in inputmemorymodules :
    count=0
    for m in inputmemcount :
        if mem==m[0] :
            m[1]+=1
            count=m[1]
    if count==0 :
        inputmemcount.append([mem,1])
        count=1
    n=""
    if inputmemorymodules.count(mem)>1 :
        n="n"+str(count)
    if inputmemorymodules.count(mem) == 1 :
        if "AS_" in mem or "VMS_" in mem:
            n="n1"
    found=False
    if "IL" in mem:
        fp.write("InputLink: "+mem+n+" [36]\n")
        IL_mem+=1
        found=True
    if "SL" in mem:
        fp.write("StubsByLayer: "+mem+n+" [36]\n")
        SL_mem+=1
        found=True
    if "SD" in mem:
        fp.write("StubsByLayer: "+mem+n+" [36]\n")
        SD_mem+=1
        found=True
    if "AS_" in mem:
        fp.write("AllStubs: "+mem+n+" [36]\n")
        AS_mem+=1
        found=True
    if "VMS_" in mem:
        fp.write("VMStubs: "+mem+n+" [19]\n")
        if count<3:
            VMS_long_mem+=1
        else:
            VMS_short_mem+=1
        found=True
    if "SP_" in mem:
        fp.write("StubPairs: "+mem+n+" [12]\n")
        SP_mem+=1
        found=True
    if "TPROJ_" in mem:
        fp.write("TrackletProjections: "+mem+n+" [54]\n")
        TPROJ_mem+=1
        found=True
    if "TPAR_" in mem:
        fp.write("TrackletParameters: "+mem+n+" [68]\n")
        TPAR_mem+=1
        found=True
    if "AP_" in mem:
        fp.write("AllProj: "+mem+n+" [56]\n")
        AP_mem+=1
        found=True
    if "VMPROJ_" in mem:
        fp.write("VMProjections: "+mem+n+" [14]\n")
        VMPROJ_mem+=1
        found=True
    if "CM_" in mem:
        fp.write("CandidateMatch: "+mem+n+" [12]\n")
        CM_mem+=1
        found=True
    if "FM_" in mem:
        fp.write("FullMatch: "+mem+n+" [40]\n")
        FM_mem+=1
        found=True
    if "TF_" in mem:
        fp.write("TrackFit: "+mem+n+" [126]\n")
        TF_mem+=1
        found=True
    if "CT_" in mem:
        fp.write("CleanTrack: "+mem+n+" [126]\n")
        CT_mem+=1
        found=True
    if not found :
        print "Did not print memorymodule : ",mem

shortmem=0
longmem=0

def printsum(memname,nmem,memwidth,memdepth,nbx,shortmem,longmem):
    n18bits=0
    if (memwidth<=18):
        n18bits=1;
    if (memwidth==36):
        n18bits=2;
    if (memwidth==54):
        n18bits=3;
    if (memwidth==122):
        n18bits=8;
    if (n18bits==0):
        print "n18bits is zero!!! Fix code"
    print memname,"{:4.0f}".format(nmem),"{:10.0f}".format(memwidth),"{:7.0f}".format(memdepth),"{:5.0f}".format(nbx),"{:14.3f}".format(IL_mem*memwidth*memdepth*nbx*1e-3),"{:10.0f}".format(nmem*n18bits)
    if (n12bits==2 or n12bits==4 or n12bits==6 or n12bits==8):
        longmem+=nmem*n12bits/2
    if (n12bits==1):
        shortmem+=nmem;
    if (n12bits==3):
        longmem+=nmem;
        shortmem+=nmem;
        

print "Memory type     #mems  bits wide   depth   #BX   bits (kbits)  #18k Bram"
#printsum("Input Link     ",IL_mem,36,64,2,shortmem,longmem)
#print "Input Link      ","{:4.0f}".format(IL_mem),"{:10.0f}".format(36),"{:7.0f}".format(64),"{:5.0f}".format(2),"{:14.3f}".format(IL_mem*36*64*2*1e-3),"{:10.0f}".format(IL_mem*2)
longmem+=IL_mem
#print "Stub Layer      ","{:4.0f}".format(SL_mem),"{:10.0f}".format(36),"{:7.0f}".format(64),"{:5.0f}".format(2),"{:14.3f}".format(SL_mem*36*64*2*1e-3),"{:10.0f}".format(SL_mem*2)
longmem+=SL_mem
#print "Stub Disk       ","{:4.0f}".format(SD_mem),"{:10.0f}".format(36),"{:7.0f}".format(64),"{:5.0f}".format(2),"{:14.3f}".format(SD_mem*36*64*2*1e-3),"{:10.0f}".format(SD_mem*2)
longmem+=SD_mem
#print "All Stubs       ","{:4.0f}".format(AS_mem),"{:10.0f}".format(36),"{:7.0f}".format(64),"{:5.0f}".format(8),"{:14.3f}".format(AS_mem*36*64*8*1e-3),"{:10.0f}".format(AS_mem*2)
longmem+=AS_mem
#print "VM Stubs (TE)   ","{:4.0f}".format(VMS_short_mem),"{:10.0f}".format(18),"{:7.0f}".format(32),"{:5.0f}".format(2),"{:14.3f}".format(VMS_short_mem*18*32*2*1e-3),"{:10.0f}".format(VMS_short_mem*1)
shortmem+=VMS_short_mem
#print "VM Stubs (ME)   ","{:4.0f}".format(VMS_long_mem),"{:10.0f}".format(18),"{:7.0f}".format(32),"{:5.0f}".format(8),"{:14.3f}".format(VMS_long_mem*18*32*8*1e-3),"{:10.0f}".format(VMS_long_mem*1)
shortmem+=VMS_long_mem
#print "ME LUT          ","{:4.0f}".format(2*SP_mem),"{:10.0f}".format(1),"{:7.0f}".format(16384),"{:5.0f}".format(1),"{:14.3f}".format(2*SP_mem*16384*1e-3),"{:10.0f}".format(2*SP_mem)
shortmem+=2*SP_mem
#print "Stub Pair       ","{:4.0f}".format(SP_mem),"{:10.0f}".format(18),"{:7.0f}".format(32),"{:5.0f}".format(2),"{:14.3f}".format(SP_mem*18*32*2*1e-3),"{:10.0f}".format(SP_mem*1)
shortmem+=SP_mem
#print "TPROJ           ","{:4.0f}".format(TPROJ_mem),"{:10.0f}".format(54),"{:7.0f}".format(64),"{:5.0f}".format(8),"{:14.3f}".format(TPROJ_mem*54*64*8*1e-3),"{:10.0f}".format(TPROJ_mem*3)
longmem+=TPROJ_mem
shortmem+=TPROJ_mem
#print "TPAR            ","{:4.0f}".format(TPAR_mem),"{:10.0f}".format(54),"{:7.0f}".format(64),"{:5.0f}".format(8),"{:14.3f}".format(TPAR_mem*54*64*8*1e-3),"{:10.0f}".format(TPAR_mem*3)
longmem+=TPAR_mem
shortmem+=TPAR_mem
#print "All Projection  ","{:4.0f}".format(AP_mem),"{:10.0f}".format(54),"{:7.0f}".format(64),"{:5.0f}".format(8),"{:14.3f}".format(AP_mem*54*64*8*1e-3),"{:10.0f}".format(AP_mem*3)
longmem+=AP_mem
shortmem+=AP_mem
#print "VM Projection   ","{:4.0f}".format(VMPROJ_mem),"{:10.0f}".format(13),"{:7.0f}".format(32),"{:5.0f}".format(2),"{:14.3f}".format(VMPROJ_mem*13*32*2*1e-3),"{:10.0f}".format(VMPROJ_mem*1)
shortmem+=VMPROJ_mem
#print "Cand. Mactch    ","{:4.0f}".format(CM_mem),"{:10.0f}".format(12),"{:7.0f}".format(32),"{:5.0f}".format(2),"{:14.3f}".format(CM_mem*12*32*2*1e-3),"{:10.0f}".format(CM_mem*1)
shortmem+=CM_mem
#print "FM Match        ","{:4.0f}".format(FM_mem),"{:10.0f}".format(36),"{:7.0f}".format(64),"{:5.0f}".format(2),"{:14.3f}".format(FM_mem*36*32*2*1e-3),"{:10.0f}".format(FM_mem*2)
longmem+=FM_mem
#print "Track Fit       ","{:4.0f}".format(TF_mem),"{:10.0f}".format(122),"{:7.0f}".format(64),"{:5.0f}".format(2),"{:14.3f}".format(TF_mem*122*64*2*1e-3),"{:10.0f}".format(TF_mem*8)
longmem+=4*TF_mem
#print "Track Fit       ","{:4.0f}".format(TF_mem),"{:10.0f}".format(122),"{:7.0f}".format(64),"{:5.0f}".format(2),"{:14.3f}".format(TF_mem*122*64*2*1e-3),"{:10.0f}".format(TF_mem*4)

print "Number of 18 bit memories : ",shortmem        
print "Number of 36 bit memories : ",longmem        
print "Megabits required :",shortmem*0.018+longmem*0.036

fp = open("wires_"+region+".dat","w")

tcin=[]
prin=[]
cmin=[]
fmin=[]
fmin2=[]
ftin=[]
tfin=[]
mtout=[]
ctout=[]

for m in inputmemcount :
    mem=m[0]
    mem.strip()
    count=m[1]
    for i in range(1,count+1) :
        n=""
        if count>1 :
            n="n"+str(i)
        if count==1 :
            if "AS_" in mem or "VMS_" in mem :
                n="n1"
        fp.write(mem+n+" input=> ")
        # now we need to search for an proc module that fills this memory
        for line in lines:
            substr = line.split(">")
            if mem in substr[2].split() :
                proc=substr[1].strip()
                fp.write(proc)
                if "SL" in mem:
                    if "_L1" in mem:
                        fp.write(".stubout1")
                    if "_L2" in mem:
                        fp.write(".stubout2")
                    if "_L3" in mem:
                        fp.write(".stubout3")
                    if "_L4" in mem:
                        fp.write(".stubout4")
                    if "_L5" in mem:
                        fp.write(".stubout5")
                    if "_L6" in mem:
                        fp.write(".stubout6")
                if "SD" in mem:
                    if "_F1" in mem or "_B1" in mem:
                        fp.write(".stubout1")
                    if "_F2" in mem or "_B2" in mem:
                        fp.write(".stubout2")
                    if "_F3" in mem or "_B3" in mem:
                        fp.write(".stubout3")
                    if "_F4" in mem or "_B4" in mem:
                        fp.write(".stubout4")
                    if "_F5" in mem or "_B5" in mem:
                        fp.write(".stubout5")
                if "VMS_" in mem:
                    fp.write(".vmstubout"+mem[8:14]+n+" ")
                if "AS_" in mem:
                    fp.write(".allstubout"+n+" ")
                if "SP_" in mem:
                    fp.write(".stubpairout")
                if "TPROJ_" in mem:
                    if ("PT_" in proc) :
                        fp.write(".projout")
                    else : 
                        if ("TPROJ_ToM" in mem) :
                            fp.write(".projoutToMinus_"+mem[23:]) 
                        else : 
                            if ("TPROJ_ToP" in mem) : 
                                fp.write(".projoutToPlus_"+mem[22:]) 
                            else :
                                fp.write(".projout"+mem[14:])
                if "VMPROJ_" in mem:
                    fp.write(".vmprojout"+mem[16:22]+n+" ")
                if "AP_" in mem:
                    fp.write(".allprojout"+n+" ")
                if "CM_" in mem:
                    fp.write(".matchout ")
                if "FM_" in mem:
                    if "_ToMinus" in mem:
                        fp.write(".matchoutminus")
                    else:
                        if "_ToPlus" in mem:
                            fp.write(".matchoutplus")
                        else:
                            ii=0
                            for f in mtout :
                                if f[0]==proc :
                                    f[1]+=1
                                    ii=f[1]
                            if ii==0:
                                mtout.append([proc,1])
                                ii=1
                            fp.write(".matchout"+str(ii)+" ")
                if "TF_" in mem:
                    fp.write(".trackout")
                if "CT_" in mem:
                    ii=0
                    for f in ctout :
                        if f[0]==proc :
                            f[1]+=1
                            ii=f[1]
                    if ii==0:
                        ctout.append([proc,1])
                        ii=1
                    fp.write(".trackout"+str(ii)+" ")
                if "TPAR_" in mem:
                    fp.write(".trackpar")
        fp.write(" output=> ")
        # now we need to search for an proc module that fills this memory
        c=0
        for line in lines:
            substr = line.split(">")
            proc=substr[1].strip()
            if mem in substr[0].split() :
                c+=1
                if (count>1) :
                    if c!=i :
                        continue
                fp.write(proc)
                if "IL" in mem:
                    fp.write(".stubin")
                if "SL" in mem:
                    if "SL1_" in mem :
                        fp.write(".stubinLink1")
                    if "SL2_" in mem :
                        fp.write(".stubinLink2")
                    if "SL3_" in mem :
                        fp.write(".stubinLink3")
                if "SD" in mem:
                    if "SD1_" in mem :
                        fp.write(".stubinLink1")
                    if "SD2_" in mem :
                        fp.write(".stubinLink2")
                    if "SD3_" in mem :
                        fp.write(".stubinLink3")
                if "VMS_" in mem:
                    if ("ME_" in proc) :
                        fp.write(".vmstubin")
                    else :
                        if ( ("_L1" in mem and not "TE_F1" in proc and not "TE_B1" in proc) or "_L3" in mem or "_L5" in mem or "_F1" in mem or "_F3" in mem or "_B1" in mem or "_B3" in mem ) :  
                            fp.write(".innervmstubin")
                        else :
                            fp.write(".outervmstubin")
                if "AS_" in mem:
                    if ("MC_" in proc) :
                        fp.write(".allstubin")
                    else :
			if ( "TC_F1D5L1D4" in proc or "TC_B1D7L1D1" in proc):
			    if ( "AS_L1" in mem ):
				fp.write(".innerallstubin")
			    if ( "AS_F1" in mem or "AS_B1" in mem ):
			    	fp.write(".outerallstubin") 
                        elif ( "_L1" in mem or "_L3" in mem or "_L5" in mem or "_F1" in mem or "_F3" in mem ) :  
                            fp.write(".innerallstubin")
                        else :
                            fp.write(".outerallstubin")
                if "SP_" in mem:
                    ii=0
                    for f in tcin :
                        if f[0]==proc :
                            f[1]+=1
                            ii=f[1]
                    if ii==0:
                        tcin.append([proc,1])
                        ii=1
                    fp.write(".stubpair"+str(ii)+"in")
                if "TPROJ_" in mem:
                    if "PT_" in proc :
                        fp.write(".projin")
                    else:
                        ii=0
                        for f in prin :
                            if f[0]==proc :
                                f[1]+=1
                                ii=f[1]
                        if ii==0:
                            prin.append([proc,1])
                            ii=1
                        fp.write(".proj"+str(ii)+"in")
                if "VMPROJ_" in mem:
                    fp.write(".vmprojin")
                if "AP_" in mem:
                    fp.write(".allprojin")
                if "CM_" in mem:
                    ii=0
                    for f in cmin :
                        if f[0]==proc :
                            f[1]+=1
                            ii=f[1]
                    if ii==0:
                        cmin.append([proc,1])
                        ii=1
                    fp.write(".match"+str(ii)+"in")
                if "TF_" in mem:
                    ii=0
                    for f in tfin :
                        if f[0]==proc :
                            f[1]+=1
                            ii=f[1]
                    if ii==0:
                        tfin.append([proc,1])
                        ii=1
                    fp.write(".trackin"+str(ii))
                if "FM_" in mem:
                    if "MT_" in proc :
                        ii=0
                        for f in fmin2 :
                            if f[0]==proc :
                                f[1]+=1
                                ii=f[1]
                        if ii==0:
                            fmin2.append([proc,1])
                            ii=1
                        fp.write(".matchin"+str(ii))
                    else:
                        num=matchin(proc,mem)
                        ii=0
                        for f in fmin2 :
                            if f[0]==proc+num :
                                f[1]+=1
                                ii=f[1]
                        if ii==0:
                            fmin2.append([proc+num,1])
                            ii=1
                        fp.write(".fullmatch"+num+"in"+str(ii))
                if "TPAR_" in mem:
                    ii=0
                    for f in ftin :
                        if f[0]==proc :
                            f[1]+=1
                            ii=f[1]
                    if ii==0:
                        ftin.append([proc,1])
                        ii=1
                    fp.write(".tpar"+str(ii)+"in")
                    

        fp.write("\n")
