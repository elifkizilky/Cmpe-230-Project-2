#!/usr/bin/python3
import sys
import re

"""
Takes operand and address_mode as parameter and 
returns the data in 16 bit binary by finding where it is
looking the address_mode

operand => 16 bit binary  address_mode => hex 
data => 16 bit binary
"""
def process_data(operand, address_mode):
    global registers,memory
    data = ""
    if address_mode == 0: #operand is immediate data
        data = operand
    elif address_mode == 1: #operand is given in the register
        data = registers[int("0b"+operand,2)]   
    elif address_mode == 2: #operand's memory address given in the register
        address = int("0b"+registers[int("0b"+operand,2)],2)

        #if given part of memory is undeclared, default value is zero
        dataup = memory.get(address,"00000000") #taking the first part of the data 
        datalow = memory.get(address+1,"00000000") #taking the second part of the data
        data = dataup + datalow
    elif address_mode == 3: #operand is memory address
        address = int("0b"+operand, 2)
        dataup = memory.get(address,"00000000") #taking the first part of the data
        datalow = memory.get(address+1,"00000000") #taking the second part of the data
        data = dataup + datalow
    return data

"""
Takes result of the operation as parameter and
sets the flags accordingly. Converts the result to 17
bit binary since an operation can produce 17 bit result at most.
Then looks for the flags.
"""
def flagcheck(result):
    global ZF,SF,CF
    
    result = format(result, '017b')
    if int("0b"+result[1:], 2) == 0:
        ZF = True
    else:
        ZF = False
    
    if result[0] == "1":
        CF = True
    else:
        CF = False
    
    if result[1] == "1":
        SF = True
    else:
        SF = False

"""
Takes the 16 bit binary as parameter and flips the bits
(Takes complement of digits)
"""
def flip_bits(binary): #takes the 16 bit 
    result = ""
    for i in binary:
        if  i=="0":
            result += "1"
        else:
            result += "0"
    return result

"""
Halts the program
(pseudo parameters)
"""
def halt(operand,address_mode):
    for character in outputl:
        file.write(character+"\n")
    exit()

"""
Calls the process_data function to take the data
and load it to register A
"""
def load(operand, address_mode):
    global registers
    data = ""
    data = process_data(operand, address_mode)
    registers[1] = data

"""

"""
def store(operand, address_mode):

    global registers
    if address_mode<1:
        print("Error: invalid address mode")
        exit()
    data = registers[1] #16 bit

    operand = int("0b" + operand, 2) #to decimal
    if address_mode == 1: #stores to register
        registers[operand] = data
    elif address_mode == 2: #stores to memory address given in the register
        address = int("0b"+registers[operand],2) #decimal
        memory[address] = data[0:8] #first byte of the data
        memory[address + 1] = data[8:] #second byte of the data
    elif address_mode == 3: #stores to memory address 
        address = operand
        memory[address] = data[0:8] #first byte of the data
        memory[address + 1] = data[8:] #second byte of the data

"""
Calls the process_data to take the data, then adds the 
data to the number in the register A in decimal. Then calls
the flagcheck function to set the flags 
"""
def add(operand, address_mode):
    global SF,ZF,CF, registers
    data1 = process_data(operand, address_mode)
    data1 = int("0b" + data1,2) #to decimal
    data2 = int("0b" + registers[1],2) #to decimal
    summation = data1 + data2
    flagcheck(summation)
    summation = format(summation, '017b')
    #summation = summation[1:]
    registers[1] = summation[1:]

"""
Calls the process_data to take the data2, then subtracts from
the number in the register A according to 2's complement. 
A + not(OPR) + 1 (not(OPR), corresponds to flip_bits function)
Then calls the flagcheck to set the flags. 

"""
def sub(operand,address_mode):
    global SF,ZF,CF,registers
    data1 = int("0b" + registers[1],2)
    data2 = process_data(operand,address_mode)
    data2 = flip_bits(data2)
    data2 = int("0b" + data2,2)+1
    result = data1+data2#what if negative
    flagcheck(result)
    result = format(result, '017b') #string
    registers[1] = result[1:]

