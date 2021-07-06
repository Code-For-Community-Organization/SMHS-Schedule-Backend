from flask import Flask, request, redirect, url_for
from sources.AeriesScraper import Request, DataParser, Period, PeriodEncoder, ValidationError
from sources.Database.DatabaseManager import DatabaseManager
from sources.Database.User import User
from typing import List, Optional
from cryptography.fernet import InvalidToken


def wrapTojsonHTML(content: str, appendBraces: bool = True) -> str:
    return f"<pre>{{ {content} }}</pre>" if appendBraces else f"<pre>{content}</pre>"


app = Flask(__name__)

app.config['DEBUG'] = True


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for("API"), 302)


@app.route('/api/v1/grades/', methods=['GET'])
def API():
    # Verify that URL query parameter includes
    # email and password we need
    if 'email' in request.args and 'password' in request.args:

        # Get email and password as their string
        email: str = request.args['email']
        password: str = request.args['password']

        # Check email and password not empty
        if email and password:
            try:
                manager = DatabaseManager()
                manager.newUserEntry(user=User(email=email, password=password))
                print(manager.getUserEntry(email=email))
            except ValueError as err:
                errorMessage: str = f"Internal: {err}"
                print(errorMessage)
            except TypeError as err:
                errorMessage: str = f"Internal: {err}"
                print(errorMessage)
            except InvalidToken as err:
                errorMessage: str = f"Internal: {err}"
                print(errorMessage)

            try:
                # Initialize networking request
                requestData: Request = Request(password, email)
                # Login to Aeries
                requestData.login()
                rawJson: Optional[str] = requestData.fetchSummary()
                if rawJson is not None:
                    dataParser: DataParser = DataParser(rawJson)
                    parsedPeriods: List[Period] = dataParser.parseData()
                    encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
                    return encodedPeriods
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
