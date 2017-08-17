#
# (c) 2017 TrueFlip S.A.R.L
# Prize counting algorithm (refactored)
# usage drawprizes.py [blockHash] [drawDd] [nextDrawId]
#  
#
# Get prices and valid combos from configuration file
# (also includes database config)


#Basic system tools
import json #Read JSON
import sys  #Read system input
import csv  #Read CSV files with less headaches
from decimal import * #Decimal operations library

#This loads the configuration file.
with open('config.json') as file:
	config = json.load(file)
combos = config['validCombos']

classes = {}

#This is input:
tickets = []
jackpot = Decimal(0)

#This is output:
payouts = []

#load tickets from CSV File (the file is always the drawid-IN/drawid-OUT - we provide sample files for you to play with)
def loadTicketsFromFile():
	global jackpot
	with open('tickets-'+currentDrawId+'.csv', 'r') as csvfile:
		array = csv.reader(csvfile, delimiter=',', quotechar='"')
		i = 0
		for element in array:
			if(i == 0): 
				jackpot = Decimal(element[0])
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
			intRep = divmod(int(hexRep,16),49)[1]
			if(intRep == 0): intRep = 49
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
		intRep = divmod(int(hexRep,16),26)[1]
		if(intRep == 0): intRep = 26
		else:
			output.append(intRep)
			success = True
			i = i + 1

	#Convert the whole thing to a sequence of strs (this is not really a bug but rather a representation issue)
	for element in output:
		stroutput.append(str(element))


	print("[INFO] The winning combination is: " + str(output))
	return stroutput

#This is run in parallel since the sets never interesect
def classifyTickets(combination,W,R):
	#['229519', '14', '25', '36', '44', '48', '25'] - example ticket
	whiteComboSet = set(combination[0:5])
	redComboSet   = {combination[5]}

	output = []
	for ticket in tickets:
		ticketWhiteSet = set(ticket[1:6])
		ticketRedSet   = {ticket[6]}
		countWhite = len(ticketWhiteSet.intersection(whiteComboSet))
		countRed  = len(ticketRedSet.intersection(redComboSet))
		if (countWhite == W and countRed == R):
			output.append(ticket)
			#print("[DEBUG]: " + str(ticket))
	
	print("[INFO] " + str(len(output)) +  " tickets are in class W=" + str(W) + "| R=" + str(R))
	return output

#Assign each ticket the amount to be paid and correct jackpot
def payWinners(winners,ratio,multiplier):
	global jackpot
	if(len(winners) == 0):
		return 0
	win = 0
	if ratio == 0:
		win = Decimal(config['ticketPrice']*multiplier)
	if ratio != 0:
		win = Decimal(ratio/len(winners)*float(jackpot))
	for winner in winners:
		jackpot = jackpot - win
		#print("[DEBUG] ID of winning ticket is: " + str(winner[0]))
		with open('results-'+currentDrawId+'.csv', 'a') as csvfile:
			writer = csv.writer(csvfile, delimiter=',',quotechar='"')
			writer.writerow([winner[0],win])
		
	if(Decimal(win * len(winners)) is None): return 0
	else: return Decimal(win * len(winners))


if __name__ == '__main__':
    seed = sys.argv[1]
    currentDrawId = sys.argv[2]
    nextDrawId = sys.argv[3]
    
    #Load the tickets from a CSV File
    loadTicketsFromFile()

    #Generate the combination
    combination = generateWinningSequence(seed)
    
    #Generate the winner lists
    nWinners = 0
    for combo in combos:
    	winners = classifyTickets(combination,combo['W'],combo['R'])
    	nWinners = nWinners + len(winners)
    	classes[combo['label']] = winners

    print("[INFO] The ratio of winners/total is " + str(float(nWinners)/float(len(tickets))*100) + "%")
    #The order matters because first come fixed, then come floating payments.
    i = 0
    while(i <= config['orders']):
    	for combo in combos:
    		payment = Decimal(0)
    		if(combo['order'] == i):
    			winners = classes[combo['label']]
    			payment = payWinners(winners,combo['ratio'],combo['multiplier'])
    			print("[INFO] Paid winners from group " + combo['label'] + " a total of " + str(payment))
    			print("[INFO] Stored winners from group " + combo['label'] + " to file!")
    			#Remove the class
    			del classes[combo['label']]
    	i = i + 1

    #Write header for the CSV 
    with open('results-'+currentDrawId+'.csv', 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(str(str(seed) + ",\"" + str(combination) + "\"," + str(jackpot)).rstrip('\r\n') + '\n' + content)

    print("[INFO] Script has completed work! Now exiting...")
    sys.exit(0)


