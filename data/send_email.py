import smtplib


def send_email(message, email):
    sender = 'rudasocialnet@gmail.com'
    password = 'ruda2005'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender, password)
        print(email)
        server.sendmail(sender, email, message)
    except Exception as  _ex:
        print(_ex)
