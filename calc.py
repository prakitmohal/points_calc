import pandas
pandas.options.mode.chained_assignment = None # removes warning

debug = True

# read in the CSVs
fees = pandas.read_csv('fees.csv',index_col=0)
pointValues = pandas.read_csv('pointValues.csv',index_col=0)
annualSpend = pandas.read_csv('annualSpend.csv')
multipliers = pandas.read_csv('multipliers.csv')

# extract point values
amex = pointValues.loc["amex","value"]
chase = pointValues.loc["chase","value"]
citi = pointValues.loc["citi","value"]
default = pointValues.loc["default","value"]

# add dummyChase/dummyCiti cards to tables manually to simplify files
newRow = {'category':'dummyChase','yearly_spending':0}
annualSpend = annualSpend.append(newRow, ignore_index=True)
newRow = {'category':'dummyCiti','yearly_spending':0}
annualSpend = annualSpend.append(newRow, ignore_index=True)
annualSpend.sort_values(by=['category'],inplace=True)
annualSpend.reset_index(drop=True,inplace=True)

newRow = {'category':'dummyChase','card':'cfu','mult':0}
multipliers = multipliers.append(newRow, ignore_index=True)
newRow = {'category':'dummyChase','card':'csp','mult':0}
multipliers = multipliers.append(newRow, ignore_index=True)
newRow = {'category':'dummyCiti','card':'double','mult':0}
multipliers = multipliers.append(newRow, ignore_index=True)
newRow = {'category':'dummyCiti','card':'premier','mult':0}
multipliers = multipliers.append(newRow, ignore_index=True)
multipliers.sort_values(by=['category'],inplace=True)
multipliers.reset_index(drop=True,inplace=True)

# category counts
numOptions = 1
numCats = len(annualSpend)
bonusSplit = {}
maxIndex = {}
curIndex = {}
header = []

print ("Analyzing Categories:",numCats)

for x in range(numCats):

    # split into groups by category
    bonusSplit[x] = multipliers.groupby(multipliers.category).get_group(annualSpend.category[x])
    
    # convert the yearly spending into points
    bonusSplit[x]["points"] = 0
    bonusSplit[x].points = bonusSplit[x]["mult"] * annualSpend.yearly_spending[x]
   
    if debug:
        print ("[DB]Category:", bonusSplit[x].category.iloc[0], \
        "Spend:", annualSpend.yearly_spending[x], \
        "Mult:", bonusSplit[x].mult.iloc[0], \
        "Points:", bonusSplit[x].points.iloc[0])
    
    del bonusSplit[x]["mult"]

    # reset the index
    bonusSplit[x].reset_index(inplace = True, drop = True)

    # create the column name and start counting rows
    header.append(bonusSplit[x].category[0])
    
    curIndex[x] = 0
    maxIndex[x] = len(bonusSplit[x])
    numOptions = numOptions * maxIndex[x]

# create header for dictionary
header.extend(("amexPts","chasePts","citiPts","fee","credits","profit"))
options = []

print ("Table Initialized with rows:",numOptions)
numCards = len(fees)

# Populate Table
for x in range(numOptions):
    
    rowList = []
    cardLookup = []
    pointList = []
    amexPts = 0
    chasePts = 0
    citiPts = 0
    fee = 0
    credits = 0
    profit = 0
    dummyChase = False
    dummyCiti = False
    chaseTx = False
    citiTx = False

    # Build up the line
    for y in range(numCats):
        
        rowList.append( bonusSplit[y].card[curIndex[y]] )
        pointList.append( bonusSplit[y].points[curIndex[y]] )

        # note that an annual fee card is in the dummy slot for chase or citi
        if (bonusSplit[y].category.iloc[0] == "dummyChase") and (bonusSplit[y].card[curIndex[y]] == "csp"):
            dummyChase = True
        elif (bonusSplit[y].category.iloc[0] == "dummyCiti") and (bonusSplit[y].card[curIndex[y]] == "premier"):
            dummyCiti = True

    # If the dummy card is a CSP/Premier AND it appears in the list for spend, 
    # we're going to get a duplicate entry. don't process it
    if not ((dummyChase == True and rowList.count("csp") > 1) or \
            (dummyCiti == True and rowList.count("premier") > 1)):

        # remove duplicates so we only add fees once
        cardLookup = list(set(rowList))
            
        # match them up with the card list 
        for y in range(len(cardLookup)):

            fee = fee - fees.loc[cardLookup[y],"fee"]
            credits = credits + fees.loc[cardLookup[y],"benefits"]

            # chase and citi require certain cards to get the full value
            # set the flags where appropriate
            if (cardLookup[y] == "csp") or (cardLookup[y] == "csr"):
                chaseTx = True
            elif (cardLookup[y] == "premier") or (cardLookup[y] == "prestige"):
                citiTx = True

        # now we can go through the row and calculate the points
        for y in range(numCats):

            # Look up the issuer
            issuer= fees.loc[rowList[y],"issuer"]
        
            # calculate points and add to profit
            if (issuer == "amex"):
                amexPts = amexPts + pointList[y]
            elif (issuer == "chase"):
                chasePts = chasePts + pointList[y]
            elif (issuer == "citi"):
                citiPts = citiPts + pointList[y]
                
        profit = fee + credits + (amexPts * amex)

        if (chaseTx == True):
            profit = chasePts * chase + profit
        else:
            profit = chasePts * default + profit

        if (citiTx == True):
            profit = citiPts * citi + profit
        else:
            profit = citiPts * default + profit
        
        # add the row to the table
        rowList.extend((amexPts,chasePts,citiPts,fee,credits,profit))
        options.append(rowList)

    # update indexes, check for overflow and adjust accordingly
    curIndex[0] = curIndex[0] + 1

    for y in range(numCats-1):
            
        if curIndex[y] == maxIndex[y]:

            curIndex[y] = 0
            curIndex[y+1] = curIndex[y+1] + 1
    
    if(x % 500 == 0):
        print ("Row", x, "analyzed out of", numOptions, "- percent complete:", \
                "{:.2%}".format(float(x)/numOptions))    

# Display the top 50 options and make it look pretty
print ("Analyzing results, please be patient, may take around a minute")

optionsFrame = pandas.DataFrame.from_dict(options)
optionsFrame.columns = header
optionsFrame = optionsFrame.nlargest(50,"profit")

optionsFrame['amexPts'] = optionsFrame['amexPts'].map("{:,.0f}".format)
optionsFrame['chasePts'] = optionsFrame['chasePts'].map("{:,.0f}".format)
optionsFrame['citiPts'] = optionsFrame['citiPts'].map("{:,.0f}".format)

optionsFrame['fee'] = optionsFrame['fee'].map("${:,.2f}".format)
optionsFrame['credits'] = optionsFrame['credits'].map("${:,.2f}".format)
optionsFrame['profit'] = optionsFrame['profit'].map("${:,.2f}".format)

print ("\n")
print (optionsFrame.to_string(index=False))
optionsFrame.to_csv("output.csv",index=None)
