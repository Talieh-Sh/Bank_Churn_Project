# Importing related libraries and modules
import os
import re
#import pickle

from flask import Flask, jsonify, render_template, request
from sqlalchemy import create_engine, and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from decimal import Decimal
from urllib.parse import unquote_plus
from urllib.parse import unquote
import sqlalchemy
from joblib import load
import numpy as np


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
#Loading Machine learning model
#################################################
# Assuming your model is named 'model.sav'
model_path = 'regression_model'
model = load(model_path)

#################################################
# Flask API App Setup
#################################################

# Create a Flask web application instance
app = Flask(__name__)

#################################################
# Flask API Routes
#################################################
# load_model =()
############# Route #1 (Homepage) ###############
# @app.route("/")
# def homepage():
#     print(request)
#     if request.method == 'GET':
#    # If 'num' is None, the user has requested page the first time
#         if(request.args.get('credit_score') == None):
#             print("Nothing")
#         else:
#             print(request.args.get('credit_score')) 

# @app.route("/")
# def homepage():
#     print(request)
#     if request.method == 'GET':
#    # If 'num' is None, the user has requested page the first time
#         if(request.args.get('credit_score') == None):
#             print("Nothing")
#         else:
#             print(request.args.get('credit_score'))            


#     # Serve the homepage HTML webpage (homepage.html)
#     return render_template("homepage.html")

@app.route("/")
def homepage():
    # Serve the homepage HTML webpage (homepage.html)
    return render_template("homepage.html")



############# Add Route for Handling Form Submission ###############
@app.route("/predict", methods=["GET"])
def predict():
    # Extracting data from the form submission
    CreditScore =request.args.get('credit_score', type=float)
    Age = request.args.get('age', type=float)
    Tenure = request.args.get('tenure', type=float)
    Balance = request.args.get('balance', type=float)
    NumOfProducts = request.args.get('num_of_products', type=int)
    HasCrCard = request.args.get('hascrcard', type=int)  # Assuming this is part of the form submission
    IsActiveMember = request.args.get('isactivemember', type=int)  # Assuming this is part of the form submission
    EstimatedSalary = request.args.get('estimated_salary', type=float)
    gender = request.args.get('gender')
    geography = request.args.get('geography')

    # Gender binary encoding
    Is_Male = 1 if gender == 'Male' else 0
    Is_Female = 0 if gender == 'Male' else 1

    # Geography binary encoding
    Is_Germany = Is_Spain = Is_France = 0
    if geography == 'Germany':
        Is_Germany = 1
    elif geography == 'Spain':
        Is_Spain = 1
    elif geography == 'France':
        Is_France = 1

    # Prepare the feature vector according to the specified format
    features = np.array([CreditScore, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Is_Male, Is_Female, Is_Germany, Is_Spain, Is_France]).reshape(1,-1)
    print(features)
    
    # Predicting the churn status
    prediction = model.predict(features)
    print(prediction)
    
    result = 'Loyal' if prediction[0] == 0 else 'Exited'
    print(result)
    # Return result to the same page or to a new prediction result page
    return render_template('homepage.html', prediction_text=f'Customer Loyalty Status: {result}')



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
    # Split the comma-separated strings into lists
    genders = gender.split(',')
    geographies = unquote_plus(geography).split(',')
    exited_values = exited.split(',')

    # Convert exited_values to floats (assuming they are stored as numeric in the database)
    exited_values = [float(value) for value in exited_values]

    # Open a session to the database
    session = Session(engine)

    # Build the filter conditions using 'in_' for matching any of the values in the lists
    filters = []
    if genders: filters.append(churn_data.gender.in_(genders))
    if geographies: filters.append(churn_data.geography.in_(geographies))
    if exited_values: filters.append(churn_data.exited.in_(exited_values))
    
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
            'Exited': float(row.exited) if isinstance(row.exited, Decimal) else row.exited,
        }
        for row in query_result
    ]

    # Return the filtered data as JSON
    return jsonify({
        "filter": {
            "gender": genders,
            "geography": geographies,
            "exited": exited_values
        },
        "data": data_list
    })

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=9091)



 