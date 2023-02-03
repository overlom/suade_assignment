# Suade Assignment

Navigate to the project directory and run the following commands:
To install flask, pandas and datetime:
pip install -r requirements.txt

Run the program:
python suade.py

Go to the endpoint URL: 
http://localhost:5000/report/?date=01/08/2019

Modify URL by entering desired date in dd/mm/yyyy format.


# Notes
Assumptions:

"The total number of customers that made an order that day." - Assumed that this question refered to unique customers

"The average order total for that day." - Assumed that order total refers to the sum of total_amounts

"The total amount of commissions generated that day." - Assumed that the commision is calculted by multiplying the total_amount by the vendors commission rate for that day.

It was assumed that there is no missing data in the provided files.

Testing: Performed using Postman.
