from json.decoder import JSONDecodeError
from flask import Flask, abort, Response, request
from scraper import Request, DataParser, Period, PeriodEncoder

app = Flask(__name__)

app.config['DEBUG'] = True

@app.route('/api/v1/grades/', methods=['GET'])
def home():
    if 'email' in request.args and 'password' in request.args:
        email: str = request.args['email']
        password: str = request.args['password']
        try:
            requestData: Request = Request("https://aeries.smhs.org/Parent/LoginParent.aspx?page=Dashboard.aspx",
                                            password,
                                            email)
            rawJson = requestData.loadSummary()
            dataParser: DataParser = DataParser(rawJson)
            parsedPeriods: list[Period] = dataParser.parseData()
            encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
        except JSONDecodeError:
            abort(404)
        return encodedPeriods
    else:
        abort(Response("Error: NO email and password provided. Please provide a valid email and password login."))

if __name__ == "__main__":
    app.run()