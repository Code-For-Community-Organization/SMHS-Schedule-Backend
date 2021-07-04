from flask import Flask, request
from sources.AeriesScraper import Request, DataParser, Period, PeriodEncoder
from typing import List

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
        requestData: Request = Request(password, email)
        requestData.login()
        rawJson = requestData.fetchSummary()
        dataParser: DataParser = DataParser(rawJson)
        parsedPeriods: List[Period] = dataParser.parseData()
        encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
        return f"<pre>{encodedPeriods}</pre>"
    else:
        return "Error: No email and password provided. Please provide a valid email and password login.", 403

if __name__ == "__main__":
    app.run(debug=True)