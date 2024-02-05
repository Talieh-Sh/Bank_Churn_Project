import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, render_template, url_for, jsonify
from collections import OrderedDict
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database Setup

# Engine creation 
engine = create_engine("postgresql://Sim0304:7UiV2jPMTGny@ep-calm-flower-a1s717nw.ap-southeast-1.aws.neon.tech/bank_churn?sslmode=require")

# Reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
churndata = Base.classes.bank_churndb

@app.route("/")
def welcome():
    """List all available API routes."""

    return (
        "Available Routes:<br/>"
        "/get_data<br/>"
    )

# Obtain Data from Database
@app.route("/get_data")
def dataset():

    # Create our session (link) from Python to the DB
    session = Session(engine)

        # Query all data
    results = session.query(
        churndata.id, churndata.customerid, churndata.surname, churndata.creditscore,
        churndata.geography, churndata.gender, churndata.age, churndata.tenure,
        churndata.balance, churndata.numofproducts, churndata.hascrcard,
        churndata.isactivemember, churndata.estimatedsalary, churndata.exited
    ).all()

    session.close()

    # Create a list to hold all the inputs
    finalresults = []
    for row in results:
        dataresults = {
            "id": row.id,
            "customerid": row.customerid,
            "surname": row.surname,
            "creditscore": row.creditscore,
            "geography": row.geography,
            "gender": row.gender,
            "age": row.age,
            "tenure": row.tenure,
            "balance": row.balance,
            "numofproducts": row.numofproducts,
            "hascrcard": row.hascrcard,
            "isactivemember": row.isactivemember,
            "estimatedsalary": row.estimatedsalary,
            "exited": row.exited
        }
        finalresults.append(dataresults)

    # Return JSON response using jsonify
    return jsonify({"results": finalresults})

if __name__ == '__main__':
    app.run(debug=True)