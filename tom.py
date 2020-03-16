#!/usr/bin/python
import sys
import re

#Cycles allowed
global cyc_add, cyc_mul
cyc_add  = 2
cyc_mul  = 20
 
#Reservation stations
global rsrvtn_stn, res_cnt,rs_init,status_q
rsrvtn_stn = {}
res_cnt={'LD': 5, 'SD': 5, 'ADD': 3, 'MUL': 3, 'BNEZ': 2}
rs_init={'inst': None, 'count': None, 'src1': None, 'src2': None, 'dest': None}
status_q={"ADD":False,"MUL":False,"LD":False,"SD":False,"BNEZ":False}

##Execution unit and trackers
global counter, inst_list, exec_stn,done_counter,BRANCH_PREDICTION
exec_stn={}
counter= 1
done_counter=1
inst_list = {}
BRANCH_PREDICTION="NT"

#Other variables
global inst_history,instruction_file,lines
inst_history = {}
lines=""
instruction_file=""

def parse_input():
    #Parsing input
    global lines,instruction_file
    no_of_inp= len(sys.argv)
    if no_of_inp < 2:
        print("Input Instruction File missing")
        exit(1)
    elif no_of_inp > 2:
        print("Too many inputs")
        print("Inputs expected: {filename for instruction set}")
    else:
    	instruction_file=sys.argv[1]

def read_inp(input):
    #Reading instruction set
    global lines
    fp = open(input,'r')
    lines = fp.read().splitlines()
    fp.close()
		

def initial_setup():
        global rsrvtn_stn,counter,exec_stn,rs_init
	global lines
	
	if(BRANCH_PREDICTION == "T"):
        	bnez_inst=[]
                for i in range(0,len(lines)):
        		if lines[i].startswith("BNEZ"):
				for j in range(0,i+1):
        					bnez_inst.append(lines[j])

		if len(bnez_inst)>0:				
			for i in range(0,3):
        			lines.extend(bnez_inst)

	#Reservation sation setup
	for res in res_cnt:
		for i in range(0, res_cnt[res]):
			rsrvtn_stn[res,i]= rs_init
	
	#Execution pipeline setup	
	for inst in lines:
		#fix inst_track, no use
		exec_stn[counter,inst]={'done': None, 'issue': None, 'exec': None, 'mem': None, 'wb': None, 'commit': None}
		inst_list[counter] =  inst	
		counter += 1


def check_free_resource(inst_typ,inst, count, des_reg, src_reg1, src_reg2):
        #Checking for free resources
        global rsrvtn_stn
	avail_res = None
	if(inst_typ=="LD"):
		res_unit = "LD"
	elif(inst_typ=="SD"):
        	res_unit = "SD"
	elif(inst_typ in ["MUL","DIV"]):
		res_unit="MUL"
	elif(inst_typ in ["ADD","SUB"]):
		res_unit="ADD"
	else:
        	res_unit = "BNEZ"
	for i in range(0, res_cnt[res_unit]):
		if(rsrvtn_stn[res_unit, i]["inst"] == None):
			rsrvtn_stn[res_unit,i]={'inst': inst, 'count': count, 'src1': src_reg1, 'src2': src_reg2, 'dest': des_reg}
			avail_res = 1
			return (avail_res)		

def free_reserve(count,inst_typ, inst):
        #Freeing up resources
	global rsrvtn_stn,rs_init
	if(inst_typ=="LD"):
        	res_unit = "LD"
	elif(inst_typ=="SD"):
        	res_unit = "SD"
	elif(inst_typ in ["MUL","DIV"]):
		res_unit="MUL"
	elif(inst_typ in ["ADD","SUB"]):
		res_unit="ADD"
	else:
        	res_unit = "BNEZ"
	for i in range(0, res_cnt[res_unit]):
		if(rsrvtn_stn[res_unit, i]["inst"] == inst and rsrvtn_stn[res_unit, i]["count"] == int(count)):
			rsrvtn_stn[res_unit,i]= rs_init

