Q: What does this thing do?
A: Brute forces credit card combinations to determine the best credit card to use
for each category. Results will print in the terminal along with a file called output.csv

Q: Isn't there a more efficient way to do this?
A: I'm a product manager not a dev

Q: Are there any prerequisites
A: You'll need to install Python and Pandas. The following command should take care of it,
adjust as needed for your particular Linux installation
> sudo apt-get install python3-pandas

Q: how do I run this thing?
A:
> python3 calc.py

Q: What are each of the sheets
A: Each sheet is a CSV file with the following

annualSpend.csv: The yearly spending given a category. You'll need to fill these in with your
specific categories and your yearly spending

multipliers.csv: The category of spend, the card that it's put on, and the points multiplier
- If a category is in annualSpend.csv it MUST be in multipliers.csv
- However, a category in multipliers.csv that isn't in annualSpend.csv will be skipped
- The more cards that are listed the longer the script takes, so the easiest way is to analyze only a few
categories at a time in annualSpend.csv
- NOTE: some Amex cards require a minimum amount of swipes to get the elevated bonus,
this assumes that you will always hit that amount

fees.csv: this is a list of credit cards, the issuer, the annual fee, and the benefits that you
personally receive from them. Everyone values their benefits differently
- Each credit card in multipliers.csv MUST match one in fees.csv
- However, if a card is in fees.csv it doesn't have to match one in multipliers.csv

pointValues.csv: The value of each point per issuer
- The script takes into account that in order to do points transfers an annual fee card
from chase or citi are required. If that condition is not met a default value is used

Q: What's with the dummyCiti and dummyChase cards
A: Right, so there are certain scenarios where even if expenses arent put on a credit card
it's worth holding onto to get the giant bump in another category.

Example: Amex Green gives 3% cash back on travel while CFF gives 3% on Restaurants
If you value Amex points higher than Chase points you're better off holding the CSP
and not putting categoried spend on it so that the Freedom points are worth a lot more

Q: Surely there must be a better way to do that
A: There probably is. And don't call me Shirley
