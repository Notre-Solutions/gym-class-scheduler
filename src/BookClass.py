from requests import session
from bs4 import BeautifulSoup
import json
from Utils import Utils, num_to_weekday
from retry import retry
import logging
import Logs
import datetime
from Email import Email, create_html_body

log = logging.getLogger('BookClass')


class BookClass:
    def __init__(self):
        self.utils = Utils()
        class_config_file = self.utils.get_config()['REST_URLS']
        self.login_url = class_config_file['LOGIN_URL']
        self.book_class_url = class_config_file['BOOK_CLASS_URL']
        self.join_waiting_list_url = class_config_file['JOIN_WAITING_LIST_URL']
        self.time_table_url = class_config_file['TIMETABLE_URL']
        self.cal_url = class_config_file['CAL_URL']
        self.time_table_file = self.utils.get_config()['FILES']['TIME_TABLE_DATA']
        self.class_dict = {}

    @retry(Exception, delay=5, tries=6)
    def get_week_schedule_data(self):
        try:
            with session() as c:
                url = self.cal_url.format(date=datetime.datetime.today().strftime('%Y%m%d'),
                                          epoch=self.utils.get_epoch())
                request = c.get(url)
                html = request.text.split('html":"')[1].split('"}')[0]
                html = html.replace(r'\n', '').replace(r'\t', '').replace('\\', '')
                soup = BeautifulSoup(html, 'html.parser')
                classes_per_day = soup.find_all(class_='fkl-cal-col')
                if len(classes_per_day) == 0:
                    log.error('Could not fetch the table data, function will wait 5 seconds and try again \
                    ( max number 6 times )')
                    raise Exception
                for i, _class in enumerate(classes_per_day):
                    if i < 7:
                        day = _class.find(class_='fkl-date-title').get_text()
                        if day == 'Today':
                            day = num_to_weekday[datetime.datetime.today().weekday()]
                        self.class_dict[day] = {}
                        class_data = classes_per_day[i + 7].find_all(class_='fkl-cal-td')
                        for data in class_data:
                            html_attrs = data.attrs
                            if html_attrs['data-location'] == 'Canary Wharf':
                                data_id = html_attrs['data-id']
                                class_name = html_attrs['data-service'].upper()
                                class_time = html_attrs['data-time'].split(' ')[0]
                                self.class_dict[day][class_name + ' ' + class_time] = {
                                    "id": data_id,
                                    "time": class_time,
                                    "name": class_name
                                }
                log.info('Writing data to {0}'.format(self.time_table_file))
                with open(self.time_table_file, 'w') as fp:
                    json.dump(self.class_dict, fp, indent=4)
        except Exception as error:
            log.error(error)
            raise

    def get_class_id(self, class_name, class_time, class_day):
        try:
            if not self.utils.does_file_exists(self.time_table_file):
                log.info('Pulling class data for the week; no json file found: {0}'.format(self.time_table_file))
                self.get_week_schedule_data()
            with open(self.time_table_file, 'r') as json_file:
                log.info('Retrieving data from {0}'.format(self.time_table_file))
                data = json.load(json_file)
            class_id = data[class_day][class_name + ' ' + class_time]['id']
            log.info('Class id: {0}'.format(class_id))
            return class_id
        except Exception as error:
            log.error('Error getting class id', error)

    @retry(Exception, delay=5, tries=2)
    def join_waiting_list(self, user, password, class_name, class_time, class_day, class_id):
        try:
            log.info('Joining waiting list for class: {0} on {1} at {2} for user: {3}'. format(
                class_name,
                class_day,
                class_time,
                user
            ))
            payload = {
                'action': 'fkl_ajax_login',
                'email': user,
                'password': password
            }
            log.info('Class id found: {0}'.format(class_id))
            with session() as c:
                log.info('Opening session to send post request')
                c.post(self.login_url, data=payload)
                if len(c.cookies.items()) > 0:
                    log.info('Opened session successfully')
                else:
                    log.exception(
                        'Unable to open session; please check if the username and password is correct for user\
                         {0}'.format(user))
                    raise ConnectionError
                log.info('Sending get request to join waiting list for class: {0}'.format(class_name))
                response = c.get(self.book_class_url.format(epoch=self.utils.get_epoch(), class_id=class_id))
                if response.status_code == 200:
                    log.info('Response 200')
                    if 'Something went wrong' in response.text:
                        log.error(
                            'Unable to join waiting list for class ({0} on {1} at {2} for user: {3}) - \
                            something went wrong.'.format(
                                class_name,
                                class_day,
                                class_time,
                                user
                            ))
                    else:
                        log.info('Join waiting list: {0} on {1} at {2} for user: {3}'.format(
                            class_name,
                            class_day,
                            class_time,
                            user
                        ))
                else:
                    log.error('Response {0}'.format(response.status_code))
        except Exception as error:
            log.error('Error booking class', error)
        finally:
            email_config = self.utils.get_config()['EMAIL']
            email = Email(
                password=email_config['PASSWORD'],
                _from=email_config['ADDRESS'],
                to=user,
                subject=f'Could not book {class_name} on {class_day} at {class_time}',
                body=create_html_body(class_name=class_name,
                                      time=class_time,
                                      day=class_day,
                                      user=user)
            )
            email.send_mail()

    @retry(Exception, delay=5, tries=2)
    def book_class(self, user, password, class_name, class_time, class_day):
        try:
            log.info('Booking class: {0} on {1} at {2} for user: {3}'. format(
                class_name,
                class_day,
                class_time,
                user
            ))
            payload = {
                'action': 'fkl_ajax_login',
                'email': user,
                'password': password
            }
            class_id = self.get_class_id(class_name, class_time, class_day)
            log.info('Class id found: {0}'.format(class_id))
            with session() as c:
                log.info('Opening session to send post request')
                c.post(self.login_url, data=payload)
                if len(c.cookies.items()) > 0:
                    log.info('Opened session successfully')
                else:
                    log.exception('Unable to open session; please check if the username and password is correct for \
                    user {0}'.format(user))
                    raise ConnectionError
                log.info('Sending get request to book class: {0}'.format(class_name))
                response = c.get(self.book_class_url.format(epoch=self.utils.get_epoch(), class_id=class_id))
                if response.status_code == 200:
                    log.info('Response 200')
                    if 'Something went wrong' in response.text:
                        log.error('Unable to book class ({0} on {1} at {2} for user: {3}) - something went wrong. \
                        The class is most likely booked up'.format(
                            class_name,
                            class_day,
                            class_time,
                            user
                        ))
                        log.info('Attempting to join waiting list.')
                        self.join_waiting_list(user, password, class_name, class_time, class_day, class_id)
                    else:
                        log.info('Class Booked: {0} on {1} at {2} for user: {3}'.format(
                            class_name,
                            class_day,
                            class_time,
                            user
                        ))
                else:
                    log.error('Response {0}'.format(response.status_code))
        except Exception as error:
            log.error('Error booking class', error)


if __name__ == "__main__":
    Logs.setup_logger('BookClass')
    BookClass().get_week_schedule_data()
    BookClass().book_class(user='stephenkelehan@gmail.com',
                           password='46292edd',
                           class_name='BOXING FDM',
                           class_time='19:30',
                           class_day='Wednesday')
