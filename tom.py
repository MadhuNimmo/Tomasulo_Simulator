import sys
def read_inp(input):
    global inst_queue=[]
    global inp_cnt=0
    fp = open(input,'r')
    lines = fp.read().splitlines()
    for line in lines:
        inst_queue.append(line)
    fp.close()
    inp_cnt = inst_queue.length


def init_pars():
    #func_units=[None]*2
    #res_stations=[None]*2
    global inp_cnt,inst_queue
    inst_status= ['Issue','Execute','Write result','Commit'];

    add_cycles=2
    mult_cycles=20

    adder_units=3
    multiplier_units=3
    branch_unit=3
    ldstr_units=3

    issues=1

    mem_busy=False

    branch_pred="NT"

    inst_cnt=0

    rsrv_stn = {'cycle': -1, 'exec': -1, 'BUSY': 'N', 'op': 'NULL', 'Vj':0, 'Vk':0, 'Qj':-1, 'Qk':-1, 'Dest':-1, 'A':0}

	for cnt in range(0, inp_cnt):
    	

def main():
    no_of_inp= len(sys.argv)
    if no_of_inp < 2:
        print("Input Instruction File missing")
        exit(1)
    elif no_of_inp > 2:
        print("Too many inputs")
        print("Inputs expected: {filename for instruction set}")
    else:
        read_inp(sys.argv[1])

main()
