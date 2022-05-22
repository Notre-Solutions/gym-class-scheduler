import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    def __init__(self, _server='smtp.gmail.com', port='587', password='', _from='', to='', body='', subject=''):
        self.server = smtplib.SMTP(f"{_server}:{port}")

        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = subject
        self.msg['From'] = _from
        self.msg['To'] = to

        self.server.ehlo()
        self.server.starttls()

        if body != '':
            self.msg.attach(MIMEText(body, 'html'))

        if _from != '' and password != '':
            self.server.login(_from, password)

    def generate_message(self):
        return f'subject: {self.subject}\n\n{self.body}'

    def send_mail(self):
        self.server.sendmail(self.msg['From'], self.msg['To'] , self.msg.as_string())
        self.server.quit()

    def log_in(self, _from, password):
        self.server.login(_from, password)


def create_html_body(class_name, time, day, user):
    with open("email_body.html", "r", encoding='utf-8') as f:
        html = f.read()
    html = html.format(_class=class_name,
                       _time=time,
                       day=day,
                       user=user)
    return html


if __name__ == "__main__":
    email = Email(
        password='',
        _from='',
        to='',
        body=create_html_body('Test Class', '00:00', 'Today', 'test user'),
        subject='Could not book Test Class on Today at 00:00'
    )
    email.send_mail()
