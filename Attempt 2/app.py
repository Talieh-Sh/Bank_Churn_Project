# Importing related libraries and modules
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify, render_template
from decimal import Decimal

import os


#################################################
# SQLAlchemy Database Setup
#################################################

# Check if the "dbpassword.txt" file exists
if os.path.isfile("dbpassword.txt"):
    # Read the database password from the external file
    with open("dbpassword.txt", "r") as password_file:
        db_password = password_file.read().strip()
else:
    # Provide guidance when the file is not found
    print("The 'dbpassword.txt' file was not found. Please create the file and add your database password to it.")
    exit()

# Use the password in your URL
url = f"postgresql://talish_68:{db_password}@ep-ancient-hat-a1q8jw52.ap-southeast-1.aws.neon.tech/Bank_Churn?sslmode=require"

# Create connection to the Neon PostgreSQL database
engine = create_engine(url)

# Create a base for automatically mapping database tables to Python classes
Base = automap_base()

# Reflect the tables in the database
Base.prepare(autoload_with=engine)

# Access the "churn_data" table
churn_data = Base.classes.churn_data


#################################################
# Flask API App Setup
#################################################

# Create a Flask web application instance
app = Flask(__name__)

#################################################
# Flask API Routes
#################################################

############# Route #1 (Homepage) ###############
@app.route("/")
def homepage():
    # Serve the homepage HTML webpage (homepage.html)
    return render_template("homepage.html")


############# Route #2 (Interactive Dashboard) ###############
@app.route("/frontend")
def dashboard():
    # Serve the Analytical Dashboard HTML webpage (dashboard.html)
    return render_template("index.html")


############# Route #3 (Sample Data) ###############
@app.route("/api/v1.0/sample_data")
def sample_data():
    # Used to preview some of the data from the Bank Churn database
    # Returns sample data

    # Establish session (link) from Python to the Bank Churn DB
    session = Session(engine)

    # Query a sample of the churn data
    query_sample = session.query(churn_data).limit(500)

    # Terminate the session
    session.close()

    # Create a list to store the queried data
    data_list = []

    # For every datapoint (row) in the query...
    # Store each attribute in its respective key within a new dictionary
    # Append data_list with the new dictionary
    for row in query_sample:
        temp_dict = {
            'Id': row.id,
            'CustomerId': row.customerid,
            'Surname': row.surname,
            'CreditScore': row.creditscore,
            'Geography': row.geography,
            'Gender': row.gender,
            'Age': float(row.age) if isinstance(row.age, Decimal) else row.age,
            'Tenure': row.tenure,
            'Balance': float(row.balance) if isinstance(row.balance, Decimal) else row.balance,
            'NumOfProducts': row.numofproducts,
            'HasCrCard': float(row.hascrcard) if isinstance(row.hascrcard, Decimal) else row.hascrcard,
            'IsActiveMember': float(row.isactivemember) if isinstance(row.isactivemember, Decimal) else row.isactivemember,
            'EstimatedSalary': float(row.estimatedsalary) if isinstance(row.estimatedsalary, Decimal) else row.estimatedsalary,
            'Exited':float(row.exited) if isinstance(row.exited, Decimal) else row.exited,
        }
        data_list.append(temp_dict)

    # Store the queried sample data in a dictionary prior to being JSONified
    results = {
        "sample_data": data_list,
    }

    # Return the JSON 'results' dictionary containing the sample data
    return jsonify(results)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8080)
