from json.decoder import JSONDecodeError
from flask import Flask, render_template, url_for, abort, Response, request
import json
import os
from urllib import parse
from src.scraper import EmptyPasswordError, FailedAttemptsError, Request, DataParser, Period, PeriodEncoder, ValidationError

app = Flask(__name__)

app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def home():
    return "Please go to /api/v1/grades/ for RESTful API."
@app.route('/api/v1/grades/', methods=['GET'])
def API():
    if 'email' in request.args and 'password' in request.args:
        email: str = request.args['email']
        password: str = request.args['password']
        try:
            requestData: Request = Request("https://aeries.smhs.org/Parent/LoginParent.aspx?page=Dashboard.aspx",
                                            password,
                                            email)
            requestData.login()
            rawJson = requestData.loadSummary()
            dataParser: DataParser = DataParser(rawJson)
            parsedPeriods: list[Period] = dataParser.parseData()
            encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
        except ValidationError:
            return "The Username and Password entered are incorrect.", 401
        except FailedAttemptsError:
            return "Too many failed login attempts, try again later", 429
        except EmptyPasswordError:
            return "Password must not be empty", 400
        except TimeoutError:
            return "Unknown error. Timeout waiting for the main grades page to load.", 408
        return encodedPeriods
    else:
        return "Error: No email and password provided. Please provide a valid email and password login.", 403

if __name__ == "__main__":
    app.run()