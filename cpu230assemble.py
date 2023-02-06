#!/usr/bin/python3
import sys
import re

"""
Converts the input into hex instructions with given parameters
opcode  => int, addrMode => hex, operand => hex
"""
def convert(opcode, addrMode, operand):
	
	addrMode = int(str(addrMode),16)
	operand  = int(str(operand),16)

	bopcode = format(opcode, '06b') 
	baddrmode = format(addrMode, '02b') 
	boperand = format(operand, '016b') 

	bin_instr = '0b' + bopcode + baddrmode + boperand 
	int_instr = int(bin_instr[2:],2) ; 
	hex_instr = format(int_instr, '06x') 
	return hex_instr

"""
Takes hex data as input and decides on address mode
Returns the cleared data in hex, address mode as hex
"""
def take_data(data,addressMode):
	if data[0] == "[" :#data is in memory
		indexLast = data.index("]")
		data = data[1:indexLast]
		tokenCheck = data.split(" ")
		if len(tokenCheck) != 1 :
			print("Error: more than one token")
			exit()
		data.strip()
		if re.match("^(A|B|C|D|E|S|a|b|c|d|e|s)$",data) :#register points to memory
			addressMode = 2
			if data == "A" or data == "a":
				data = 1
			elif data == "B" or data == "b":
				data = 2
			elif data == "C" or data == "c":
				data = 3
			elif data == "D" or data == "d":
				data = 4
			elif data == "E" or data == "e":
				data = 5
			elif data == "S" or data == "s":
				data = 6

		else:#immediate data points to memory
			addressMode = 3
			if not re.match(r"^\s*[0]*[A-F0-9]{1,4}\s*$",data,re.IGNORECASE):
				print("invalid memory address")
				exit()

	elif (data[0] == "\'") or (data[0] == "\""): #data is character
		addressMode = 0
		data.strip()
		if len(data) != 3 :
			print("invalid character")
			exit()
		data = data[1:2]
		data = hex(ord(data))[2:]
	
	elif re.match("^(A|B|C|D|E|S|a|b|c|d|e|s)$",data) :#data is given in register
		addressMode = 1
		if data == "A" or data == "a":
			data = 1
		elif data == "B" or data== "b":
			data = 2
		elif data == "C" or data == "c":
			data = 3
		elif data == "D" or data == "d":
			data = 4
		elif data == "E" or data == "e":
			data = 5
		elif data == "S" or data == "s":
			data = 6
	else:#data is immediate
		addressMode = 0
		data = data.upper()
		if data in labels:
			data = labels[data]
		elif not re.match(r"^\s*[0]*[A-F0-9]{1,4}\s*$",data,re.IGNORECASE):
			print("invalid immediate data",data)
			exit()
	return data,addressMode

number_of_instr = 0#instruction count for labeling
labels = {} #holds the labels is upper case
labelkeys = labels.keys()
output = [] #stores the lines that will be written to ".bin" file
file1 = open(sys.argv[1], "r")
argument = sys.argv[1]
file2= open(argument[0:argument.index(".")] + ".bin", "w")
lines = []#read file lines into list
for line in file1:
	line = line.strip()
	if not bool(line):
		continue
	if ":" in line:
		if re.match(r"^\s*[A-Za-z0-9]+\s*:\s*$", line):
			string = line[0:line.index(":")] 
			string = string.strip().upper()
			if string in labelkeys:
				print("Error: multiple definition of label")
				exit()
			else:
				labels[string] = hex(3*number_of_instr)[2:]
		else:
			print("Error: invalid label syntax")
			exit()
	lines.append(line)
	if ":" not in line: #label lines is not counted as instruction line
		number_of_instr += 1


commands = {
	#dictionary of commands
	#to have easy access to the decimal codes of commands
	"HALT": 1, 
	"LOAD":2,
	"STORE":3,
	"ADD":4,
 	"SUB":5,
 	"INC":6, 
 	"DEC":7, 
 	"XOR":8, 
 	"AND":9, 
 	"OR": 10, 
 	"NOT": 11, 
 	"SHL": 12,
 	"SHR": 13,
 	"NOP": 14,
 	"PUSH": 15,
 	"POP": 16, 
 	"CMP": 17,
 	"JMP": 18, 
 	"JZ": 19,
 	"JE": 19,
 	"JNZ": 20,
 	"JNE":20,
 	"JC": 21,
 	"JNC": 22,
 	"JA": 23,
 	"JAE": 24,
 	"JB": 25,
 	"JBE": 26,
 	"READ" : 27,
 	"PRINT" : 28
}
addressMode = -1 
keys = commands.keys()

for text in lines:
	words = re.split(r"\s+", text,1) #first element of this list is operation or label, data is in other part
	proper_syntax = False
	if ":" not in text:
		for command in keys:
			#syntax check of instructions with operand
			if (command != "HALT" or command != "NOP") and re.match(r"^\s*" + command +r"\s*([A-Z0-9]+|\[\s*[0]*[A-FS0-9]{1,4}\s*\]|[\'\"].[\'\"])\s*$" ,text, re.IGNORECASE):
				proper_syntax = True
				break	
		if not(proper_syntax):
			#instructions with no operand or syntax error
			if (text.strip().upper() == "HALT"):
				#print("helllo halt")
				output.append("040000")
				continue
			if text.strip().upper() == "NOP":
				output.append("380000")
				continue
			print("Error: invalid syntax:",text)
			exit()
			break # how to handle exceptions ???

		#if we reach here, it is guaranteed that we have an operand due to regex check
		data = str(words[1])
		data, addressMode = take_data(data,addressMode)
		words[0] = words[0].upper()
		if addressMode == -1:
			print("Error: invalid address mode")
			exit()
		if words[0] in commands:
			output.append(convert(commands[words[0]],addressMode,data).lower())
		else:
			print("Error: not an operation")
			exit()
	else: #passes labels
		pass

for l in output:
	file2.write(l + "\n")
	