"""
Calls the process_data function to take the data and then 
increments it by 1 then sets the flag by calling flagcheck function, 
then stores that result according to address_mode
"""
def inc(operand,address_mode):
    global SF,ZF,CF,registers
    data = process_data(operand, address_mode)
    data_int = int("0b" + data,2)
    result = data_int+1
    flagcheck(result)
    #flagcheck(data_int)
    result = format(result, '017b') #string
    result = result[1:]
    
    if address_mode == 1: #stores to register
        registers[int("0b"+operand,2)] = result
    elif address_mode == 2: #stores to memory given in the register
        address = int("0b"+registers[int("0b"+operand,2)],2)  
        memory[address] = result[0:8]
        memory[address + 1] = result[8:]
    elif address_mode == 3: #stores to memory address
        address = int("0b"+operand,2)
        memory[address] = result[0:8]
        memory[address + 1] = result[8:]

"""
Calls the process_data function to take the data
then add it to -1 in binary (converting to decimal => 65535)
and then calls the flagcheck to set the flags. Finally it subtracts
65536 from the result since in 2's complement, the most significant bit
has negative value when converting to decimal.
Then stores the result accorcing to address_mode.
"""
def dec(operand, address_mode):
    global SF,ZF,CF,registers
    data = process_data(operand, address_mode)
    data_int = int("0b" + data,2)
    data2 = 65535   #negative one in binary
    result = data_int+data2 
    flagcheck(result)
    result = result -65536
    result = format(result, '017b') 
    result = result[1:]
    if address_mode == 1: #stores to register
        registers[int("0b"+operand,2)] = result
    elif address_mode == 2: #stores to memory address given in the register
        address = int("0b"+registers[int("0b"+operand,2)],2)  
        memory[address] = result[0:8]
        memory[address + 1] = result[8:]
    elif address_mode == 3: #stores the memory address
        address = int("0b"+operand,2)
        memory[address] = result[0:8]
        memory[address + 1] = result[8:]

"""
Calls the process_data function to take the data
then xor the data and the data in the register A. 
Then sets the flags SF and ZF. Stores the result in
register A.
"""
def Xor(operand, address_mode):
    global registers, SF,ZF
    data1 = process_data(operand,address_mode) #16 bit string
    data2 = registers[1] #16 bit string
    result = int("0b" + data1, 2) ^ int("0b" + data2,2) #decimal
    result = format(result, '016b') #16 bit string
    if result[0] == "1":
        SF = True
    else:
        SF = False
    if int("0b" +result,2) == 0:
        ZF = True
    else:
        ZF = False
    registers[1] = result

"""
Calls the process_data function to take the data
then ands the data and the data in the register A. 
Then sets the flags SF and ZF. Stores the result in
register A.
"""
def And(operand,address_mode):
    global registers, SF,ZF
    data1 = process_data(operand,address_mode) #16 bit string
    data2 = registers[1] #16 bit string
    result = int("0b" + data1, 2) & int("0b" + data2,2) #decimal
    result = format(result, '016b') #16 bit string
    if result[0] == "1":
        SF = True
    else:
        SF = False
    if int("0b" +result,2) == 0:
        ZF = True
    else:
        ZF = False
    registers[1] = result

"""
Calls the process_data function to take the data
then "or"s the data and the data in the register A. 
Then sets the flags SF and ZF. Stores the result in
register A.
"""
def Or(operand, address_mode):
    global registers, SF,ZF
    data1 = process_data(operand,address_mode) #16 bit string
    data2 = registers[1] #16 bit string
    result = int("0b" + data1, 2) | int("0b" + data2,2) #decimal
    result = format(result, '016b') #16 bit string
    if result[0] == "1":
        SF = True
    else:
        SF = False
    if int("0b" +result,2) == 0:
        ZF = True
    else:
        ZF = False
    registers[1] = result

