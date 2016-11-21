import os,sys
import PTdict

def topOfList(l,string):
    l1 = [x for x in l if string not in x]
    l2 = [x for x in l if string in x]
    for x in l2:
        l1.insert(0,x)
    return l1
def endOfList(l,string):
    l1 = [x for x in l if string not in x]
    l2 = [x for x in l if string in x]
    print '1',l1
    print '2',l2
    for x in l1:
        l2.append(x)
    return l2

# Define the module class with all the properties
class Module:
    def __init__(self):
        self.module = None
        self.name = None # Names defined in the DN
        self.inputs = None # In and out from master wires file
        self.outputs = None
        self.in_names = None # In and out names should be consistent with Verilog modules
        self.out_names = None
        self.common = None
        self.parameters = '' # Each module has unique parameters
        self.size = 0 # Memory sizes for connecting wires
        self.start = '' 
        self.done = ''

# Read the processing modules
if len(sys.argv) > 1:
    region = sys.argv[1]
else:
    print 'Region to process needed. Try "D3" and run again'
    sys.exit()
# Run the other scripts from here
os.system('python SubProject.py '+region)
os.system('python Wires.py wires.'+region)

f = open('processingmodules_'+region+'.dat')
modules = []
for line in f:
    signals = [] # Pair with nice name and specific instance name
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].strip())
    modules.append(signals) # Add to the list of pairs

# Read the memory modules
g = open('memorymodules_'+region+'.dat')
memories = []
for line in g:
    signals = [] # Nice name, instance name, memory size
    signals.append(line.split(':')[0])
    signals.append(line.split(':')[1].split(' ')[1].strip())
    if len(line.split(':')[1].split(' '))>2:
        signals.append(int(line.split(':')[1].split(' ')[-1].replace('[','').replace(']','').strip()))
    memories.append(signals) # Add to the list of triplets

# Common signals for every module # IPBus might go away
Common = '.clk(clk),\n.reset(reset),\n.en_proc(en_proc)'

# Read initial lines of Tracklet_processing
# Define inputs, outputs and start/done signals
p = open('prologue.txt')
#if "D5" in region:
#  p = open('prologue_disk.txt')
#else:
#  p = open('prologue.txt')
prologue = []
for line in p:
    prologue.append(line)
# Read final lines for IPbus and possible reader
if "D5" in region:
  ep  = open('epilogue_disk.txt')
else:
  ep  = open('epilogue.txt')
epilogue = []
for line in ep:
    epilogue.append(line)

string_prologue = ''
string_starts = ''
string_memories = ''
string_processing = ''
string_epilogue = ''
####################################################
####################################################

il = 0

# Always write the initial lines
for p in prologue:
    string_prologue += '\n' +  p.strip()
    
