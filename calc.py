import pandas
pandas.options.mode.chained_assignment = None # removes warning

debug = False

# read in the CSVs
cards = pandas.read_csv('cards.csv',index_col=0)
values = pandas.read_csv('values.csv',index_col=0)
spending = pandas.read_csv('spending.csv')
bonuses = pandas.read_csv('bonuses.csv')

# extract point values
amex = values.loc["amex","value"]
chase = values.loc["chase","value"]
citi = values.loc["citi","value"]
default = values.loc["default","value"]

# category counts
numOptions = 1
numCats = len(spending)
bonusSplit = {}
maxIndex = {}
curIndex = {}
header = []

print "Analyzing Categories:",numCats

for x in range(numCats):

    # split into groups by category
    bonusSplit[x] = bonuses.groupby(bonuses.category).get_group(spending.category[x])
    
    # convert the yearly spending into points
    bonusSplit[x]["points"] = 0
    bonusSplit[x].points = bonusSplit[x]["mult"] * spending.yearly_spending[x]
   
    if debug:
        print "[DB]Category:", bonusSplit[x].category.iloc[0], \
        "Spend:", spending.yearly_spending[x], \
        "Mult:", bonusSplit[x].mult.iloc[0], \
        "Points:", bonusSplit[x].points.iloc[0]
    
    del bonusSplit[x]["mult"]

    # reset the index
    bonusSplit[x].reset_index(inplace = True, drop = True)

    # create the column name and start counting rows
    header.append(bonusSplit[x].category[0])
    
    curIndex[x] = 0
    maxIndex[x] = len(bonusSplit[x])
    numOptions = numOptions * maxIndex[x]

# initialize options list
options = pandas.DataFrame(columns = header)
options["profit"] = 0

print "Table Initialized with rows:",numOptions
numCards = len(cards)

# Populate Table
for x in range(numOptions):
    
    rowList = []
    cardLookup = []
    pointList = []
    fee = 0
    revenue = 0
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

    # If the dummy card is a CSP/CSR AND it appears in the list for spend, 
    # we're going to get a duplicate entry. don't process it
    if not ((dummyChase == True and rowList.count("csp") > 1) or \
            (dummyCiti == True and rowList.count("premier") > 1)):

        # remove duplicates so we only add fees once
        cardLookup = list(set(rowList))
            
        # match them up with the card list 
        for y in range(len(cardLookup)):

            fee = fee - cards.loc[cardLookup[y],"fee"] + cards.loc[cardLookup[y],"benefits"]

            # chase and citi require certain cards to get the full value
            # set the flags where appropriate
            if (cardLookup[y] == "csp") or (cardLookup[y] == "csr"):
                chaseTx = True
            elif (cardLookup[y] == "premier") or (cardLookup[y] == "prestige"):
                citiTx = True

        if debug:
            print "[DB]Fee:", fee

        # now we can go through the row and calculate the revenue
        for y in range(numCats):

            # Look up the issuer
            issuer= cards.loc[rowList[y],"issuer"]
        
            # calculate revenue
            if (issuer == "amex"):
                revenue = pointList[y] * amex + revenue
            
                if debug:
                    print "[DB]AmexPts:", pointList[y], "val:", amex, "total:", pointList[y] * amex

            if (issuer == "chase"):
                if (chaseTx == True):
                    revenue = pointList[y] * chase + revenue
                
                    if debug:
                        print "[DB]ChaseTxTruePts:", pointList[y], "val:", chase, "total:", pointList[y] * chase
                else:
                    revenue = pointList[y] * default + revenue
        
            if (issuer == "citi"):
                if (citiTx == True):
                    revenue = pointList[y] * citi + revenue
                else:
                    revenue = pointList[y] * default + revenue
    
        # add the row to the table
        rowList.append( revenue + fee )
        options.loc[x] = rowList

    # update indexes, check for overflow and adjust accordingly
    curIndex[0] = curIndex[0] + 1

    for y in range(numCats-1):
            
        if curIndex[y] == maxIndex[y]:

            curIndex[y] = 0
            curIndex[y+1] = curIndex[y+1] + 1
    
    if(x % 100 == 0):
        print "Row populated", x, "out of", numOptions, "- percent complete:", \
                "{:.2%}".format(float(x)/numOptions)    

# Display the top 50 options and make it look pretty
print ("\n")

options = options.nlargest(50,"profit")
options['profit'] = options['profit'].map("${:,.2f}".format)

print options.to_string(index=False)
options.to_csv("output.csv",index=None)