"""
Calls the process_data function to take the data
then takes the complement of the data by calling the flip_bits
function.Then sets the flags SF and ZF. Stores the result
according to address_mode
"""
def Not(operand, address_mode):
    global SF,ZF,registers
    data = process_data(operand, address_mode)
    result = flip_bits(data)
    if result[0] == "1":
        SF = True
    else:
        SF = False
    if int("0b" +result,2) == 0:
        ZF = True
    else:
        ZF = False
    if address_mode == 1: #stores to register
        registers[int("0b"+operand,2)] = result
    elif address_mode == 2: #stores to memory address given in the register
        address = int("0b"+registers[int("0b"+operand,2)],2)  
        memory[address] = result[0:8]
        memory[address + 1] = result[8:]
    elif address_mode == 3: #stores to memory address
        address = int("0b"+operand,2)
        memory[address] = result[0:8]
        memory[address + 1] = result[8:]
"""
Shifts the operand to the right in register by 1 bit. Checks if the address mode
is not 1 since it is not allowed. Then shifts the bits by
using slicing. Then sets the flags SF and ZF.
"""
def shiftright(register,address_mode):
    global SF,ZF, registers
    if address_mode!=1:
        print("Error: invalid address mode")
        exit()
    register = int("0b" + register, 2) #to decimal, since register is named according to decimal
    num = registers[register] #takes the data from register
    num = num[0:len(num)-1] #shifts it to right
    num = "0"+num #puts 0 to the begining
    sign = num[0:1]
    if(sign=="1"):
        SF = True
    else:
        SF = False
    if(int(num, 16)==0):
        ZF = True
    else:
        ZF = False
    registers[register] = num #stores it to the register

"""
Shifts the operand to the left in register by 1 bit. Checks if the address mode
is not 1 since it is not allowed. Then shifts the bits by
using slicing. Then sets the flags SF, ZF and ZF.
"""
def shiftleft(register,address_mode):
    global SF,ZF,CF, registers
    if address_mode!=1:
        print("Error: invalid address mode")
        exit()
    register = int("0b" + register, 2)
    num = registers[register]
    #carrycheck  
    carry = num[0:1]
    if(carry=="1"):
        CF = True
    else:
        CF = False
    num = num[1:]  #shifts it to left 
    num = num+"0" #puts 0 to the end
    #signcheck
    sign = num[0:1]
    if(sign=="1"):
        SF = True
    else:
        SF = False
    #zerocheck
    if(int(num, 16)==0):
        ZF = True
    else:
        ZF = False
    registers[register] = num #stores it to the register

#just passes
def nop(operand,address_mode):
    pass

"""
Pushes the data in the register to stack and then decrements
S by 2. Checks if the address_mode is not 1 since it is not allowed
otherwise. Stores the data to the pointed address by S
"""
def Push(operand,address_mode):
    #modified , needs to be checked
    global registers,stack
    if address_mode!=1:
        print("Error: invalid address mode")
        exit()
    data = registers[int("0b" + operand, 2)]
    stack.append(data)#16 bit string
    memory[registers[6]]=data[0:8]
    memory[registers[6]+1]=data[8:]
    registers[6] = registers[6]-2

"""
Pops the data to the register from stack and then increments
S by 2. Checks if the address_mode is not 1 since it is not allowed
otherwise. Clears the data from the pointed address by S
"""
def Pop(operand,address_mode):
    #modified, needs to be checked
    global registers,stack
    if address_mode!=1:
        print("Error: invalid address mode")
        exit()
    data = stack.pop()
    registers[int("0b" + operand, 2)] = data
    memory.pop(registers[6]+2)
    memory.pop(registers[6]+3)
    registers[6] = registers[6]+2
"""
Calls the process_data function to take the data, then
compares the data with the data in the register A and sets 
the flags accordingly
operation => A-OPR => = A + flip_bits (OPR)+ 1
"""
def Cmp(operand,address_mode):
    global registers
    data1 = registers[1]#16 bit
    data2 = process_data(operand,address_mode)#16 bit
    data2 = flip_bits(data2)
    data1 = int("0b"+data1,2)
    data2 = int("0b"+data2,2)+1
    result = data1 + data2
    flagcheck(result)

