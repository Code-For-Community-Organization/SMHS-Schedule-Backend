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
        print("Received email: {0}, password: {1}".format(email, password))
        try:
            requestData: Request = Request("https://aeries.smhs.org/Parent/LoginParent.aspx?page=Dashboard.aspx",
                                            password,
                                            email)
            print("requestData created, ready to load summary")
            rawJson = requestData.loadSummary()
            print("Raw json fetched: {0}".format(rawJson))
            dataParser: DataParser = DataParser(rawJson)
            parsedPeriods: list[Period] = dataParser.parseData()
            print("Parsed periods: {0}".format(parsedPeriods))
            encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
            print("Encoded periods: {0}".format(encodedPeriods))
        except JSONDecodeError:
            print("JSONDecoderError, abort 404")
            abort(404)
        return encodedPeriods
    else:
        abort(Response("Error: NO email and password provided. Please provide a valid email and password login."))

if __name__ == "__main__":
    app.run()