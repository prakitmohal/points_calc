import pandas
pandas.options.mode.chained_assignment = None # removes warning

# read in the CSVs
pointValues = pandas.read_csv('config/pointValues.csv',index_col=0)
multipliers = pandas.read_csv('config/multipliers.csv')
annualSpend = pandas.read_csv('config/annualSpend.csv')
fees = pandas.read_csv('config/fees.csv')

# extract point values
amex = pointValues.loc["amex","value"]
capone = pointValues.loc["capone","value"]
chase = pointValues.loc["chase","value"]
citi = pointValues.loc["citi","value"]
default = pointValues.loc["default","value"]
del(pointValues)

# if annual spend is 0 lets remove them now to save time
for x in range(len(annualSpend)):

	if annualSpend.yearly_spending[x] == 0:
		annualSpend.drop(x,inplace = True)

annualSpend.reset_index(drop=True,inplace=True)

csrFound = 0
cspFound = 0
csrNet = 0
cspNet = 0
chaseNet = 0
citiNet = 0
chaseDummy = ""
citiDummy = ""
fees['net'] = 0

# lets clean up our input dataframes to take into account anything that should be skipped
# first remove cards that the user wants to skip from the fees and multipliers list
# and calculate the net fee. then clean up the dataFrame
for x in range(len(fees)):

    if fees.analyze[x] == False:

        for y in range(len(multipliers)):
            if fees.card[x] == multipliers.card[y]:
                multipliers.drop(y,inplace = True)
        		
        # if they don't want it analyzed don't add it in later
        fees.drop(x,inplace = True)
        multipliers.reset_index(drop=True,inplace=True)
    
    else: # calculate the net 
        fees.net[x] = fees.benefits[x] - fees.fee[x]
        
        # let's see if this is a Chase or Citi annual fee card and store for later
        if fees.card[x] == "csr":
            csrFound = True
            csrNet = fees.net[x]    
        elif fees.card[x] == "csp":
            cspFound = True
            cspNet = fees.net[x]    
        elif fees.card[x] == "premier":
            citiNet = fees.net[x]
            citiDummy = "premier"    

fees.drop(columns=['fee','benefits','analyze'],inplace=True)

# This isn't great code BUT it saves a bunch of cycles later on
# Chase requires an annual fee card for points transfers
# determine which one it is
if (csrFound == True) and (cspFound == True):
    if (csrNet >= cspNet):
        chaseNet = csrNet
        chaseDummy = "csr"
    else:
        chaseNet = cspNet
        chaseDummy = "csp"
elif (csrFound == True):
    chaseNet = csrNet
    chaseDummy = "csr"
elif (cspFound == True):
    chaseNet = cspNet
    chaseDummy = "csp"

# if the category doesn't exist in multipliers anymore remove it from the annual spend
for x in range(len(annualSpend)):

	drop = 1

	for y in range(len(multipliers)):
		if annualSpend.category[x] == multipliers.category[y]:
			drop = 0
			break

	if (drop == True):
		annualSpend.drop(x,inplace = True)

annualSpend.reset_index(drop=True,inplace=True)

# we're taking the multipliers and multiplying each row by annualSpend to 
# get the number of points that are earned per card based on yearly spending
# we are also divvying up the multiplers table by category
# once this is done we're complete with annualSpend and multipliers
numOptions = 1
numCats = len(annualSpend)
bonusSplit = {}
maxIndex = {}
curIndex = {}
header = []
category = ""

print ("Analyzing Categories:",numCats)

for x in range(numCats):

    # split into groups by category
    category = annualSpend.category[x]
    bonusSplit[x] = multipliers.groupby(multipliers.category).get_group(category)
  
    # add the defaults, but obviously don't add it to the default column
    # skip the freedom column you'd need some odd values to beat 5% on a free card
    # see if the card is in the list first before adding
    # this is applicable for everyday and cfu in certain categories
    if (category != "default" and category != "freedom"):
        
        if "double" in fees.values:
            bonusSplit[x].loc[len(bonusSplit[x].index)] = [category,'double',2] 
        if "venturex" in fees.values:
            bonusSplit[x].loc[len(bonusSplit[x].index)] = [category,'venturex',2] 
        
        if ("cfu" not in bonusSplit[x].values and "cfu" in fees.values):
            bonusSplit[x].loc[len(bonusSplit[x].index)] = [category,'cfu',1.5] 
        
        # don't add the amex cards to the no amex category lol
        if (category != "rest-noamex" or category != "groc-noamex"):
            if ("pref" not in bonusSplit[x].values and "pref" in fees.values):
                bonusSplit[x].loc[len(bonusSplit[x].index)] = [category,'pref',1.5]
            if ("everyday" not in bonusSplit[x].values and "everyday" in fees.values):
                bonusSplit[x].loc[len(bonusSplit[x].index)] = [category,'everyday',1.2]
   
    # convert the yearly spending into points
    bonusSplit[x]["points"] = 0
    bonusSplit[x].points = bonusSplit[x]["mult"] * annualSpend.yearly_spending[x]
   
    del bonusSplit[x]["mult"]

    # reset the index
    bonusSplit[x].reset_index(inplace = True, drop = True)

    # create the column name and start counting rows
    header.append(bonusSplit[x].category[0])
    
    curIndex[x] = 0
    maxIndex[x] = len(bonusSplit[x])
    numOptions = numOptions * maxIndex[x]

