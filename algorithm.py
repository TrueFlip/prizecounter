#This is the prize draw logic

import datetime
from decimal import *
import csv

debug = False

#Sequence of available numbers for choice:
#Open csv file

rows = []
draw_results = []
tickets = []
drawdate = ''
piggybank_current_fund = 0
jackpot = 0

def StepA():
    global rows
    global draw_results
    global tickets
    global drawid
    global piggybank_current_fund
    global jackpot

    with open('results.csv', 'r') as csvfile:
        data = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in data:
            rows.append(row)

    drawid = rows[0][0]
    piggybank_current_fund = Decimal(rows[0][1])
    jackpot = Decimal(rows[0][2])

    if debug == True:
        print(drawid)
        print(piggybank_current_fund)
        print(jackpot)

    for i in range(1,len(rows)):
        tickets.append(tuple(rows[i]))

    print(tickets)

#Jackpot Winners

def getWinners(tickets,Wset,Rset,WsetNum,RsetNum):

    winners = []
    winners_tickets = []

    for ticket in tickets:
        whiteset = [int(ticket[1]), int(ticket[2]), int(ticket[3]), int(ticket[4]), int(ticket[5])]
        redset = [int(ticket[6])]

        if (len(set(whiteset).intersection(set(Wset))) == WsetNum and len(set(redset).intersection(set(Rset))) == RsetNum):
            winners_tickets.append(ticket)
            w = (ticket[0])
            winners.append(w)

    remaining_tickets = set(tickets) - set(winners_tickets)

    return [winners,remaining_tickets]

def makePayment(winners,value,type):

    global piggybank_current_fund
    global jackpot
    global draw_results

    myothercontext = Context(prec=10, rounding=ROUND_HALF_DOWN)
    setcontext(myothercontext)

    if len(winners) == 0:
        return [1, 0]

    #winners = (winners,)
    paid = 0

    if type == 'fixed':
        total_amount = value * Decimal(len(winners))
        if  piggybank_current_fund <= 0:
            print('Current fund is 0! We cannot make any payments')
            return [11,0]
        if piggybank_current_fund - Decimal(total_amount) < 0:
            print('We don not have enough cash to cover everyone!')
            return[11,0]

        amount_per_winner = round(value,8)

    if type == 'percent':
        value = round(value,3)
        total_amount = Decimal(value)*piggybank_current_fund
        amount_per_winner = total_amount/len(winners)
        paid = Decimal(total_amount)
        if  piggybank_current_fund <= 0:
            print('Current fund is 0! We cannot make any payments')
            return [11, 0]
        if piggybank_current_fund - Decimal(total_amount) < 0:
            print('We do not have enough cash to cover everyone!')
            return [11, 0]


    if type == 'jackpot':
        if  jackpot <= 0:
            print('Current fund is 0! We cannot make any payments')
            return [11, 0]
        amount_per_winner = Decimal(jackpot)/Decimal(len(winners))

    state = 11

    a = Decimal(piggybank_current_fund)

    if type == 'fixed':
        for winner in winners:
            try:
                piggybank_current_fund = Decimal(piggybank_current_fund) - Decimal(amount_per_winner)
                draw_results.append([winner,amount_per_winner])
                state = 1
            except:
                print(piggybank_current_fund)
    if type == 'percent':
        for winner in winners:
            try:
                draw_results.append([winner, amount_per_winner])
                state = 1
            except:
                state = 11
    if type == 'jackpot':
        for winner in winners:
            try:
                piggybank_current_fund = Decimal(piggybank_current_fund) - Decimal(amount_per_winner)
                draw_results.append([winner, amount_per_winner])
                state = 1
            except:
                state = 11

    return [state,paid]

def getRandomSeed(seed):

    print(seed)
    out = []

    end_size = len(seed)
    block_size = 3
    samplesize = 6
    j = 1
    k = 1

    while len(out) < samplesize-1:
        valid = False
        while (not valid):
            nhex = seed[end_size-block_size*j:end_size-block_size*(j-1)]
            nint = divmod(int(nhex,16),49)[1]
            if nint in out:
                valid = False
                j = j + 1
                continue
            if nint == 0:
                valid = False
                j = j + 1
                continue
            else:
                valid = True
                out.append(nint)
                j = j + 1
                continue
           

    print(j)

    valid=False

    while(not valid):
        valid == False
        nhex = seed[end_size - block_size * j:end_size - block_size * (j - 1)]
        nint = divmod(int(nhex,16), 29)[1]
        if nint == 0:
            valid = False
        else:
            valid = True
            out.append(nint)

    print(out)
    return out

