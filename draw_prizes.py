#
# (c) 2017 TrueFlip S.A.R.L
# Prize counting algorithm (refactored)
# usage drawprizes.py [blockHash] [drawDd] [nextDrawId]
# python draw_prizes.py 000000000000000000304fb7d35a034a39acdf3ab54e69cee3ee06caefa0a0c1  487700 487701
#  
#
# Get prices and valid combos from configuration file
# (also includes database config)
# IMPORTANT NOTE: IF TWO CLASSES WIN THE JACKPOT SUCH A SITUATION IS PROCESSED MANUALLY. SINCE THE ODDS OF SUCH AN EVENT ARE EXTREMELY LOW WE DO NOT HANDLE IT PROGRAMATICALLY

#Basic system tools
import json #Read JSON
import sys  #Read system input
import csv  #Read CSV files with less headaches
from decimal import * #Decimal operations library
import os

#This loads the configuration file.
with open('config.json') as file:
	config = json.load(file)
combos = config['validCombos']

classes = {}

#This is input:
tickets = []
jackpot = Decimal(0)

special_winners = []
#This is output:
payouts = []

#load tickets from CSV File (the file is always the drawid-IN/drawid-OUT - we provide sample files for you to play with)
def loadTicketsFromFile(n):
	global jackpot
	global tickets
	global payouts
	tickets = []
	payouts = []
	with open('tickets-'+currentDrawId+'-' + str(n) + '.csv', 'r') as csvfile:
		array = csv.reader(csvfile, delimiter=',', quotechar='"')
		i = 0
		ln = 0
		for element in array:
			if(i == 0 and n == 0):
				jackpot = Decimal(element[0])
				i = 1
			elif(i == 0 and n != 0):
				#Load jackpot from previous file.
				file = open('results-'+currentDrawId+'-' + str(n - 1) + '.csv', 'r') 
				arr = csv.reader(file,delimiter=',', quotechar='"')
				for x in arr:
					if ln == 0:
						jackpot = Decimal(x[2])
						ln = 1
				file.close()
				i = 1
			else:
				tickets.append(element)
				#print("[DEBUG] " + str(element))

	print("[INFO] Jackpot is: " + str(jackpot))
   
#Generate the winning numbers
def generateWinningSequence(seed):
	output = []
	stroutput = []
	size = len(seed)
	block_size = config['blockSize']
	whiteSamples = config['Wsize']
	redSamples = config['Rsize']
	
	#Cycle A: Pick white balls
	i = 1
	while(len(output) < whiteSamples):
		success = False
		while(not success):
			hexRep = seed[size - block_size*i:size - block_size*(i-1)]
			intRep = divmod(int(hexRep,16),20)[1]
			if(intRep == 0): intRep = 20
			if(intRep in set(output)):
				success = False
				i = i + 1
			if(intRep not in set(output)):
				output.append(intRep)
				success = True
				i = i + 1

	#Cycle B: Pick a red ball
	success = False

	while(not success):
		hexRep = seed[size - block_size*i:size - block_size*(i-1)]
		intRep = divmod(int(hexRep,16),4)[1]
		if(intRep == 0): intRep = 4
		output.append(intRep)
		success = True
		i = i + 1

	#Convert the whole thing to a sequence of strs (this is not really a bug but rather a representation issue)
	for element in output:
		stroutput.append(str(element))


	print("[INFO] The winning combination is: " + str(output))
	return stroutput

#This is run in parallel since the sets never interesect
#Fix this at some point - i.e. figure out what the actual ticket size is;
def classifyTickets(combination,W,R):
	#['229519', '14', '25', '36', '44', '48', '25'] - example ticket
	whiteComboSet = set(combination[0:config['Wsize']])
	redComboSet   = {combination[config['Wsize']]}

	output = []
	for ticket in tickets:
		ticketWhiteSet = set(ticket[1:9])
		ticketRedSet   = set(ticket[9:13])
		countWhite = len(ticketWhiteSet.intersection(whiteComboSet))
		countRed  = len(ticketRedSet.intersection(redComboSet))
		if (countWhite == W and countRed == R):
			output.append(ticket)
			#print("[DEBUG]: " + str(ticket))

	print("[INFO] " + str(len(output)) +  " tickets are in class W=" + str(W) + "| R=" + str(R))
	return output

