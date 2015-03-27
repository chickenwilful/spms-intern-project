import os
import sys
import requests

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spms_site.settings")
import django
django.setup()


import logging
from agents.models import Agent, BadNum

logger = logging.getLogger("cea_crawler")
logger.setLevel(logging.DEBUG)

# create file handler
file_handler = logging.FileHandler('crawler.log')
file_handler.setLevel(logging.ERROR)

# create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s")
formatter.datefmt = "%d/%b/%Y %H:%M:%S"
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


from requests import Session, ConnectionError
import time
from lxml import html
import traceback


CEA_DOMAIN = "https://www.cea.gov.sg"
HEADER_URL = "https://www.cea.gov.sg/cea/app/newimplpublicregister/publicregister.jspa"
SEARCH_URL = "https://www.cea.gov.sg/cea/app/newimplpublicregister/searchPublicRegister.jspa"

LAST_NUM = "14072"
LEN = ""

# 00970

# 1, 2, 13070

# 9, 2, 90276

def get_agent_html_by_phone_number(phone_number):
    logger.info("get agent by phone number = %s" % phone_number)
    try:
        session = Session()
        session.head(HEADER_URL)
        response = session.post(
            url=SEARCH_URL,
            data={
                'type': 'searchSls',
                'slsName': '',
                'slsEaName': '',
                'slsRegNo': '',
                'slsMblNum': phone_number,
                'answer': ''
            },
            headers={
                'Referer': HEADER_URL,
            })
        if "Invalid captcha" in response.text:
            raise ConnectionError
        return response.text
    except ConnectionError as e:
        logger.error("Connection Error with phonenumber = %s" % phone_number + str(e))
        logger.info('Try to resume...')
        time.sleep(3)
        return get_agent_html_by_phone_number(phone_number)


def get_agents_by_html(source_code):  # care only about 1st page of results
    tree = html.fromstring(source_code)
    rows = tree.xpath('//tbody/tr')
    agents = []
    for row in rows:
        agents.append(Agent(reg_number=row.xpath('td/a/text()'), name=row.xpath('td/span/text()')))
    logger.info("get %d agents." % len(agents))
    if len(agents) > 0:
        logger.info(agents[0])
    return agents


def get_agents_by_phone_number(phone_number):
    source_code = get_agent_html_by_phone_number(phone_number)
    return get_agents_by_html(source_code)


def update_agents(agents, phone_number):
    logger.info("update agents with phonenumber = %s" % phone_number)
    if len(agents) == 0 or len(agents) != 8:
        return
    try:
        if len(agents) > 1:
            raise ValueError("More than 1 matched agent")
        # agent = Agent.objects.filter(reg_number=agents[0].reg_number).get(name=agents[0].name)
        # agent.phone_number = phone_number
        # agent.save()
        agent = agents[0]
        logger.info("save agent = " + str(agent) + "phonenumber = %s" % phone_number)
    except ValueError as e:
        logger.error(phone_number + " " + str(e))


def get_all_sub_sequences(input_string):
    length = len(input_string)
    return [input_string[i:j+1] for i in xrange(length) for j in xrange(i, length)]


def already_crawled(input_string):
    if len(input_string) > len(LAST_NUM):
        return False
    if len(input_string) < len(LAST_NUM):
        return True
    return input_string <= LAST_NUM


def is_valid(num):
    # if already_crawled(num):
    #     return False
    strings = get_all_sub_sequences(num)
    for string in strings:
        if BadNum.objects.filter(numstr=string).count() > 0:
            # logger.info("%s is not valid" % num)
            return False
    # logger.info("%s is valid" % num)
    return True

NUM_RANGE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
NUM_RANGE8 = ['8', '9']


def update_all_agents(num, i):
    if i > LEN:
        if not already_crawled(num):
            time.sleep(0.4)
            agents = get_agents_by_phone_number(num)
            if i > 8:
                # update agent
                update_agents(agents, num)
                return
            if len(agents) == 0:
                # update bad number
                logger.info("update badnumber = " + num)
                if BadNum.objects.filter(numstr=num).count() == 0:
                    BadNum.objects.create(numstr=num)
                print len(BadNum.objects.all())
                return
        return

    if i == 8:
        num_range = NUM_RANGE8
    else:
        num_range = NUM_RANGE

    for d in num_range:
        if (i == 8):
            new_num = d + num
        else:
            new_num = num + d
        if is_valid(new_num):
            update_all_agents(new_num, i+1)


if __name__ == "__main__":
    with open("multi_crawler_last_num.txt", "r") as f:
        LAST_NUM = f.reads()
    for l in range(5, 9):
        LEN = l
        update_all_agents("1", 2)