"""
Calls the process_data to take the addres, then jumps to the given
address by setting the PC aka. Program counter. Checks if the address 
mode is 0 or not since the other modes are not allowed.
"""
def Jmp(operand,address_mode):
    global PC
    if address_mode!=0:
        print("Error: invalid address mode")
        exit()
    address = process_data(operand,address_mode)
    PC = int("0b"+address,2)

"""
Calls the process_data to take the addres, then jumps to the given address 
if ZF==True by setting the PC aka.Program counter. Checks if the address mode 
is 0 or not since the other modes are not allowed.
"""
def Jz(operand,address_mode):
    global ZF,PC
    if address_mode!=0:
        print("Error: invalid address mode")
        exit()
    if ZF == True:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)

"""
Calls the process_data to take the addres, then jumps to the given address 
if ZF==False by setting the PC aka.Program counter. Checks if the address mode 
is 0 or not since the other modes are not allowed.
"""
def Jnz(operand,address_mode):
    global ZF,PC
    if address_mode!=0:
        print("Error: invalid address mode")
        exit()
    if ZF == False:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)

"""
Calls the process_data to take the addres, then jumps to the given address 
if CF==True by setting the PC aka.Program counter. Checks if the address mode 
is 0 or not since the other modes are not allowed.
"""
def Jc(operand,address_mode):
    global CF,PC
    if address_mode!=0:
        print("invalid address mode")
        exit()
    if CF == True:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)

"""
Calls the process_data to take the addres, then jumps to the given address 
if CF==False by setting the PC aka.Program counter. Checks if the address mode 
is 0 or not since the other modes are not allowed.
"""
def Jnc(operand,address_mode):
    global CF,PC
    if address_mode!=0:
        print("invalid address mode")
        exit()
    if CF == False:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)

"""
Calls the process_data to take the addres, then jumps to the given address 
if  SF==False & ZF= False by setting the PC aka.Program counter. Checks if the 
address mode is 0 or not since the other modes are not allowed.
"""
def Ja(operand,address_mode):
    global SF,ZF,PC
    if address_mode!=0:
        print("invalid address mode")
        exit()
    if SF == False and ZF == False:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)
"""
Calls the process_data to take the addres, then jumps to the given address 
if  SF==False or ZF==True or CF==True by setting the PC aka.Program counter. 
Checks if the address mode is 0 or not since the other modes are not allowed.
"""
def Jae(operand,address_mode):
    global SF,ZF,PC
    if address_mode!=0:
        print("invalid address mode")
        exit()
    if SF == False or CF == True or ZF == True:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)

"""
Calls the process_data to take the addres, then jumps to the given address 
if SF==True and ZF==False by setting the PC aka.Program counter. 
Checks if the address mode is 0 or not since the other modes are not allowed.
"""
def Jb(operand,address_mode):
    global SF,ZF,PC
    if address_mode!=0:
        print("invalid address mode")
        exit()
    if SF == True and ZF == False:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)
"""
Calls the process_data to take the addres, then jumps to the given address 
if SF==True or ZF==True by setting the PC aka.Program counter. 
Checks if the address mode is 0 or not since the other modes are not allowed.
"""
def Jbe(operand,address_mode):
    global SF,ZF,PC
    if address_mode!=0:
        print("invalid address mode")
        exit()
    if SF == True or ZF == True:
        address = process_data(operand,address_mode)
        PC = int("0b"+address,2)
