from flask import Flask, request, redirect, url_for
from sources.AeriesScraper import Request, DataParser, Period, PeriodEncoder, ValidationError
from sources.DatabaseManager import DatabaseManager
from sources.Student import Student
from typing import List, Optional
from cryptography.fernet import InvalidToken
import json

def wrapTojsonHTML(content: str, appendBraces: bool = True) -> str:
        preTag: str = '<pre style="word-wrap: break-word; white-space: pre-wrap;">'
        return f"{{ {content} }}" if appendBraces else f"{content}"

app = Flask(__name__)

app.config['DEBUG'] = True


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for("API"), 302)


@app.route('/api/v1/grades/', methods=['GET', 'POST'])
def API():
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

        if 'reload' in request.args and request.args['reload'].lower() == "false":
            # Check email and password not empty
            if email and password:
                manager = DatabaseManager()

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
                        print(errorMessage)
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
    else:
        errorMessage: str = """Error: No email and password provided. 
        Please provide a valid email and password login."""
        return errorMessage, 400


if __name__ == "__main__":
    app.run(debug=True)