# Start looping over the memories first
for x in memories:
    h = open('wires_'+region+'.dat') # Open the wire connections file
    m = Module() # Create a module
    i = [] # List of inputs
    i_n = [] # List of input names
    o = [] # List of outputs
    o_n = [] # List of output names
    m.module = x[0] # Module nice name from memory list
    m.name = x[1]  # Module instance name from memory list
    if len(x)>2: # If triplet, get the memory size
        m.size = x[2]
    for line in h: # Loop over connections
        if line.split(' ')[0] == x[1]:  # If instance corresponds to current memory
            if len(line.split(' ')[2].split('.')) > 1: # Memory has inputs
                i.append(line.split(' ')[2].split('.')[0]+'_'+x[1]) # Add input to module's list
                i.append(line.split(' ')[2].split('.')[0]+'_'+x[1]+'_wr_en') # Memory inputs usually have a write enable
                i_n.append('data_in') # Names defined in Verilog memory module
                i_n.append('enable')
            if len(line.split(' ')[-1].split('.')) > 1: # Memory has outputs
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0]+'_number') # Number of items in memory that goes to processing module
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0]+'_read_add')
                o.append(x[1]+'_'+line.split(' ')[-1].split('.')[0])
                o_n.append('number_out') # Names defined in Verilog memory module
                o_n.append('read_add')
                o_n.append('data_out')
    # Define the properties of the module
    m.inputs = i
    m.outputs = o
    m.in_names = i_n
    m.out_names = o_n
    m.common = Common
    ####################################################
    # Specific properties of the memories
    # Any new memories added here
    ####################################################
    if m.module == 'InputLink':
        il +=  1
        m.outputs = [m.outputs[-1]] # This memory has been gutted and is now a passthrough
        m.in_names.append('data_in1') # Two inputs from the links stiched together
        m.in_names.append('data_in2')
        m.inputs.append('input_link%d_reg1'%il)
        m.inputs.append('input_link%d_reg2'%il)
        m.inputs.append(m.outputs[-1]+'_read_en')
        m.out_names = [m.out_names[-1]]
        m.in_names.append('read_en')
        m.out_names.append('empty')
        m.outputs.append(m.outputs[-1]+'_empty')
        m.common = m.common.replace('//.reset(','.reset(')
    if m.module == 'StubsByLayer':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done1_5 = True
    if m.module == 'StubsByDisk':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done1_5 = True
    if m.module == 'AllStubs':
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:] # They are accessed directly by TC and MC
        m.start = m.inputs[0].replace(m.name,'')+'start'
        if 'MC' in m.outputs[0]:
            m.out_names = ['read_add_MC','data_out_MC'] # If the memory is read by an MC change the output names # TODO not needed anymore
    if m.module == 'VMStubs':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done2_5 = True
        if 'ME' in m.outputs[0]:
            m.parameters = '#("Match")'
        else:
            m.parameters = '#("Tracklet")'
    if m.module == 'StubPairs':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done3_5 = True
    if m.module == 'TrackletParameters':
        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:]
        m.start = m.inputs[0].replace(m.name,'')+'start'
    if m.module == 'TrackletProjections':
        #print m.name
        m.start = m.inputs[0].replace(m.name,'')+'proj_start'
        if 'From' in m.name:
            m.start = m.start.replace('proj_','')
            m.parameters = "#(1'b1)"
        if 'To' in m.name:
            m.parameters = "#(1'b1)"
        m.done = m.name+'_start'
    if m.module == 'AllProj':
        if 'L4D' in m.name or 'L5D' in m.name or 'L6D' in m.name:
            m.parameters = "#(1'b0,1'b0)"   #inner,disk
	if 'F1D' in m.name or 'F2D' in m.name or 'F3D' in m.name or 'F4D' in m.name or 'F5D' in m.name: 
            m.parameters = "#(1'b0,1'b1)"   #inner,disk
	if 'B1D' in m.name or 'B2D' in m.name or 'B3D' in m.name or 'B4D' in m.name or 'B5D' in m.name: 
            m.parameters = "#(1'b0,1'b1)"   #inner,disk

        m.out_names = m.out_names[1:] # These memories don't have to send number out
        m.outputs = m.outputs[1:]
        m.start = m.inputs[0].replace(m.name,'')+'start'
    if m.module == 'VMProjections':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done6_5 = True
    if m.module == 'CandidateMatch':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done7_5 = True
    if m.module == 'FullMatch':
        m.out_names.append('read_en')
        if 'From' in m.name:
            m.parameters = "#(64)"
            m.outputs.append(m.outputs[-1]+'_read_en')
        elif 'To' in m.name:
            m.parameters = "#(64)"
            m.outputs.append(m.outputs[-1]+'_read_en')
        else:
            m.outputs.append(m.outputs[-1]+'_read_en')
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
    if m.module == 'TrackFit':
        #m.out_names = m.out_names[1:] # These memories don't have to send number out
        #m.outputs = m.outputs[1:]
        m.out_names.append('index_out')
        m.outputs.append(m.outputs[-1]+'_index')
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done10_5 = True
    if m.module == 'CleanTrack':
        m.outputs.append(m.name+'_DataStream') # Final track out
        m.out_names.append('data_out')
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        ####################################################
    if('mem' not in sys.argv): # If you don't want memories in the print out
        string_memories += '\n'
        for i in m.inputs: # Declare the wires to be used in the memory
            if 'input_link' not in i: # Input link memory does not have an enable
                if '_en' in i:
                    string_memories += '\n' +  'wire '+i+';'
                else:
                    string_memories += '\n' +  'wire ['+str(m.size-1)+':0] '+i+';' # Size of the wire
        for o in m.outputs: # Declare the wires to be used in the memory
            if 'empty' in o or 'CT_' in o: # Not needed wires
                string_memories += '\n' +  '//wire '+o+';'
            elif 'number' in o:
                string_memories += '\n' +  'wire [5:0] '+o+';' # Number of objects in memory
            elif '_index' in o:
                string_memories += '\n' +  'wire [53:0] '+o+' [`tmux-1:0];' # Matrix of stub indices for PD
            elif 'read' in o:
                if m.module == 'VMStubs' or m.module == 'AllStubs' or m.module == 'TrackletParameters' : # These memories have to cross the link
                    string_memories += '\n' +  'wire [10:0] '+o+';' # Deeper for latency
                elif m.module == 'TrackletProjections' or m.module == 'FullMatch': # Not as deep
                    if '_en' in o:
                        string_memories += '\n' +  'wire '+o+';'
                    else:
                        string_memories += '\n' +  'wire [9:0] '+o+';'                
                else:
                    string_memories += '\n' +  'wire [8:0] '+o+';' # Standard depth 6 bits of number plus 3 of BX
                #print 'wire [5:0] '+o+';'
            elif "1'b1" in o:
                continue
            else:
                string_memories += '\n' +  'wire ['+str(m.size-1)+':0] '+o+';' # Wire size
        string_memories += '\n' +  m.module + ' ' + m.parameters +  ' ' + m.name + '(' # Parameters here
        for n,i in zip(m.in_names,m.inputs): # Loop over signals and names
            string_memories += '\n' +  '.'+n+'('+i+'),'
        for n,o in zip(m.out_names,m.outputs):
            string_memories += '\n' +  '.'+n+'('+o+'),'
        string_memories += '\n' +  '.start('+m.start+'),'
        string_memories += '\n' +  '.done('+m.done+'),'
        string_memories += '\n' +  m.common
        string_memories += '\n' +  ');'

