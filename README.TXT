Q: What does this thing do?
A: Brute forces credit card combinations to determine the best credit card to use
for each category

Q: Isn't there a more efficient way to do this?
A: I'm a product manager not a dev

Q: Are there any prerequisites
A: You'll need to install Python and Pandas. The following command should take care of it,
adjust as needed for your particular Linux installation
> sudo apt-get install python3-pandas

Q: how do I run this thing?
A:
> python calc.py

Q: What are each of the sheets
A: Each sheet is a CSV file with the following

spending.csv: The yearly spending given a category. You'll need to fill these in with your
specific categories and your yearly spending

bonuses.csv: The category of spend, the card that it's put on, and the points multiplyer
- If a category is in spending.csv it MUST be in bonuses.csv
- However, a category in bonuses.csv that isn't in spending.csv will be skipped
- The more cards that are listed the longer the script takes, so the easiest way is to analyze only a few
categories at a time in spending.csv
- NOTE: some Amex cards require a minimum amount of swipes to get the elevated bonus,
this assumes that you will always hit that amount

cards.csv: this is a list of credit cards, the issuer, the annual fee, and the benefits that you
personally receive from them. Everyone values their benefits differently
- Each credit card in bonuses.csv MUST match one in cards.csv
- However, if a card is in cards.csv it doesn't have to match one in bonuses.csv

values.csv: The value of each point per issuer
- The script takes into account that in order to do points transfers an annual fee card
from chase or citi are required. If that condition is not met a default value is used

Q: What's with the dummyCiti and dummyChase cards
A: Right, so there are certain scenarios where even if expenses arent put on a credit card
it's worth holding onto to get the giant bump in another category.

Example: Amex Green gives 3% cash back on travel while CFF gives 3% on Restaurants
If you value Amex points higher than Chase points you're better off holding the CSP
and not putting categoried spend on it so that the Freedom points are worth a lot more

Q: Surely there must be a better way to do this
A: There probably is. And don't call me Shirley