"""
Reads a character (1 length) input from the console, and
stores it to the register or memory. Checks if the address mode 
is 0 since it is not allowed. Converts the character to 16 bit 
data using ASCII code. Then stores it to the address looking to the
address_mode.
"""
def Read(operand,address_mode):
    global registers,memory
    if address_mode==0:
        print("Error: invalid address mode")
        exit()
    character = input()
    if len(character) > 1:
        print("Error: invalid character")
        exit()
    character_bin = format(ord(character),"016b")
    if address_mode == 1: #stores to the register
        registers[int("0b"+operand,2)] = character_bin
    elif address_mode == 2: #stores to the address given in the register
        address = int("0b"+registers[int("0b"+operand,2)],2)  
        memory[address] = character_bin[0:8] #first byte of the data
        memory[address + 1] = character_bin[8:] #second byte of the data
    elif address_mode == 3: #stores to the memory addres
        address = int("0b"+operand,2)
        memory[address] = character_bin[0:8] #first byte of the data
        memory[address + 1] = character_bin[8:] #second byte of the data

"""
Calls the process_data function to take the data, then
prints the data to the the file.
"""
def Print(operand,address_mode):
    global outputl
    data = process_data(operand,address_mode)
    character_dec = int("0b"+data,2)
    character = chr(character_dec)
    outputl.append(character)
    
    
"""
Represents the instructions with fields: instruction (itself), 
opcode => instruction code, address_mode => address mode, operand => operand
"""
class Instr:
    def __init__(self, _instruction):
        self.instruction = _instruction
        operation = self.instruction[0:2] #taking instructions opcode+addressing mode(hex)
        _operand = self.instruction[2:] #taking operand(hex)
        #to decimal
        dec_operation = int(str(operation),16) 
        dec_operand = int(str(_operand),16)
        #to binary
        b_operand = format(dec_operand, '016b') 
        b_operation = format(dec_operation, '08b') 

        self.opcode = int(str(b_operation[0:6]),2) #integer decimal
        self.address_mode = int(str(b_operation[6:]),2) # integer decimal
        self.operand = b_operand #string 16 bits binary

ZF = False #zero flag
SF = False #sign flag
CF = False #carry flag
PC = False #program counter

argument = sys.argv[1]
outputl = []
file= open(argument[0:argument.index(".")]+ ".txt", "w")
registers = {1:"",2:"",3:"",4:"",5:"",6:65534} #registers are represented in hex corresponding bit patterns, data is string 16 bit binary except S
stack = [] #Program stack

memory = {"":"000000"} #represents the memory structure, address =>integer decimal, data => string binary data
file1 = open(sys.argv[1], "r")
instructions = []
mem_index = 0 #points the memory index that will be filled

for line in file1:
    instructions.append(Instr(line))
    #Instruction is 3 byte but memory addresses store 1 byte, thus instruction is divided to 3 parts
    memory[mem_index] = format(int( line[0:2], 16), '016b') #first 2 bit of instruction includes opcode & address mode
    mem_index += 1
    memory[mem_index] = format(int( line[2:4], 16), '016b') #first half of 16 bit data aka. 8 bit
    mem_index += 1
    memory[mem_index] = format(int( line[4:6], 16), '016b') #second half of 16 bit data aka. 8 bit
    mem_index += 1

funcs = { #holds the corresponding instruction functions, key => opcode in decimal, value => function
    1:halt,
    2:load,
    3:store,
    4:add, 
    5:sub,
    6:inc,
    7:dec,
    8:Xor,
    9:And,
    10:Or,
    11:Not,
    12:shiftleft, 
    13:shiftright,
    14:nop,
    15:Push,
    16:Pop,
    17:Cmp,
    18:Jmp,
    19:Jz,
    20:Jnz,
    21:Jc,
    22:Jnc,
    23:Ja,
    24:Jae,
    25:Jb,
    26:Jbe,
    27:Read,
    28:Print
    }

#continues until no instructions left
while(PC<len(instructions)*3):
    instr = instructions[PC//3]
    PC+=3 #PC increments by the length of instruction
    opcode = instr.opcode
    address_mode = instr.address_mode
    operand = instr.operand
    funcs[opcode](operand,address_mode) #calling function
    
for character in outputl:
    file.write(character+"\n")