#Assign each ticket the amount to be paid and correct jackpot
#This needs to be fixed to fix the problem of multpliers.
def payWinners(i,winners,ratio):
	global jackpot
	if(len(winners) == 0):
		return 0
	win = 0
	val = combo['E' + str(i)]
	if ratio == 0 and val > 0:
		win = Decimal(val)
	if val < 0:
		print("Warn - nothing to do here")
		return 0
	if ratio != 0:
		win = Decimal(ratio/len(winners)*float(jackpot))
	for winner in winners:
		if ratio == 0:
			jackpot = jackpot - win*int(winner[13])
		else:
			jackpot = jackpot - win
		#print("[DEBUG] ID of winning ticket is: " + str(winner[0]))
		file = open('results-'+currentDrawId+ '-' + str(i) + '.csv', 'a')
		with file as csvfile:
			writer = csv.writer(csvfile, delimiter=',',quotechar='"')
			if ratio == 0:
				writer.writerow([winner[0],win*int(winner[13])])
			else:
				writer.writerow([winner[0],win])
		file.close()
	if(Decimal(win * len(winners)) is None): return 0
	else: return Decimal(win * len(winners))


if __name__ == '__main__':
    seed = sys.argv[1]
    currentDrawId = sys.argv[2]
    nextDrawId = sys.argv[3]
    
    #We iterate over different cases of e2,e3,e4
    for x in range(0,4):
    	#Load the tickets from a CSV File
    	loadTicketsFromFile(x)
    	combination = generateWinningSequence(seed)

    	if(len(tickets) == 0):
    		print("No tickets were part of class " + str(x) + " in this draw...")
    		f = open('results-'+str(currentDrawId)+"-"+str(x)+'.csv', 'w')
    		f.write(str(str(seed) + ",\"" + str(combination) + "\"," + str(jackpot)).rstrip('\r\n') + '\n')
    		f.close()
		continue

    	#Generate the combination

    	#Generate the winner lists
    	nWinners = 0
    	for combo in combos:
    		winners = classifyTickets(combination,combo['W'],combo['R'])
    		nWinners = nWinners + len(winners)
    		classes[combo['label']] = winners
    	try:
    		print("[INFO] The ratio of winners/total is " + str(float(nWinners)/float(len(tickets))*100) + "%")
    	except:
    		print("[INFO] The ratio of winners/total is 0 because no one bought tickets!")
    	#The order matters because first come fixed, then come floating payments.
    	i = 0
    	while(i <= config['orders']):
    		for combo in combos:
    			payment = Decimal(0)
    			if(combo['order'] == i):
    				winners = classes[combo['label']]
    				payment = payWinners(x,winners,combo['ratio'])
    				print("[INFO] Paid winners from group " + combo['label'] + " a total of " + str(payment))
    				print("[INFO] Stored winners from group " + combo['label'] + " to file!")
    				#Remove the class
    				del classes[combo['label']]
    		i = i + 1
	
    	#Write header for the CSV 
    	try:
    		f = open('results-'+str(currentDrawId)+"-"+str(x)+'.csv', 'r+')
    		content = f.read()
    		f.seek(0,0)
    		f.write(str(str(seed) + ",\"" + str(combination) + "\"," + str(jackpot)).rstrip('\r\n') + '\n' + content)
    		f.close()
    	except Exception as ex:
    		print(ex)
    		with open('results-'+str(currentDrawId)+"-"+str(x)+'.csv', 'a') as f:
    			f.write(str(str(seed) + ",\"" + str(combination) + "\"," + str(jackpot)).rstrip('\r\n'))
    			print("[DEBUG] Could not write header")
	
    print("[INFO] Script has completed work! Now exiting...")
    sys.exit(0)