del(annualSpend)
del(multipliers)

# reset the index in fees
fees.set_index('card',inplace=True)

# create header for dictionary
if (chaseDummy != ""):
    header.append("dummyChase")
if (citiDummy != ""):
    header.append("dummyCiti")

header.extend(("amexPts","caponePts","chasePts","citiPts","netFees","profit"))

options = []

print ("Table Initialized with rows:",numOptions)
numCards = len(fees)

# Populate Table
for x in range(numOptions):
    
    rowList = []
    cardLookup = []
    pointList = []
    amexPts = 0
    caponePts = 0
    chasePts = 0
    citiPts = 0
    netFees = 0
    profit = 0
    tempChase = ""
    tempCiti = ""
    chaseFee = False
    citiFee = False

    # Build up the line
    for y in range(numCats):
        
        rowList.append( bonusSplit[y].card[curIndex[y]] )
        pointList.append( bonusSplit[y].points[curIndex[y]] )

    # remove duplicates so we only add fees once
    cardLookup = list(set(rowList))
            
    # match them up with the card list 
    for y in range(len(cardLookup)):

        netFees = netFees + fees.loc[cardLookup[y],"net"]

        # chase and citi require certain cards to get the full value
        # set the flags where appropriate
        if (cardLookup[y] == "csp") or (cardLookup[y] == "csr"):
            chaseFee = True
        elif (cardLookup[y] == "premier"):
            citiFee = True

    # now we can go through the row and calculate the points
    for y in range(numCats):

        # Look up the issuer
        issuer= fees.loc[rowList[y],"issuer"]
      
        # calculate points and add to profit
        if (issuer == "amex"):
            amexPts = amexPts + pointList[y]
        elif (issuer == "capone"):
            caponePts = caponePts + pointList[y]
        elif (issuer == "chase"):
            chasePts = chasePts + pointList[y]
        elif (issuer == "citi"):
            citiPts = citiPts + pointList[y]
                
    profit = netFees + (amexPts * amex) + (caponePts * capone)

    # this is where the magic happens from before
    # If there are points but there's no annual fee card run the math
    # and see if a dummy makes sense 
    if (chaseFee == True):
        profit = chasePts * chase + profit
    elif (chaseDummy != ""):
        if (chasePts * default > chasePts * chase + chaseNet):
            profit = chasePts * default + profit
        else:
            netFees = netFees + chaseNet
            profit = chasePts * chase + profit + chaseNet
            tempChase = chaseDummy

    if (citiFee == True):
        profit = citiPts * citi + profit
        tempCiti = ""
    elif (citiDummy != ""):
        if (citiPts * default > citiPts * citi + citiNet):
            profit = citiPts * default + profit
        else:
            netFees = netFees + citiNet            
            profit = citiPts * citi + profit + citiNet
            tempCiti = citiDummy
 
    # add the row to the table
    if (chaseDummy != ""):
        rowList.append(tempChase)
    if (citiDummy != ""):
        rowList.append(tempCiti)
    
    rowList.extend((amexPts,caponePts,chasePts,citiPts,netFees,profit))
    options.append(rowList)

    # update indexes, check for overflow and adjust accordingly
    curIndex[0] = curIndex[0] + 1

    for y in range(numCats-1):
            
        if curIndex[y] == maxIndex[y]:

            curIndex[y] = 0
            curIndex[y+1] = curIndex[y+1] + 1
    
    if(x % 10000 == 0):
        print ("Row", x, "analyzed out of", numOptions, "- percent complete:", \
                "{:.2%}".format(float(x)/numOptions))    

# Display the top 50 options and make it look pretty
print ("Analyzing results, please be patient, may take around a minute")

optionsFrame = pandas.DataFrame.from_dict(options)
optionsFrame.columns = header
optionsFrame = optionsFrame.nlargest(50,"profit")

optionsFrame['amexPts'] = optionsFrame['amexPts'].map("{:,.0f}".format)
optionsFrame['caponePts'] = optionsFrame['caponePts'].map("{:,.0f}".format)
optionsFrame['chasePts'] = optionsFrame['chasePts'].map("{:,.0f}".format)
optionsFrame['citiPts'] = optionsFrame['citiPts'].map("{:,.0f}".format)

optionsFrame['netFees'] = optionsFrame['netFees'].map("${:,.2f}".format)
optionsFrame['profit'] = optionsFrame['profit'].map("${:,.2f}".format)

print ("\n")
print (optionsFrame.to_string(index=False))
optionsFrame.to_csv("output.csv",index=None)