####################################################
####################################################
# Done is only needed for 1 module
# If seen once, don't add it anymore
seen_done1_0 = False
seen_done2_0 = False
seen_done3_0 = False
seen_done4_0 = False
seen_done_proj = False
seen_done5_0 = False
seen_done6_0 = False
seen_done7_0 = False
seen_done8_0 = False
seen_done9_0 = False
seen_done10_0 = False

# Start looping over the processing modules
for x in modules:
    h = open('wires_'+region+'.dat') # Open the wire connections file
    m = Module() # Create a module
    i = [] # List of inputs
    i_n = [] # List of input names
    o = [] # List of outputs
    o_n = [] # List of output names
    m.module = x[0] # Module nice name from processing list
    m.name = x[1]  # Module instance name from processing list
    for line in h: # Loop over connections
        if line.split(' ')[-1].strip().split('.')[0] == x[1]: # If instance corresponds to current processing
            i.append(line.split(' ')[0]+'_'+x[1]) # Add input to module's list
            i_n.append(line.split(' ')[-1].strip().split('.')[1])
        if line.split(' ')[2].strip().split('.')[0] == x[1]:
            o.append(x[1]+'_'+line.split(' ')[0]) # Add output to module's list
            o_n.append(line.split(' ')[2].strip().split('.')[1])
    # Define the properties of the module
    m.inputs = i
    m.outputs = o
    m.in_names = i_n
    m.out_names = o_n
    m.common = Common
    ####################################################
    # Specific properties of the processing modules
    # Any new processing added here
    ####################################################
    if m.module == 'LayerRouter':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done1_0 = True
        out_names = []
        outputs = []
        for cnt,out in enumerate(m.outputs):
            out_names.append(str('wr_en%d' %(cnt+1))) # Write enable for every layer
            outputs.append(out+'_wr_en')
        #print out_names
        m.out_names = m.out_names + out_names
        m.outputs = m.outputs + outputs
    if m.module == 'VMRouter':
        enables = []
        enables_2 = []
        for o in m.out_names: 
            if 'vmstubout' in o:
                enables.append(o+'_wr_en') # For every output name create a write enable name
        for o in m.outputs:
            if 'VMR' in o and 'VMS' in o: # Output going to VMStub memory
                enables_2.append(o+'_wr_en') # For every output create a write enable
        m.out_names = m.out_names + enables
        m.outputs = m.outputs + enables_2
        if 'L1' in m.name or 'L3' in m.name or 'L5' in m.name: # Odd layer parameters
            if 'L1' in m.name or 'L3' in m.name: # Inner layer parameter
                m.parameters = "#(1'b1,1'b1)"
            else:
                m.parameters = "#(1'b0,1'b1)"
        else:
            if 'L2' in m.name:
                m.parameters = "#(1'b1,1'b0)"
            else:
                m.parameters = "#(1'b0,1'b0)"
        if 'F1' in m.name or 'F3' in m.name or 'F5' in m.name:
            if 'D5' in m.name:
                m.parameters = "#(1'b1,1'b1,1'b0)"  # PS module, Odd, barrel
            if 'D6' in m.name:
                m.parameters = "#(1'b0,1'b1,1'b0)"  # 2S module, Odd, barrel
        if 'F2' in m.name or 'F4' in m.name:
            if 'D5' in m.name:
                m.parameters = "#(1'b1,1'b0,1'b0)"  # PS module, Odd, barrel
            if 'D6' in m.name:
                m.parameters = "#(1'b0,1'b0,1'b0)"  # 2S module, Odd, barrel

        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done2_0 = True
        vs = 0
        valids = []
        valids2 = []
        for o in m.outputs:
            if 'VMR_L' in o and '_AS_L' in o: # Output going to AllStub memory
                vs = vs + 1
                valids.append(o+'_wr_en')
                valids2.append('valid_data%d'%vs)
            elif 'VMRD_F' in o and '_AS_F' in o: # Output going to AllStub memory
                vs = vs + 1
                valids.append(o+'_wr_en')
                valids2.append('valid_data%d'%vs)
            elif 'VMRD_B' in o and '_AS_B' in o: # Output going to AllStub memory
                vs = vs + 1
                valids.append(o+'_wr_en')
                valids2.append('valid_data%d'%vs)
        m.outputs = m.outputs + valids
        m.out_names = m.out_names + valids2
    if m.module == 'TrackletEngine':
        m.out_names.append('valid_data')
        m.outputs.append(m.outputs[0]+'_wr_en')
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done3_0 = True
        if 'TE_F' in m.name or 'TE_B' in m.name:
            m.parameters = '#("TETable_%s_phi.txt","TETable_%s_z.txt",'"1'b0"')'%(m.name,m.name) # TE Tables names have to be in this format. CHECK EMULATION
        else:
            m.parameters = '#("TETable_%s_phi.txt","TETable_%s_z.txt")'%(m.name,m.name) # TE Tables names have to be in this format. CHECK EMULATION

    if m.module == 'TrackletCalculator':
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'stubin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AS_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back
        ons = []
        for o in m.out_names:
            ons.append('valid_'+o)
        m.out_names = m.out_names + ons
        m.out_names = m.out_names + ['done_proj'] # Done signal for projections
        seen_done_proj = True
        outs = []
        for o in m.outputs:
            outs.append(o+'_wr_en')
        m.outputs = m.outputs+outs
        m.outputs = m.outputs+[m.name+'_proj_start'] # Hardcoded signal name
        
        TC_index = ''
        if 'L1' in m.name:
            if 'D3L2D3' in m.name:
                TC_index = "4'b0000"
            if 'D3L2D4' in m.name:
                TC_index = "4'b0001"
            if 'D4L2D4' in m.name:
                TC_index = "4'b0010"
            m.parameters = "#(.BARREL(1'b1),"+'.InvR_FILE("InvRTable_TC_L1D3L2D3.dat"),'+".R1MEAN(`TC_L1L2_krA),.R2MEAN(`TC_L1L2_krB),.TC_index("+TC_index+"),.IsInner1(1'b1),.IsInner2(1'b1))"
        if 'L3' in m.name:
            if 'D3L4D3' in m.name:
                TC_index = "4'b0011"
            if 'D3L4D4' in m.name:
                TC_index = "4'b0100"
            if 'D4L4D4' in m.name:
                TC_index = "4'b0101"
            m.parameters = "#(.BARREL(1'b1),"+'.InvR_FILE("InvRTable_TC_L3D3L4D3.dat"),'+".R1MEAN(`TC_L3L4_krA),.R2MEAN(`TC_L3L4_krB),.TC_index("+TC_index+"),.IsInner1(1'b1),.IsInner2(1'b0))"
        if 'L5' in m.name:
            if 'D3L6D3' in m.name:
                TC_index = "4'b0011"
            if 'D3L6D4' in m.name:
                TC_index = "4'b0100"
            if 'D4L6D4' in m.name:
                TC_index = "4'b0101"            
            m.parameters = "#(.BARREL(1'b1),"+'.InvR_FILE("InvRTable_TC_L5D3L6D3.dat"),'+".R1MEAN(`TC_L5L6_krA),.R2MEAN(`TC_L5L6_krB),.TC_index("+TC_index+"),.IsInner1(1'b0),.IsInner2(1'b0))"
        if 'F1' in m.name:
            if 'D5F2D5' in m.name:
                TC_index = "4'b0111" 
                m.parameters = '#(.BARREL(0),.InvR_FILE("InvRTable_TC_F1D5F2D5.dat"),.InvT_FILE("InvTTable_TC_F1D5F2D5.dat"),.TC_index('+TC_index+"))"#,981,1515,2341,2778,512)' # Parameter string for possible LUT file
        if 'F3' in m.name:
            if 'D5F4D5' in m.name:
                TC_index = "4'b0111"
                m.parameters = '#(.BARREL(0),.InvR_FILE("InvRTable_TC_F3D5F4D5.dat"),.InvT_FILE("InvTTable_TC_F3D5F4D5.dat"),.TC_index('+TC_index+"),.Z1MEAN(14'sd3294),.Z2MEAN(14'sd3917))"#,981,1515,3294,3917,512)' # Parameter string for possible LUT file #HERE!!!!
        if 'F1' in m.name:
            if 'D5L1D4' in m.name:
                TC_index = "4'b0110" 
                m.parameters = '#(.BARREL(0),.InvR_FILE("InvRTable_TC_F1D5L1D4.dat"),.InvT_FILE("InvTTable_TC_F1D5L1D4.dat"),.TC_index('+TC_index+"))"#,981,1515,2341,2778,512)' # Parameter string for possible LUT file
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done4_0 = True
    if m.module == 'ProjectionTransceiver':
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'

        if 'L3F3F5' in m.name:
            m.parameters = '#("L3F3F5")'
            d_ins = PTdict.L3F3F5_ins
            d_outs = PTdict.L3F3F5_outs
        elif 'L2L4F2' in m.name:
            m.parameters = '#("L2L4F2")'
            d_ins = PTdict.L2L4F2_ins
            d_outs = PTdict.L2L4F2_outs
        elif 'F1L5' in m.name:
            m.parameters = '#("F1L5")'
            d_ins = PTdict.F1L5_ins
            d_outs = PTdict.F1L5_outs
        elif 'L1L6F4' in m.name:
            m.parameters = '#("L1L6F4")'
            d_ins = PTdict.L1L6F4_ins
            d_outs = PTdict.L1L6F4_outs

        #print m.inputs[0].split('_')
                                        
        m.in_names = ['projin_disk_'+str(x) for x in range(1,8)] + ['projin_layer_'+str(x) for x in range(1,14)]
        ins = []
        #m.inputs = sorted(sorted(m.inputs, key=lambda i:(i.split('_')[2])[3]), key=lambda j:(j.split('_')[2])[7])
        for x in d_ins:
            found = False
            z = ''
            for y in m.inputs:
                if x in y:
                    found = True
                    z = y
            if found:
                ins.append(z)
            else:
                ins.append("1'b0")
        m.inputs = ins

        outs = []
        for o in m.outputs:
            if 'wr' not in o:
                outs.append([d_outs[o.split('_')[-2]+'_'+o.split('_')[-1]],o])
        m.outputs = []
        m.out_names = []
        for x in outs:
            m.out_names.append(x[0])
            m.out_names.append(x[0].replace('projout','valid'))
            m.outputs.append(x[1])
            m.outputs.append(x[1]+'_wr_en')
        
        m.out_names = m.out_names+['valid_proj_data_stream','proj_data_stream'] # Outputs to links
        m.in_names = m.in_names+['incomming_proj_data_stream'] # Input from links
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']        
                
    if m.module == 'ProjectionRouter':
        m.outputs.append(m.outputs[-1]+'_wr_en') # Write enable signal to AllProjection memory
        m.out_names.append('valid_data')
        m.outputs = m.outputs + [x+'_wr_en' for x in m.outputs[:-2]] # Write enable to VMProjection memory
        m.out_names = m.out_names + [x+'_wr_en' for x in m.out_names[:-2]]
        if 'PR_L1' in m.name or 'PR_L3' in m.name: # Inner odd parameters
            m.parameters = "#(1'b1,1'b1)"
        elif 'PR_L2' in m.name:
            m.parameters = "#(1'b0,1'b1)"
        elif 'PR_L4' in m.name or 'PR_L6' in m.name: # Outer even parameters
            m.parameters = "#(1'b0,1'b0)"
        elif 'PR_L5' in m.name:
            m.parameters = "#(1'b1,1'b0)"
        elif 'PRD' in m.name:
            if 'PRD_F1' in m.name or 'PRD_F3' in m.name or 'PRD_F5' in m.name or 'PRD_B1' in m.name or 'PRD_B3' in m.name or 'PRD_B5' in m.name:
                m.parameters = "#(1'b1,"  # odd
            if 'PRD_F2' in m.name or 'PRD_F4' in m.name or 'PRD_B2' in m.name or 'PRD_B4' in m.name:
                m.parameters = "#(1'b0,"  # even
	    if 'D5' in m.name or 'D7' in m.name:
		m.parameters += "1'b0"	  # inner (PS modules)
	    if 'D6' in m.name or 'D8' in m.name:
		m.parameters += "1'b1"	  # outer (2S modules)
	    m.parameters += ",1'b0)"	  # barrel
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done6_0 = True
    if m.module == 'MatchEngine':
        m.outputs.append(m.outputs[0]+'_wr_en') 
        m.out_names.append('valid_data')
	if ('_F1D' in m.name or '_F2D' in m.name or '_F3D' in m.name or '_F4D' in m.name or '_F5D' in m.name):
	    m.parameters += "#(.DISK(1'b1))"
	if 'VMPROJ' in m.inputs[1]: #default
          m.start = m.inputs[1].replace(m.name,'')+'start'
          m.done = m.name+'_start'
	elif 'VMPROJ' in m.inputs[0]: #for F5 or B5 VMS is m.inputs[1] b/c these do not have TrackletEngines which change order of wires
          m.start = m.inputs[0].replace(m.name,'')+'start'
          m.done = m.name+'_start'
        seen_done7_0 = True
    if m.module == 'MatchCalculator':
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allprojin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AP_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back

        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allstubin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllStubs and AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AS_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back
        m.outputs.append(m.outputs[0]+'_wr_en') # Write enable for local and neighbor matches
        m.outputs.append(m.outputs[1]+'_wr_en')
        m.outputs.append(m.outputs[2]+'_wr_en')
        if ('L5L6_L1D4' in m.name or 'L5L6_L2D4' in m.name):
	    m.outputs.append(m.outputs[3]+'_wr_en')
        m.out_names.append('valid_matchminus')
        m.out_names.append('valid_matchplus')
        m.out_names.append('valid_match')
        if ('L5L6_L1D4' in m.name or 'L5L6_L2D4' in m.name):
	    m.out_names.append('valid_match2')
        dtcregion = '010'
        if 'D1' in m.name:
            dtcregion = '000'
        elif 'D2' in m.name:
            dtcregion = '001'
        elif 'D3' in m.name:
            dtcregion = '010'
        elif 'D4' in m.name:
            dtcregion = '011'
        elif 'D5' in m.name:
            dtcregion = '100'
        elif 'D6' in m.name:
            dtcregion = '101'
        elif 'D7' in m.name:
            dtcregion = '110'
        elif 'D8' in m.name:
            dtcregion = '111'

        if 'MC_L1L2_L3' in m.name: # Parameter for constants # Will be moved to header file
            m.parameters = "#(3'b"+dtcregion+",1'b1,`PHI_L3,`Z_L3,`R_L3,`PHID_L3,`ZD_L3,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L1L2_L3,`MC_z_L1L2_L3,`MC_zfactor_INNER)"
        if 'MC_L1L2_L4' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b0,`PHI_L4,`Z_L4,`R_L4,`PHID_L4,`ZD_L4,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L1L2_L4,`MC_z_L1L2_L4,`MC_zfactor_OUTER)"
        if 'MC_L1L2_L5' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b0,`PHI_L5,`Z_L5,`R_L5,`PHID_L5,`ZD_L5,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L1L2_L5,`MC_z_L1L2_L5,`MC_zfactor_OUTER)"
        if 'MC_L1L2_L6' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b0,`PHI_L6,`Z_L6,`R_L6,`PHID_L6,`ZD_L6,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L1L2_L6,`MC_z_L1L2_L6,`MC_zfactor_OUTER)"
        if 'MC_L3L4_L1' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b1,`PHI_L1,`Z_L1,`R_L1,`PHID_L1,`ZD_L1,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L3L4_L1,`MC_z_L3L4_L1,`MC_zfactor_INNER)"
        if 'MC_L3L4_L2' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b1,`PHI_L2,`Z_L2,`R_L2,`PHID_L2,`ZD_L2,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L3L4_L2,`MC_z_L3L4_L2,`MC_zfactor_INNER)"
        if 'MC_L3L4_L5' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b0,`PHI_L5,`Z_L5,`R_L5,`PHID_L5,`ZD_L5,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L3L4_L5,`MC_z_L3L4_L5,`MC_zfactor_OUTER)"
        if 'MC_L3L4_L6' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b0,`PHI_L6,`Z_L6,`R_L6,`PHID_L6,`ZD_L6,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L3L4_L6,`MC_z_L3L4_L6,`MC_zfactor_OUTER)"
        if 'MC_L5L6_L1' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b1,`PHI_L1,`Z_L1,`R_L1,`PHID_L1,`ZD_L1,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L5L6_L1,`MC_z_L5L6_L1,`MC_zfactor_INNER)"
        if 'MC_L5L6_L2' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b1,`PHI_L2,`Z_L2,`R_L2,`PHID_L2,`ZD_L2,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L5L6_L2,`MC_z_L5L6_L2,`MC_zfactor_INNER)"
        if 'MC_L5L6_L3' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b1,`PHI_L3,`Z_L3,`R_L3,`PHID_L3,`ZD_L3,`MC_k1ABC_INNER,`MC_k2ABC_INNER,`MC_phi_L5L6_L3,`MC_z_L5L6_L3,`MC_zfactor_INNER)"
        if 'MC_L5L6_L4' in m.name:
            m.parameters = "#(3'b"+dtcregion+",1'b0,`PHI_L4,`Z_L4,`R_L4,`PHID_L4,`ZD_L4,`MC_k1ABC_OUTER,`MC_k2ABC_OUTER,`MC_phi_L5L6_L4,`MC_z_L5L6_L4,`MC_zfactor_OUTER)"
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done8_0 = True
    if m.module == 'DiskMatchCalculator':
        if 'D5' in m.name:
            dtcregion = '100'
	    inner = True 
        elif 'D6' in m.name:
            dtcregion = '101'
	    inner = False
        elif 'D7' in m.name:
            dtcregion = '110'
	    inner = True
        elif 'D8' in m.name:
            dtcregion = '111'
	    inner = False
        
        m.parameters = "#(.DTC_INDEX(3'b"+dtcregion+")"
	if inner:
	    m.parameters += ",.INNER(1'b1)"
	else:
	    m.parameters += ",.INNER(1'b0),.PHICUT(32'sd700921),.RCUT(32'sd128)"
	if 'F3F4' in m.name and 'F5' not in m.name:
	    m.parameters += ",.F1F2SEED(1'b0)"  
	m.parameters += ")"
 
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allprojin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AP_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back
        for i,n in enumerate(m.in_names): # Count the inputs
            if 'allstubin' in n:
                m.in_names.insert(len(m.in_names),m.in_names.pop(i)) # Move the AllStubs and AllProjections to the back
        for i,n in enumerate(m.inputs): # Count the inputs
            if 'AS_' in n:
                m.inputs.insert(len(m.inputs),m.inputs.pop(i)) # Move the AllProjections to the back

        m.outputs = topOfList(m.outputs,'FM_'+m.name.split('_')[1]) # Put at the top of the list
                
        m.outputs = topOfList(m.outputs,'FM_FL3FL4') # Put at the top of the list	
        m.outputs = topOfList(m.outputs,'FM_L1') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'FM_L4') # Put at the top of the list
        if ('MC_F1F2' in m.name):
	    m.outputs = topOfList(m.outputs,'FM_F1L1') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'FM_F1F') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'FM_F3F') # Put at the top of the list

        m.outputs = topOfList(m.outputs,'ToMinus') # Put at the top of the list
        m.out_names = topOfList(m.out_names,'minus') # Put at the top of the list
        m.outputs = topOfList(m.outputs,'ToPlus') # Put at the top of the list
        m.out_names = topOfList(m.out_names,'plus') # Put at the top of the list

        os = []        
        for o in m.outputs:
            os.append(o+'_wr_en')
        m.outputs = m.outputs + os        
        ons = []
        p = 1
        n = 1
        for on in m.out_names:
            if 'plus' in on:
                ons.append('matchoutplus'+str(p))
                p = p+1            
            elif 'minus' in on:
                ons.append('matchoutminus'+str(n))
                n = n+1
            else:
                ons.append(on)
        m.out_names = ons
        os = []
        ons = []
        for o in m.out_names:
            ons.append('valid_'+o)
        for o in outputs:
            os.append(o+'_wr_en')    
        m.out_names = m.out_names + ons
        m.outputs = m.outputs + os
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done8_0 = True
    if m.module == 'MatchTransceiver':
        ons = []
        m.parameters = '#("Layer")'
        if 'FDSK' in m.name:
	    if region == 'D4D6' or region == 'D3D6':
		m.parameters = '#("Hybrid")'
            else:
		m.parameters = '#("Disk")'
            m.inputs = sorted(m.inputs, key=lambda i:(i.split('_')[2])[3])
            if len(m.inputs) > 6:
                for x in xrange(6):
                    m.inputs.insert(6,"1'bX")
                    m.in_names.append('matchin'+str(x+13))
            m.outputs = sorted(m.outputs, key=lambda o:(o.split('_')[2])[3])
        for i,o in enumerate(m.out_names): # Count the outputs
            ons.append(o)
        for i,o in enumerate(m.out_names):
            ons.append('valid_matchout%d'%(i+1))
        m.out_names = ons
        valids = []
        for o in m.outputs:
            valids.append(o+'_wr_en')
        m.outputs = m.outputs + valids
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
             
        m.out_names = m.out_names+['valid_match_data_stream','match_data_stream'] # Output signals to links
        m.in_names = m.in_names+['incomming_match_data_stream'] # Input signals from links
        m.outputs = m.outputs+[m.name+'_To_DataStream_en',m.name+'_To_DataStream']
        m.inputs = m.inputs+[m.name+'_From_DataStream']        
    if m.module == 'FitTrack':        
        if 'L1L2' in m.name:
            m.parameters = '#("L1L2")'
        elif 'L3L4' in m.name:
            m.parameters = '#("L3L4")'
        elif 'L5L6' in m.name:
            m.parameters = '#("L5L6")'
        elif 'F1L' in m.name:
            m.parameters = '#("F1L1")'
        elif 'F1F2' in m.name or 'B1B2' in m.name:
            m.parameters = '#("F1F2")'
        elif 'F3F4' in m.name or 'B3B4' in m.name:
            m.parameters = '#("F3F4")'
                
        m.out_names.append('valid_fit')
        m.outputs.append(m.outputs[0]+'_wr_en')
        for i in m.inputs:
            if 'From' in i:
                m.start = i.replace(m.name,'')+'start'
        m.done = m.name+'_start'
        seen_done10_0 = True
    if m.module == 'PurgeDuplicate':
	if region=='D3D6':
	    m.parameters = '#(.SCOPE("D3D6"))'
	if region=='D4D6':
	    m.parameters = '#(.SCOPE("D4D6"))'
	if region=='D3':
	    m.parameters = '#(.SCOPE("D3"))'
	if region=='D3D4':
	    m.parameters = '#(.SCOPE("D3D4"))'
	if region=='D5':
	    m.parameters = '#(.SCOPE("D5"))'
	if region=='D5D6':
	    m.parameters = '#(.SCOPE("D5D6"))'
        for x in range(1,len(m.outputs)+1):
            m.out_names.append('valid_out_'+str(x))
        os = []
        for o in m.outputs:
            os.append(o+'_wr_en')
        m.outputs += os
        m.start = m.inputs[0].replace(m.name,'')+'start'
        m.done = m.name+'_start'
        m.in_names.append('')
    ####################################################
    if('mod' not in sys.argv): # If you don't want processing modules in the print out
        string_processing += '\n'
        string_processing += '\n' +  m.module + ' ' +m.parameters + ' ' +m.name + '('
        k = 1
        if m.module == 'ProjectionRouter':
            #print m.inputs
            while len(m.inputs) < 7:
                m.inputs.append("1'b0")
                m.in_names.append('proj'+str(len(m.inputs))+'in')
                
        if m.module == 'MatchTransceiver':
            ins = [x for x in m.inputs if 'Stream' not in x]
            while len(ins) < 24:
                m.inputs.append("1'b0")
                ins.append("1'b0")
                m.in_names.append('matchin'+str(len(ins)))

        for n,i in zip(m.in_names,m.inputs): # Loop over inputs and input names
            if m.module != 'LayerRouter' and m.module != 'DiskRouter': # Special cases for signals without normal read_add
                if n == 'tpar1in':
                    string_processing += '\n' +  '.read_add_pars1('+i+'_read_add),'
                elif n == 'tpar2in':
                    string_processing += '\n' +  '.read_add_pars2('+i+'_read_add),'
                elif n == 'tpar3in':
                    string_processing += '\n' +  '.read_add_pars3('+i+'_read_add),'
                elif n == 'incomming_proj_data_stream':
                    string_processing += '\n' +  '.valid_incomming_proj_data_stream('+i+'_en),'
                elif n == 'incomming_match_data_stream':
                    string_processing += '\n' +  '.valid_incomming_match_data_stream('+i+'_en),'
                elif 'fullmatch' in n:
                    string_processing += '\n' +  '.number'+n.split('match')[-1]+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add'+n.split('match')[-1]+'('+i+'_read_add),'
                    string_processing += '\n' +  '.read_en'+n.split('match')[-1]+'('+i+'_read_en),'
                elif 'allstubin' in n:
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
                elif 'allprojin' in n:
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
                elif 'trackin' in n:
                    string_processing += '\n' +  '.numberin'+n[-1]+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
                    string_processing += '\n' +  '.index_in'+n[-1]+'('+i+'_index),'
                elif "1'b0" in i:
		    if 'matchin' in n:
                    	string_processing += '\n' +  '.number_in'+n.split('matchin')[-1]+"(6'b0),"
		    else:
                    	string_processing += '\n' +  '.number_in_'+n+"(6'b0),"
                elif "1'bX" in i:
                    string_processing += '\n' +  '.number_in'+n.split('matchin')[-1]+"(6'b0),"
                elif 'matchin' in n:
                    string_processing += '\n' +  '.number_in'+n.split('matchin')[-1]+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add'+n.split('matchin')[-1]+'('+i+'_read_add),'
                    string_processing += '\n' +  '.read_en'+n.split('matchin')[-1]+'('+i+'_read_en),'
                else:
                    string_processing += '\n' +  '.number_in_'+n+'('+i+'_number),'
                    string_processing += '\n' +  '.read_add_'+n+'('+i+'_read_add),'
            if "1'b0" not in i and "1'bX" not in i:
                string_processing += '\n' +  '.'+n+'('+i+'),' # Write the signal name
            k = k + 1

            
        for n,o in zip(m.out_names,m.outputs): # Loop over outputs and output names 
            string_processing += '\n' +  '.'+n+'('+o+'),'
        string_processing += '\n' +  '.start('+m.start+'),'
        string_processing += '\n' +  '.done('+m.done+'),'
        string_processing += '\n' +  m.common
        string_processing += '\n' +  ');'

# Write the final lines

for ep in epilogue:
    string_epilogue += '\n' +  ep.strip()
    
starts = [x.split('),')[0] for x in (string_memories+string_processing).split('.start(')]

for x in set(starts[1:]):
    if len(x)>1 and 'IL' not in x:
        string_starts += '\n' +  'wire [1:0] '+ x +';'

if region == 'D3':
    print 'Processing D3'
    print 'Memories implemented=',len(memories)
    print 'Processing modules implemented=',len(modules)
    string_prologue = string_prologue.replace('Tracklet_processing','Tracklet_processingD3')
if region == 'D5':
    print 'Processing D5'
    print 'Memories implemented=',len(memories)
    print 'Processing modules implemented=',len(modules)
    string_prologue = string_prologue.replace('Tracklet_processing','Tracklet_processingD5')
if region == 'D3D4':
    print 'Processing D3D4'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD3D4')
if region == 'D3D6':
    print 'Processing D3D6'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD3D6')
if region == 'D5D6':
    print 'Processing D5D6'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD5D6')
if region == 'D4D5':
    print 'Processing D4D5'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD4D5')
if region == 'D4D6':
    print 'Processing D4D6'
    print 'Memories implemented =',len(memories)
    print 'Processing modules implemented =',len(modules)
    string_prologue = string_prologue.replace('module Tracklet_processing','module Tracklet_processingD4D6')
    
g = open('test.txt','w')
g.write(string_prologue)
g.write(string_starts)
g.write(string_memories)
g.write(string_processing)
g.write(string_epilogue)
