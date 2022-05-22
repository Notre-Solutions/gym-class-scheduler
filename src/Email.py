import smtplib


class Email:
    def __init__(self, _server='smtp.gmail.com', port='587', password='', _from='', to='', body='', subject=''):
        self._from = _from
        self.to = to
        self.body = body
        self.subject = subject
        self.server = smtplib.SMTP(f"{_server}:{port}")

        self.server.ehlo()
        self.server.starttls()

        if _from != '' and password != '':
            self.server.login(_from, password)

    def generate_message(self):
        return f'subject: {self.subject}\n\n{self.body}'

    def send_mail(self):
        self.server.sendmail(self._from, self.to, self.generate_message())
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
        body='test',
        subject='test'
    )
    email.send_mail()
