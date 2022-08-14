from flask_mail import Message


def send_email(json):
    name = json["name"]
    phone_number = json["phone_number"]
    email = json["email"]
    school = json["school"]
    grade = json["grade"]
    send_to = json["send_email"]

    msg = Message('Email Title', sender=sender, recipients=[send_to])
    # vvv Email Content vvv
    msg.body = f"""
            name: {name},
            phone number: {phone_number},
            email: {email},
            school: {school},
            grade: {grade},
        """
    mail.send(msg)