def parse_inst(inst):
        #Fetching information from instruction set
	regex_pattern = re.search('(LD)\s+(\S+)\s*,\s*(\S+)', inst)
	if(regex_pattern):
        	inst_typ = regex_pattern.group(1)
		des_reg = regex_pattern.group(2)
        	src_reg1 = regex_pattern.group(3)
		src_reg2 = None
		return (inst_typ,des_reg, src_reg1, src_reg2)

	regex_pattern = re.search('(ADD|SUB|MUL|DIV)\w*\s+(\S+)\s*,\s*(\S+)\s*,\s*(\S+)', inst)
	if(regex_pattern):
        	inst_typ = regex_pattern.group(1)
		des_reg  = regex_pattern.group(2)
        	src_reg1 = regex_pattern.group(3)
		src_reg2 = regex_pattern.group(4)
		return (inst_typ,des_reg, src_reg1, src_reg2)

	regex_pattern = re.search('(SD|BNEZ)\w*\s+(\S+)\s*,\s*(\S+)\s*', inst)
	if(regex_pattern):
        	inst_typ = regex_pattern.group(1)
		des_reg  = None
        	src_reg1 = regex_pattern.group(2)
		src_reg2 = regex_pattern.group(3)
		return (inst_typ,des_reg, src_reg1, src_reg2)
		
	print "Instruction format not supported: ", inst 
	return
	
def issue_inst(count,inst,clock):
        global exec_stn,inst_history
	exec_stn[count, inst]["issue"] = clock
	inst_history[count] = inst
	return

def exec_inst(count,inst,clock,inst_typ):
        global exec_stn
	exec_stn[count, inst]["exec"] = clock
	return 	

def mem_inst(count,inst,clock,inst_typ):
        global exec_stn,status_q
	exec_stn[count, inst]["wb"] = clock
	exec_stn[count, inst]["done"] = 1				
	return

def display_output():
        #Printing results
        global exec_stn, counter, inst_list
	
	out = '%2s %16s %10s %5s %5s %5s %5s' % ("Number", "Instruction", "Issue", "Execution", "Memory", "WriteBack", "Commit")
	print out
	keys=["issue", "exec", "mem", "wb", "commit"]

	for count in range(1, counter):
		issue = "" 
		exec_i = ""
		mem  = ""
		wb = ""
		commit = ""
		lst=[]
		inst = inst_list[count]
		lst.append(count)
		lst.append(inst)
		for k in keys:
			if(exec_stn[count,inst][k]):
				lst.append(exec_stn[count,inst][k])
			else:
				lst.append("")
		out= '%2s %18s %10s %7s %7s %8s %8s' % tuple(lst)
		print out

def main():
    global instruction_file
    ##Preprocessing 
    parse_input()
    read_inp(instruction_file)
    initial_setup()
    ##Simulation
    tomasulo_sim()
    ##Display 
    display_output()

