import logging
import re
from lxml import etree

logger = logging.getLogger("agents_crawler")
logger.setLevel(logging.DEBUG)

# create file handler
file_handler = logging.FileHandler('stproperty_crawler.log')
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

import os
import sys
from lxml import html
import csv


sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spms_site.settings")
import django
django.setup()

import requests
from requests import exceptions
from agents.models import AgentStProperty

DOMAIN = "http://www.stproperty.sg"
SEARCH_URL = "http://www.stproperty.sg/property-agent/page%d/size-50/sort-name-asc"
AGENT_CSV_FILENAME = "agents_stproperty.csv"

MIN_ID = 0
NUM_PAGE = 460


def get_page(url):
    source_code = requests.get(url)
    return source_code


def get_agent_url_list_from_url(url):
    logger.info("Get Agent List, url = %s" % url)
    try:
        source_code = get_page(url)
        agent_url_list = []
        tree = html.fromstring(source_code.text)
        anchors = tree.cssselect('div#container')[0].cssselect('a.agent-name')
        for a in anchors:
            agent_url_list.append(a.get('href'))
        logger.info("Get %d agent urls." % len(agent_url_list))
        logger.info(agent_url_list[0])
        return agent_url_list
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP Error: " + str(e))
        return []
    except IndexError as e:
        logger.error(str(e))
        with open("error_page.html", "w") as f:
            f.write(source_code.text.decode('utf-8'))
        return []


def get_agent_by_url(url):
    logger.info("get agent by url, url = %s" % url)
    message = " url = %s" % url
    try:
        source_code = get_page(url)
        tree = html.fromstring(source_code.text)
        # Get detail information about the agent
        agent_section = tree.cssselect('div.agent-section')[0]
        name = agent_section.cssselect('ul a.agent-name')[0].text.strip()
        cea = agent_section.cssselect('li p a')
        lic_number = cea[0].text.strip()
        reg_number = cea[1].text.strip()
        try:
            estate_name = agent_section.cssselect('strong')[0].text.strip()
        except AttributeError:
            estate_name = None
        try:
            call_id = agent_section.xpath('//div[@title="Call Agent"]')[0].cssselect('a')[0].get('id')
            phone_number = get_agent_phone_number(url, source_code.text.encode('utf-8'), call_id)
        except IndexError:
            phone_number = None
        agent = AgentStProperty(name=name, estate_name=estate_name, phone_number=phone_number, lic_number=lic_number, reg_number=reg_number)
        logger.info(agent)
        return agent
    except requests.exceptions.HTTPError as e:
        logger.error("HTTPError: " + str(e) + message)
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(str(e) + message)
        return None
    except IndexError as e:
        logger.error(str(e) + message)
        with open("error_page.html", "w") as f:
            f.write(source_code.text.encode('utf-8'))
        return None
    except AttributeError as e:
        logger.error(str(e) + message)
        return None
    except UnicodeError as e:
        logger.error(str(e) + message)
        return None
    except etree.XMLSyntaxError as e:
        logger.error(str(e) + message)
        return None


def get_all_agents_url():
    for num_page in range(1, NUM_PAGE + 1):
        url = SEARCH_URL % num_page
        agent_url_list = get_agent_url_list_from_url(url)
        for agent_url in agent_url_list:
            agent = AgentStProperty(url=agent_url)
            agent.save()
    logger.info("get all %d agents url" % len(AgentStProperty.objects.all()))


def get_agent_phone_number(agent_url, source_code, call_id):
    pattern = re.escape('$("#%s").html("' % call_id) + r'.*(\d{4})\s(\d{4})'
    try:
        regex = re.search(pattern, source_code, re.I)
        phone_number = regex.group(1) + regex.group(2)
        return phone_number
    except ValueError:
        logger.error("can not get phone number for agent url = %s" %agent_url)
        return None


def get_all_agents_info():
    agents = AgentStProperty.objects.filter(id__gte=MIN_ID)
    for agent in agents:
        if not agent.name:
            temp = get_agent_by_url(DOMAIN + agent.url)
            if temp:
                agent.name = temp.name
                agent.estate_name = temp.estate_name
                agent.phone_number = temp.phone_number
                agent.lic_number = temp.lic_number
                agent.reg_number = temp.reg_number
                agent.save()
                print agent.id


def write_agents_csv(filename):
    with open(filename, "wb") as csvfile:
        field_names = ["Agent Name", "Estate Agents Name", "Phone Number", "Estate Agents License Number", "Agent Registration Number"]
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(field_names)
        agents = AgentStProperty.objects.filter(name__isnull=False)
        for agent in agents:
            agent.name = agent.name.encode('ascii', 'ignore').decode('ascii')
            if agent.estate_name:
                agent.estate_name = agent.estate_name.encode('ascii', 'ignore').decode('ascii')
            writer.writerow([agent.name, agent.estate_name, agent.phone_number, agent.lic_number, agent.reg_number])


if __name__ == "__main__":
    # get_all_agents_url()
    # get_all_agents_info()
    write_agents_csv(AGENT_CSV_FILENAME)
