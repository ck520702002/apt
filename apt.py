import pdb
import itertools
import copy
import operator
from multiprocessing import Pool
#file opening
#filename = raw_input("Enter the inputfile name: ")
f = open('inputfile2.txt')

#data cleaning
a = [x for x in f.readlines() if x != '\r\n']
a = [w.replace(' | ', ',') for w in a]
a = [w.replace("\r\n", '') for w in a]

#data splitting 
peopleList = []
offersList = []
relationshipsList = []

for x in range(1 , a.index('offers')):
	peopleList.append(a[x])

for x in range(a.index('offers')+1 , a.index('relationships')):
	offersList.append(a[x])

for x in range(a.index('relationships')+1 , len(a)):
	relationshipsList.append(a[x])

#put data into lists of dictionaries
people = []
offers = []
relationships = []

for person in peopleList:
	temp = {}
	tempList = person.split(',')
	temp['name'] = tempList[0]
	temp['type'] = tempList[1]
	people.append(temp)

for offer in offersList:
	temp = {}
	tempList = offer.split(',')
	temp['name'] = tempList[0]
	temp['company'] = tempList[1]
	temp['type'] = tempList[2]
	temp['location'] = tempList[3]
	temp['utility'] = 0
	offers.append(temp)

for relationship in relationshipsList:
	temp = {}
	tempList = relationship.split(',')
	temp['p1'] = tempList[0]
	temp['p2'] = tempList[1]
	temp['relationship'] = tempList[2]
	relationships.append(temp)

#data mockup, for people, offers, relationships, they should be like these:
#
#people = [{'name':'Amy','type':'Academic'},
#          {'name':'Bob','type':'Entrepreneur'},
#          {'name':'Charlie','type':'Money Grubber'}]
#
#offers = [{'name':'Amy','company':'MacroHard','type':'Big Software Firm','location':'Seattle','utility':0},
#		  {'name':'Amy','company':'Stanguard College','type':'Grad School','location':'San Francisco','utility':0},
#		  {'name':'Amy','company':'Dartboard Modeling','type':'Hedge Fund','location':'NYC','utility':0},
#		  {'name':'Bob','company':'Bigup-Side','type':'Startup','location':'NYC','utility':0},
#		  {'name':'Bob','company':'Questionable Tactics','type':'Hedge Fund','location':'San Francisco','utility':0},
#		  {'name':'Charlie','company':'Cash-Money Inc.','type':'Investment Bank','location':'NYC','utility':0},
#		  {'name':'Charlie','company':'Arbitrack','type':'Hedge Fund','location':'San Francisco','utility':0}]
#
#relationships = [{'p1':'Bob','p2':'Amy','relationship':'Dating'},
#				 {'p1':'Bob','p2':'Charlie','relationship':'Mortal Enemies'}]
#end of data processing


#initialize given constraints
benefits = [{'type':'Big Software Firm','pay':6,'hours':6,'impact':2,'learn':8},
			{'type':'Hedge Fund','pay':8,'hours':8,'impact':4,'learn':6},
			{'type':'Investment Bank','pay':10,'hours':10,'impact':3,'learn':4},
			{'type':'Startup','pay':4,'hours':8,'impact':10,'learn':8},
			{'type':'Grad School','pay':1,'hours':4,'impact':3,'learn':10}]


personalities = [{'type':'Money Grubber','pay':10,'hours':-1,'impact':4,'learn':2},
				 {'type':'Entrepreneur','pay':4,'hours':-2,'impact':10,'learn':8},
				 {'type':'Slacker','pay':1,'hours':-10,'impact':2,'learn':2},
				 {'type':'Academic','pay':2,'hours':-6,'impact':8,'learn':10}]


#this is a function that calculates the bonus between 2 given people
def relationshipBonus (name1, name2):
	for relationship in relationships:
		if (name1 == relationship['p1'] and name2 == relationship['p2']) or (name2 == relationship['p1'] and name1 == relationship['p2']):
			if relationship['relationship'] == 'Dating':
				return 50
			elif relationship['relationship'] == 'Friends':
				return 20
	return 0

#caculate the utility for each offer in the offers list without considering the geography
for person in people:
	for personality in personalities:
		if personality['type'] == person['type']:
			for offer in offers:
				if offer['name'] == person['name']:
					for benefit in benefits:
						if benefit['type'] == offer['type']:
							offer['utility'] = benefit['pay']*personality['pay']+benefit['hours']*personality['hours']+benefit['impact']*personality['impact']+benefit['learn']*personality['learn']

#put the offers into personalOffer -> Amy's offers[{..},{..}]
#make a list of personalOffers -> [ [{..},{..}], [{..},{..}] .. ] 
personalOffers = []
for person in people:
	personalOffers.append([offer for offer in offers if offer['name'] == person['name']])


