from flask import Flask, request
from sources.AeriesScraper import Request, DataParser, Period, PeriodEncoder, ValidationError
from typing import List
    
def wrapTojsonHTML(content: str, appendBraces: bool = True) -> str:
        preTag: str = '<pre style="word-wrap: break-word; white-space: pre-wrap;">'
        return f"{preTag}{{ {content} }}</pre>" if appendBraces else f"{preTag}{content}</pre>"

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
        if email and password:
            try:
                requestData: Request = Request(password, email)
                requestData.login()
                rawJson = requestData.fetchSummary()
                dataParser: DataParser = DataParser(rawJson)
                parsedPeriods: List[Period] = dataParser.parseData()
                encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
                return wrapTojsonHTML(encodedPeriods, appendBraces=False)

            except ValidationError as err:
                return wrapTojsonHTML(str(err))
        else:
            errorMessage: str = "Error: Email and password cannot be empty."
            return wrapTojsonHTML(errorMessage), 400
    else:
        errorMessage: str = "Error: No email and password provided. Please provide a valid email and password login."
        return wrapTojsonHTML(errorMessage), 403

if __name__ == "__main__":
    app.run(debug=True)