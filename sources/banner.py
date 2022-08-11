from flask import Flask, request
from flask_mail import Mail, Message
from app import app

sender = 'example@gmail.com'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = sender
app.config['MAIL_PASSWORD'] = 'wnhidjasvwxudaqh' # Needs to be received in a 2FA account with app passwords (google)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


@app.route("/submit", methods=["POST"])
def submit():
    content = request.json
    print(content)

    name = content["name"]
    phone_number = content["phone_number"]
    email = content["email"]
    school = content["school"]
    grade = content["grade"]
    send_email = content["send_email"]

    msg = Message('Email Title', sender=sender, recipients=[send_email])
    # vvv Email Content vvv
    msg.body = f"""
        name: {name},
        phone number: {phone_number},
        email: {email},
        school: {school},
        grade: {grade},
    """
    mail.send(msg)
    return True