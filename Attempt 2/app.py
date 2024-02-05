# Importing related libraries and modules
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_
from urllib.parse import unquote

from flask import Flask, jsonify, render_template
from decimal import Decimal

import os
import re
from urllib.parse import unquote
 



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


print(Base.classes.keys())  # This will print out the names of all tables that were reflected
churn_data_class = Base.classes.churn_data  # Access the churn_data class (this line assumes churn_data is the correct table name)
print(dir(churn_data_class))  # This will print out all attributes/columns of the churn_data class

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



############# Route #3 (Filter Options) ###############
@app.route("/api/filter_options")
def filter_options():
    # Establish session (link) from Python to the SQLite DB
    session = Session(engine)

    # Assuming 'gender', 'country', and 'exited' are column names in your 'churn_data' table
    # Query the unique genders from the churn_data table
    query_genders = session.query(churn_data.gender).distinct().all()
    genders = [row.gender for row in query_genders]

    # Query the unique countries from the churn_data table
    query_countries = session.query(churn_data.geography).distinct().all()
    countries = [row.geography for row in query_countries]

    # Query the unique churn values (assuming boolean or discrete values) from the churn_data table
    query_churn = session.query(churn_data.exited).distinct().all()
    churn = [float(row.exited) if isinstance(row.exited, Decimal) else row.exited for row in query_churn]
    

    # Stores the information in a dictionary (Gender, Country, Churn)
    results = {
        "Gender": genders,
        "Country": countries,
        "Churn": churn
    }

    # Return the JSON 'results' dictionary that includes all options to populate for the HTML interactive filter tools 
    return jsonify(results)


############# Route #4 (Sample Data) ###############
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

############# Route #5 ([Dynamic API Route] Query Data based on Filters Applied) ###############
@app.route("/api/filter_data/<gender>/<geography>/<exited>")
def filtered_churn_data(gender, geography, exited):
    # Validate the inputs
    valid_genders = ['Male', 'Female']
    valid_geographies = ['Spain', 'France', 'Germany']  # Assuming these are the countries in your dataset
    valid_exited_values = ['0', '1']
    
    if gender not in valid_genders:
        return jsonify({"error": "Bad Request: Gender parameter must be 'Male' or 'Female'."}), 400

    if geography not in valid_geographies:
        return jsonify({"error": f"Bad Request: Geography parameter must be one of {valid_geographies}."}), 400
    
    if exited not in valid_exited_values:
        return jsonify({"error": "Bad Request: Exited parameter must be '0' or '1'."}), 400
    
    # Decode the geography parameter to handle URL encoding
    geography = unquote(geography)

    # Open a session to the database
    session = Session(engine)

    # Build the filter conditions, ensuring we match the attribute names exactly as in your database model
    filters = [
        churn_data.gender == gender,
        churn_data.geography == geography,
        churn_data.exited == float(exited)  # Cast exited to float to match the database representation
    ]
    
    # Execute the query with filters
    query_result = session.query(churn_data).filter(and_(*filters)).all()
    session.close()

    # Transform the query result into a list of dictionaries
    data_list = [
        {
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
        for row in query_result
    ]

    # Return the filtered data as JSON
    return jsonify({
        "filter": {
            "gender": gender,
            "geography": geography,
            "exited": exited
        },
        "data": data_list
    })
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=9090)



 