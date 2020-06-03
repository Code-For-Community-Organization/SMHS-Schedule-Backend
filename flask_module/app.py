from flask import Flask, render_template, url_for
import json
from flask_mail import Mail



app = Flask(__name__)

app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "woodburyjevonmao@gmail.com"
app.config['MAIL_PASSWORD'] = "SelinaJevon"
mail = Mail(app)
with open("parsedSummary.json", "r") as f:
    sumGradeJson = json.load(f)

print(sumGradeJson)

@app.route('/')
def hello_world():
    
    return render_template('home.html',sumGradeJson = sumGradeJson)

@app.route("/email")
def sendEmail():
    pass
