from datetime import datetime, timedelta
import requests
from urllib import parse, request
import xml.etree.ElementTree as ET
import time
import string

PONDSIDE_SITES = [139, 140, 141, 142, 143, 122, 123, 124, 125, 126, 127, 128,\
 129, 130, 131, 132, 133, 134, 135, 136, 111, 112, 113, 114, 116, 117, 93, 94,\
 95, 97, 98, 100, 102]
OTHER_SITES = [120, 121, 159, 160, 161]
START_DATE = (2017, 6, 17)
END_DATE = (2017, 9, 20)
STAY_LENGTH = 2#Number of nights
API_KEY = ''
PARK_ID = 100

def get_date_list():
    """
    Returns a list of string dates for use in building the URL for the API call.
    Dates are the same day of the week.
    """

    #Get the total number of weeks between START_DATE and END_DATE
    weeks = ((datetime(*END_DATE) - datetime(*START_DATE)).days) // 7

    #Build a list of start dates, all of which will be the same day of week.
    #The string formatter is needed due to the API requirements.
    date_list = []
    for i in range(weeks + 1):
        date_list.append((datetime(*START_DATE) + timedelta(days = 7 * i)).
        strftime('%m/%d/%Y'))
    return date_list

def get_url(date):
        """
        Returns a single URL for a specific date and stay length (determined by
        STAY_LENGTH variable).
        Input: 'date' is a string with the format
        The use of the parse.urlunparse is probably unnecessary, but it helps to
        make the function more modular.
        """
        url_data = ('http',
                    'api.amp.active.com',
                    '/camping/campsites/',
                    '',
                    'contractCode=NY&parkId=%s&arvdate=%s&lengthOfStay=%s&api_key=%s'
                    % (PARK_ID, date, STAY_LENGTH, API_KEY),
                    '')
        url = parse.urlunparse(url_data)
        return url

def api_call_generator(wait_time):
    """
    A generator function that returns the results of the API call.
    Requires 'requests' module.
    wait_time: an int, the amount of time in seconds to wait between calls.
    """
    date_list = get_date_list()
    for date in date_list:
        url = get_url(date)
        time.sleep(wait_time)
        yield requests.get(url)

def parse_results(api_return):
    """
    Parses the xml file returned from the API call and appends the results
    to a file 'camping_spots.txt'
    """
    dates = {'Pondside': [], 'Other Sites': []}
    root = ET.fromstring(api_return.text)

    #Iterate over the results
    for child in root:
        if child.attrib['availabilityStatus'] == 'Y':
            site = int(child.attrib['Site'].lstrip(string.ascii_letters))
            if site in PONDSIDE_SITES:
                dates['Pondside'].append(site)
            elif site in OTHER_SITES:
                dates['Other Sites'].append(site)

    #Write results to file
    with open('camping_spots.txt', 'a') as f:
        f.write('%s nights, arriving on %s, sites available: %s\n' %
                  (root.attrib['lengthOfStay'], root.attrib['arvdate'],
                  str(dates)))

def get_available_dates():
    """
    The main function that calls the generator until it raises a StopIteration
    error.
    """
    wait_time = 5#In seconds
    r = api_call_generator(wait_time)

    #Add a timestamp and separator
    with open('camping_spots.txt', 'a') as f:
        f.write('-' * 25 + str(datetime.now()) + '-' * 25 + "\n")

    #Uses the generator function
    while True:
        try:
            api_call = next(r)
            parse_results(api_call)
        except StopIteration:
            break

if __name__ == "__main__":
    get_available_dates()

