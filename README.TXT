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

annualSpend.csv: 
- The yearly spending in a given category
- ACTION ITEM (AI) - Fill in your yearly spending

multipliers.csv: 
- The category of spend, the card that it's put on, and the points multiplier
- Unless a new credit card comes in with new multipliers this can stay mostly static
- NOTE: some Amex cards require a minimum amount of swipes to get the elevated bonus,
this assumes that you will always hit that amount

fees.csv: this is a list of credit cards, the issuer, the annual fee, the benefits,
and whether or not a card should be analyzed
- The fee column should be roughly static unless they change
- AI: Fill in with benefits you derive from the card (Example: DoorDash + CSR Travel Credit)
- AI: Select if the card should be included in the analysis
- Note: It can take awhile to run with all combos so you may want to start by excluding some cards 

pointValues.csv: The value of each point per issuer
- AI: Fill in with your personal point values
- Note: The script takes into account that in order to do points transfers an annual fee card
from chase or citi are required. If that condition is not met a default value is used

Q: What's with the dummyCiti and dummyChase cards I see in the results
A: Right, so there are certain scenarios where even if expenses arent put on a credit card
it's worth holding onto to get the giant bump in another category.

Example: Even with no Travel or Dining spend you may want to hold a CSP anyway to unlock
the higher value from point transfers from a Freedom card

Q: Surely there must be a better way to do that
A: There probably is. And don't call me Shirley