#Main program which returns the winning numbers (5 Whites and 1 Red)

#x = getRandomSeed(drawdate)
#hash = x[0]
#whiteballs = random.sample(sequence,5)
#sequence = set(sequence) - set(whiteballs)
#redball = random.sample(sequence,1)

#print(sorted(whiteballs))
#print(redball)

#FOR TEST ONLY!!!!
def StepB(seed,drawid):

    global rows
    global draw_results
    global tickets
    global drawdate
    global piggybank_current_fund
    global jackpot

    balls = getRandomSeed(seed)

    print(balls)

    whiteballs = balls[0:5]
    redball = balls[5:6]

    #For test only.

    #print(sorted(whiteballs))
    #print(redball)
    #Now we have to run the logic which works as follows


    strwin = str(whiteballs[0]) +'-' + str(whiteballs[1]) + '-' + str(whiteballs[2]) + '-' + str(whiteballs[3]) + '-' + str(whiteballs[4]) + '-R-' + str(redball[0])

    basePrice = 0.001

    draw_results = []

    #Jackpot winners.
    jkwinners,    tickets   = getWinners(tickets, whiteballs, redball, 5, 1)
    winners003jk, tickets = getWinners(tickets, whiteballs, redball, 5, 0)
    winners001jk, tickets = getWinners(tickets, whiteballs, redball, 4, 1)

    #Fixed winners

    winners25, tickets = getWinners(tickets, whiteballs, redball, 4, 0)
    winners20, tickets = getWinners(tickets, whiteballs, redball, 3, 1)
    winners08, tickets = getWinners(tickets, whiteballs, redball, 3, 0)
    winners10, tickets = getWinners(tickets, whiteballs, redball, 2, 1)
    winners05, tickets = getWinners(tickets, whiteballs, redball, 1, 1)
    winners03, tickets = getWinners(tickets, whiteballs, redball, 2, 0)
    winners01, tickets = getWinners(tickets, whiteballs, redball, 1, 0)

    print(piggybank_current_fund)
    print("-0-----0---")

    #Make all the payments.
    state = makePayment(winners01,Decimal(basePrice*1),"fixed")[0]
    if state != 1:
        print("Something went 0.001 payment")
        exit()
    state = makePayment(winners03,Decimal(basePrice*3),'fixed')[0]
    if state != 1:
        print("Something went 0.003 payment")
        exit()
    state = makePayment(winners05,Decimal(basePrice*5),'fixed')[0]
    if state != 1:
        print("Something went 0.005 payment")
        exit()
    state = makePayment(winners10,Decimal(basePrice*10),'fixed')[0]
    if state != 1:
        print("Something went 0.010 payment")
        exit()
    state = makePayment(winners08,Decimal(basePrice*8),'fixed')[0]
    if state != 1:
        print("Something went 0.08 payment")
        exit()
    state = makePayment(winners20,Decimal(basePrice*20),'fixed')[0]
    if state != 1:
        print("Something went 0.02 payment")
        exit()
    state = makePayment(winners25,Decimal(basePrice*25),'fixed')[0]
    if state != 1:
        print("Something went 0.025 payment")
        exit()

    #Here we have to make a lock because the value should not decrease;

    paid = Decimal(0.00000000)

    x = makePayment(winners001jk,round(0.01,3),'percent')
    if x[0] != 1:
        print("Something went wrong")
        exit()
    paid = paid + Decimal(x[1])

    x = makePayment(winners003jk,round(0.03,3),'percent')
    if x[0] != 1:
        print("Something went wrong")
        exit()
    paid = paid + Decimal(x[1])

    x = makePayment(jkwinners,1,'jackpot')
    if x[0] != 1:
        print("Something went wrong")
        exit()
    #Final steps:
    piggybank_current_fund = piggybank_current_fund - paid


    if debug == True:
        print(draw_results)

        total = Decimal(0)

        for result in draw_results:
            total = total + result[2]
        print(total)

    print(draw_results)
    #Move cash left-over to jackpot

    jackpot = jackpot + piggybank_current_fund
    piggybank_current_fund = Decimal(0)

    #Write the results to a CSV File

    with open('out.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"')
        writer.writerow([drawid,piggybank_current_fund,jackpot]) #New date, piggy bank and jackpot
        writer.writerow([strwin])
        writer.writerow([seed])
        for result in draw_results:
            writer.writerow(result)

    print("Done")

    #Say goodbye