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

############# Add Homepage Route ###############

@app.route("/")
def homepage():
    # Serve the homepage HTML webpage (homepage.html)
    return render_template("homepage.html")



############# Add Route for Handling Form Submission - Machine Learning Model ###############
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
    
    result = 'Loyal' if prediction[0] == 0 else 'Not Loyal'
    print(result)


    # Prepare a summary of the inputs
    # Prepare a summary of the inputs with HTML non-breaking spaces for visual spacing
    input_summary = f"Credit Score: {CreditScore},&nbsp;&nbsp;&nbsp;Age: {Age},&nbsp;&nbsp;&nbsp;Tenure: {Tenure},&nbsp;&nbsp;&nbsp;Balance: {Balance},&nbsp;&nbsp;&nbsp;" \
                f"Number of Products: {NumOfProducts},&nbsp;&nbsp;&nbsp;Has Credit Card: {'Yes' if HasCrCard == 1 else 'No'},&nbsp;&nbsp;&nbsp;" \
                f"Active Member: {'Yes' if IsActiveMember == 1 else 'No'},&nbsp;&nbsp;&nbsp;Estimated Salary: {EstimatedSalary},&nbsp;&nbsp;&nbsp;" \
                f"Gender: {gender},&nbsp;&nbsp;&nbsp;Geography: {geography}"

    # Determine result status for styling
    result_status = 'loyal' if prediction[0] == 0 else 'not-loyal'

    # Return result to the same page or to a new prediction result page
        # Include the summary in the context
        # Pass result_status to the template
    return render_template('homepage.html', prediction_text=f'Customer Loyalty Status: {result}', input_summary=input_summary, result_status=result_status)




############# Route #2 (Sample Data) ###############
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
    app.run(debug=True, host='localhost', port=9091)



 