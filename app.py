from collections import OrderedDict
from flask import Flask, request, redirect, url_for
from sources.AeriesScraper import Request, Period, PeriodEncoder, ValidationError
from sources.DatabaseManager import DatabaseManager, debug
from sources.Student import Student
from sources.AnnoucementScraper import AnnoucementScraper
from typing import List, Optional
from cryptography.fernet import InvalidToken
import json
from multiprocessing import Process
from datetime import date
import os
import sys

app = Flask(__name__)
if debug:
    app.secret_key = '\xc0\xed\xa2\x021\xe6\xfc\xaccZ08\x89+\x9f\xbb'
else:
    app.secret_key = os.environ.get('FLASK_SECRET')

def setup_app():
    annoucementScraper = AnnoucementScraper()
    process = Process(target=annoucementScraper.fetchAnnoucements)
    process.start()

setup_app()

@app.route('/', methods=['GET'])
def home():
    return redirect(url_for("API"), 302)

@app.route('/api/v1')
@app.route('/api')
def API():
    error_info = OrderedDict()
    error_info['Error'] = 'The API URL needs to be specified, please go to grades for student grade API or annoucements for daily annoucement API.'
    error_info['Grades API URL'] = '/api/v1/grades'
    error_info['Annoucements API URL'] = '/api/v1/annoucements'
    return error_info

@app.route('/api/grades', methods=['POST'])
@app.route('/api/v1/grades/', methods=['POST'])
def grades_API():
    #Check if POST from include email and password
    if 'email' in request.form and 'password' in request.form:
        email: str = request.form['email']
        password: str = request.form['password']

    # Fallback on URL query parameter includes
    # email and password we need
    elif 'email' in request.args and 'password' in request.args:
        # Get email and password as their string
        email: str = request.args['email']
        password: str = request.args['password']
    else:
        errorMessage: str = """Error: No email and password provided. 
        Please provide a valid email and password login."""
        return errorMessage, 400
    if email and password:
        manager = DatabaseManager()

        #Try fetch user's data from database
        userData = manager.getUserGrades(email=email)

        if 'reload' in request.args and request.args['reload'].lower() == "false":
            #Try fetch user's data from database
            userData = manager.getUserGrades(email=email)

            #Check if user's data already exist in database
            if userData is not None:
                encodedPeriods = json.dumps(userData)
                return encodedPeriods
        try:
            # Initialize networking request
            requestData: Request = Request(password, email)
            # Login to Aeries
            requestData.login()
            rawJson: Optional[str] = requestData.fetchSummary()
            if rawJson is not None:
                parsedPeriods: List[Period] = Period.convertToPeriods(rawJson)
                try:
                    manager.newUserEntry(user=Student(email=email, password=password, grades=parsedPeriods))           
                    #Schedule periodic grades networking fetch
                    #allStudents = manager.getAllUserEntryObjects()
                    #print("All students:", allStudents)
                    # if allStudents is not None:
                    #     #Fitler for outdated students logic is
                    #     #in scheduleAsyncFetch, so here we pass in all the students
                    #     loop = asyncio.new_event_loop()
                    #     loop.create_task(scheduleAsyncFetch(students=allStudents))
                    #     loop.run_forever()
                    encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)

                    return encodedPeriods
                except (ValueError, TypeError, InvalidToken) as err:
                    errorMessage: str = f"Internal: {err}"
                    if debug:
                        print(errorMessage)
                        sys.stdout.flush()
                    return errorMessage, 500
            else:
                errorMessage: str = """Internal: Server encountered error when
                fetching summary after login. Please file a bug report."""
                return errorMessage, 500

        except ValidationError as err:
            return str(err), 401
    else:
        errorMessage: str = "Error: Email and password cannot be empty."
        return errorMessage, 400

def validateDate(dateString: str) -> bool:
    try:
        date.fromisoformat(dateString)
        return True
    except ValueError:
        return False

@app.route('/api/annoucements', methods=['GET'])
@app.route('/api/v1/annoucements/', methods=['GET'])
def annoucements_API():
    if 'date' in request.args:
        date = request.args.get('date')
        annoucementScraper = AnnoucementScraper()
        annoucement_result = annoucementScraper.fetchFromDB(date_raw=date)
        if annoucement_result is not None:
            return json.dumps(annoucement_result)
        else:
            return f"Error: Annoucement for given date, {date} not found", 404
    else:
        errorMessage: str = "Error: Date parameter need to be specified."
        return errorMessage, 400

if __name__ == "__main__":
    app.run(debug=True)