#initialize the name lists:
#for marriedNameList, it contains the names that are married
#for mortalNameList, it contains the names that are mortal enemies but not in the marriedNameList
#i do so since the people in the marriedNameList have to be at the same location, 
#which would reduce the number of combinations that needs to be considered
marriedNameList =[]
mortalNameList = []
for relationship in relationships:
	if relationship['relationship'] == 'Married' and relationship['p1'] not in marriedNameList:
			marriedNameList.append(relationship['p1'])
			marriedNameList.append(relationship['p2'])
for relationship in relationships:
	if relationship['relationship'] == 'Mortal Enemies' and relationship['p1'] not in mortalNameList and relationship['p1'] not in marriedNameList and relationship['p2'] not in marriedNameList:
			mortalNameList.append(relationship['p1'])
			mortalNameList.append(relationship['p2'])

enemyOffers = []
marriedOffers =[]
for relationship in relationships:
	if relationship['relationship'] == 'Married':
		marriedOffer = [personalOffer for personalOffer in personalOffers if personalOffer[0]['name'] == relationship['p1']  or personalOffer[0]['name'] == relationship['p2']]
		marriedOffers.append(marriedOffer)
		
	elif relationship['relationship'] == 'Mortal Enemies':	
		if relationship['p1'] not in marriedNameList and relationship['p2'] not in marriedNameList:
			enemyOffer = [personalOffer for personalOffer in personalOffers if personalOffer[0]['name'] == relationship['p1']  or personalOffer[0]['name'] == relationship['p2']]
			enemyOffers.append(enemyOffer)

#for every married couple, generates all the combinations and then delete the ones that they are not in the same city
#put the possible combinations into lists
possibleMarriedCombinationSet =[]
for marriedOffer in marriedOffers:
	marriedCombinations = map(list,itertools.product( *marriedOffer))
	possibleCombinations =[combination for combination in marriedCombinations if combination[0]['location'] == combination[1]['location']]
	possibleMarriedCombinationSet.append(possibleCombinations)

possibleEnemyCombinationSet=[]
for enemyOffer in enemyOffers:
	enemyCombinations = map(list,itertools.product( *enemyOffer))
	possibleCombinations =[combination for combination in enemyCombinations if combination[0]['location'] != combination[1]['location']]
	possibleEnemyCombinationSet.append(possibleCombinations)

#generates the possible combinations for people who are not married and people whose mortal enemy is a married person

normalCombinations=[]
normalOffers = [personalOffer for personalOffer in personalOffers if personalOffer[0]['name'] not in marriedNameList and personalOffer[0]['name'] not in mortalNameList ]

pool = Pool(1500)
for result in pool.imap(list, itertools.product(*normalOffers	)):
    normalCombinations.append(result)
    print len(normalCombinations)

#normalCombinations = map(list,itertools.product( *normalOffers))

#generates the possible combinations of the possible combinations for the married people and the normal people
#put the result into resultCombinations
resultCombinations = normalCombinations
for possibleMarriedCombination in possibleMarriedCombinationSet:
	templist= [possibleMarriedCombination, resultCombinations]
	resultCombinations = map(list,itertools.product( *templist))

#generates the possible combinations of the possible combinations for the mortal enemies and the resultCombinations
for possibleEnemyCombination in possibleEnemyCombinationSet:
	templist= [possibleEnemyCombination, resultCombinations]
	resultCombinations = map(list,itertools.product( *templist))

#normalize the list combinations into: [ [offer1,offer2..] , [offer3,offer4.] .. ]
combinations = []
for resultCombination in resultCombinations:
	combination =[]
	for offerSet in resultCombination:
		for offer in offerSet:
			combination.append(offer)
	combinations.append(combination)

#check if there are people that are mortal enemies to the married people
#eliminates the impossible combinations
finalCombinations=[]
for combination in combinations:
	for offer in combination:
		for otherOffer in combination:
			for relationship in relationships:
				if relationship['relationship'] == 'Mortal Enemies' and relationship['p1'] ==offer['name'] and relationship['p2'] == otherOffer['name']:
					if offer['location']!=otherOffer['location']:
						finalCombinations.append(combination)




	

#combinations=[]
#combinations = map(list,itertools.product( *personalOffers))
#pool = Pool(500)
#count=0
#for result in pool.imap(list, itertools.product(*personalOffers	)):
#    combinations.append(result)
#    print len(combinations)



#for each combination, calculate the utility for each offer considering the geography
results = []
for combination in finalCombinations:
	assignments = []
	total = 0
	for offer in combination:
		temp = {}
		bonus = 0
		for otherOffer in combination:
			if otherOffer['name'] != offer['name']:
				if otherOffer['location'] == offer['location']:
					bonus = relationshipBonus(otherOffer['name'],offer['name']) +bonus
		temp = {'name':offer['name'],'company':offer['company'],'utility':offer['utility']+bonus}
		assignments.append(temp)
		total =total +temp['utility']
	results.append({'assignments':assignments,'totalUtility':total})

#sort the results list by the total utility
results.sort(key=operator.itemgetter('totalUtility'))
optimal = results.pop()

print ("the optimal assignments are:")
for offer in optimal['assignments']:
	print (offer['name'] + ' --> ' + offer['company'])