def tomasulo_sim():
	global exec_stn, counter, inst_list,done_counter,status_q
	clock = 0
	cnt_inst = 1
	
	while(1):
		not_ready = 0
		free_res=[]
		for count in range(1, cnt_inst):

			inst = inst_list[count] 
			
			if(exec_stn[count, inst]["done"] == 1):
				continue
			inst_typ, des_reg, src_reg1, src_reg2 = parse_inst(inst)
			avail_res = None
			if(exec_stn[count, inst]["issue"] == None and not_ready == 0):
				avail_res = check_free_resource(inst_typ,inst, count, des_reg, src_reg1, src_reg2)

			
			if(exec_stn[count, inst]["issue"] == None and avail_res == None):
				not_ready = 1
				continue
			
			not_ready_conflict = None
			dep = None
        		if( (inst_typ in ["LD","SD"] and  exec_stn[count, inst]["mem"] == None ) or ( inst_typ not in ["LD","SD"] and exec_stn[count, inst]["exec"] == None) ):
        
				not_ready_conflict, dep = data_dependencies(inst, count, des_reg, src_reg1, src_reg2, inst_history)
			
			if(status_q["BNEZ"]==True):
				not_ready_conflict = 1
							
			if(inst_typ == "LD"):			
				##WB
				if(exec_stn[count, inst]["mem"] and not_ready_conflict == None ):
					mem_inst(count, inst,clock,"LD")
					done_counter+=1
					free_res.append([count,inst_typ,inst])
					
				##Mem
				elif(exec_stn[count, inst]["exec"] ):
					exec_stn[count, inst]["mem"] = clock
					status_q["LD"]=False
			
				##Exec
				elif(exec_stn[count, inst]["issue"] and status_q["BNEZ"]==False and status_q["LD"] == False and not_ready_conflict == None): 
					exec_inst(count,inst,clock,inst_typ)

				##Issue 
				elif(exec_stn[count, inst]["issue"] == None):
					issue_inst(count, inst,clock)
								
			elif(inst_typ == "SD"):			
				##Mem
				if(exec_stn[count, inst]["exec"] and not_ready_conflict == None):
					exec_stn[count, inst]["mem"] = clock
					status_q["SD"]=False
					exec_stn[count, inst]["done"] = 1
					done_counter+=1
					free_res.append([count,inst_typ,inst])
			
				##Exec
				elif(exec_stn[count, inst]["issue"] and status_q["BNEZ"]==False and status_q["SD"]==False and not_ready_conflict == None):
					exec_inst(count,inst,clock,"SD")
			
				##Issue 
				elif(exec_stn[count, inst]["issue"] == None):
					issue_inst(count, inst,clock)					
			
	
			if(inst_typ in ["ADD","SUB"]):	

				##Mem
				if(exec_stn[count, inst]["exec"] and clock - exec_stn[count, inst]["exec"] == cyc_add ):
					mem_inst(count, inst,clock,"ADD")	
					done_counter+=1		
					free_res.append([count,inst_typ,inst])
					
				##Exec
				elif(exec_stn[count, inst]["issue"]  and not_ready_conflict == None and clock>=status_q["ADD"] ):
					exec_inst(count,inst,clock,"ADD")
					status_q["ADD"]=clock+cyc_add

				##Issue 
				elif(exec_stn[count, inst]["issue"] == None):
					issue_inst(count, inst,clock)				
	
			if(inst_typ in ["MUL","DIV"]):			
				 
				##Mem
				if(exec_stn[count, inst]["exec"] and clock - exec_stn[count, inst]["exec"] == cyc_mul ):
					mem_inst(count, inst,clock,"MUL")
					done_counter+=1	
					free_res.append([count,inst_typ,inst])
				##Exec
				elif(exec_stn[count, inst]["issue"] and not_ready_conflict == None and clock>=status_q["MUL"]):
					exec_inst(count, inst,clock,"MUL")
					status_q["MUL"]=clock+cyc_mul
				##Issue 
				elif(exec_stn[count, inst]["issue"] == None):
					issue_inst(count, inst,clock)										
	
	
			if(inst_typ == "BNEZ"):			
				 
				##Exec
				if(exec_stn[count, inst]["issue"] and not_ready_conflict == None):
					exec_stn[count, inst]["exec"] = clock
					exec_stn[count, inst]["done"] = 1
					done_counter+=1
					free_res.append([count,inst_typ,inst])
					status_q["BNEZ"]=True
				## Issue 
				if(exec_stn[count, inst]["issue"] == None):
					issue_inst(count, inst,clock)			
		clock += 1

		if(free_res):
			for i in range(0,len(free_res)):
				count=free_res[i][0]
				free_reserve(free_res[i][0], free_res[i][1],free_res[i][2])
				inst_history[int(count)] = None	
		
		status_q["BNEZ"]=False		
		free_res=[]
			
		if(cnt_inst < counter and not_ready == 0):	
			cnt_inst += 1

		if counter==done_counter:
        		break
		
		if clock>1000:
			print "Simulation too big/failed"
			return
			
	#Commit instructions
	last_val = 1 
	keys=["wb","mem","exec"]

	for count in inst_list.keys():
		for k in keys:			 
			inst = inst_list[count]
			if(exec_stn[count, inst][k] > 0):
				if(last_val >= exec_stn[count, inst][k] + 1) :
					exec_stn[count, inst]["commit"] = last_val + 1
					last_val = exec_stn[count, inst]["commit"] 
				else:
					exec_stn[count, inst]["commit"] = exec_stn[count, inst][k] + 1
					last_val = exec_stn[count, inst]["commit"]
				break

def data_dependencies(inst, count, des_reg, src_reg1, src_reg2, inst_history):
        global BRANCH_PREDICTION
	busy = None
	dep = None
	for ref_inst in inst_history:
		if(inst_history[ref_inst] == None or int(ref_inst) == int(count)):
			continue
			
		inst_typ,ref_des_reg, ref_src_reg1, ref_src_reg2  = parse_inst(inst_history[ref_inst])
		if( int(count) > int(ref_inst) and ((ref_des_reg == src_reg1 or ref_des_reg == src_reg2 and inst_typ!="BNEZ") or (inst_typ=="BNEZ" and BRANCH_PREDICTION=="T"))):
			busy = 1
			dep  = inst_history[ref_inst]
	return ([busy, dep])

main()  
