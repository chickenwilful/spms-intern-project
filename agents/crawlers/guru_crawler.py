import logging

logger = logging.getLogger("agents_crawler")
logger.setLevel(logging.DEBUG)

# create file handler
file_handler = logging.FileHandler('gurucrawler.log')
file_handler.setLevel(logging.INFO)

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

from _elementtree import tostring
import os
import string
import sys
from lxml import html
import time
import csv


sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spms_site.settings")
import django
django.setup()

import requests
from requests import exceptions
from agents.models import Agent, AgentGuru

HOST = "http://www.propertyguru.com.sg"
AGENTS_FIRSTNAME_URL = "http://www.propertyguru.com.sg/property-agent-directory/firstname"
AGENT_CSV_FILENAME = "agents_guru.csv"

ERROR_TOLERANT = 310
MIN_ID = 5000


def get_page(url):
    # fake header to overcome prevent robots
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,vi;q=0.6,de;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'PHPSESSID2=6mj8gknl7fb475gt3je5p4nsc3; PGURU_VISITOR=14257464361556916011fHjzCqhRhpnP; D_SID=155.69.160.11:tLNLqoiqKX+qHkFYfrO01Wc9BzDJfBD1fyCP03uzDzs; cX_S=i6z8m8nypiae71o7; SEARCH_PER_PAGE=10; __utmt=1; __utmt_guru=1; D_PID=DB18CFAB-938F-3ADE-8B23-6A06210E302D; D_IID=E57E0F31-C4A1-3439-8A11-D0D7AB463C2A; D_UID=85D8EE08-CA75-3FE5-B1B3-3519BC8C8A1A; D_HID=T5Lu2/lekdM50y/8Fugi+EPwo6zk0MRpTs26bbWB78Q; __utma=165735807.1214253065.1425928504.1425928504.1425928504.1; __utmb=165735807.10.10.1425928505; __utmc=165735807; __utmz=165735807.1425928505.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); cX_P=i7290jyt3dsyq2r4',
        'Host': "www.propertyguru.com.sg",
        'Pragma': 'no-cache'
    }
    source_code = requests.get(url, headers=headers)  # , proxies={"http": "http://1111.161.126.99:80"})
    return source_code


def get_agent_url_list_from_url(url):
    logger.info("Get Agent List, url = %s" % url)
    try:
        source_code = get_page(url)
        agent_url_list = []
        tree = html.fromstring(source_code.text)
        anchors = tree.cssselect('div.alisting_item div.alisting_thumb a')
        for a in anchors:
            agent_url_list.append(a.get('href'))
        logger.info("Get Agent List done!")
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
    try:
        source_code = get_page(url)
        tree = html.fromstring(source_code.text)
        # Get detail information about the agent
        summary1 = tostring(tree.cssselect('div.summary1')[0])
        summary2 = tostring(tree.cssselect('div.summary2')[0])
        name = html.fromstring(summary1).cssselect('h1.summarytitle a')[0].text.encode('ascii', 'ignore').decode('ascii').strip()
        try:
            estate_name = html.fromstring(summary1).cssselect('div.summary1 span.greytext')[0].text.strip()
        except IndexError:
            estate_name = None
        phone_number = html.fromstring(summary2).cssselect('span.orangebold')[0].text.strip()
        cea = html.fromstring(summary2).cssselect('div.top15 a')
        try:
            lic_number = cea[0].text.strip()
        except IndexError:
            lic_number = None
        try:
            reg_number = cea[1].text.strip()
        except IndexError:
            reg_number = None
        agent = Agent(name=name, estate_name=estate_name, phone_number=phone_number, lic_number=lic_number, reg_number=reg_number)
        logger.info(agent)
        return agent
    except requests.exceptions.HTTPError as e:
        logger.error("HTTPError: " + str(e))
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(str(e))
        return None
    except IndexError as e:
        logger.error(str(e))
        with open("error_page.html", "w") as f:
            f.write(source_code.text.encode('utf-8'))
        return None
    except AttributeError as e:
        logger.error(str(e))
        return None


def get_num_page(first_letter):
    logger.info("Get num page, first_letter= %c" % first_letter)
    url = AGENTS_FIRSTNAME_URL + "/" + first_letter + "/1?items_per_page=50"
    try:
        source_code = get_page(url)
        page = html.fromstring(source_code.text).cssselect("div.resultFound2 font.redtext")[0].text
        logger.info("Get num page, first_letter = %c done, num_page = %d" % (first_letter, int(page)))
        return int(page)
    except requests.exceptions.HTTPError as e:
        logger.error(str(e))
        return None
    except IndexError as e:
        logger.error(str(e))
        return None


def get_all_agents_url():

    existing = [agent.url for agent in Agent.objects.all()]
    agents = []
    for c in string.ascii_uppercase:
        num = get_num_page(c)
        if num:
            page_num = (num - 1) / 50 + 1
            for page in range(1, page_num + 1):
                url = AGENTS_FIRSTNAME_URL + "/%c/%d" % (c, page) + "?items_per_page=50"
                agent_url_list = get_agent_url_list_from_url(url)
                for agent_url in agent_url_list:
                    agent = get_agent_by_url(HOST + agent_url)
                    if agent is None:  # some error happens, try to process again
                        time.sleep(1)
                        agent = get_agent_by_url(HOST + agent_url)
                    else:
                        agent.save()
                        agents.append(agent)
                time.sleep(1)
        logger.info("Get all agents with first_letter = %c done!" % c)
    logger.info("Get agents: %d" % (len(agents)))
    return agents


def get_all_agents_info():
    error_num = 0
    for agent in Agent.objects.filter(id__gte=MIN_ID):
        if not agent.name:
            temp = get_agent_by_url(HOST + agent.url)
            if temp:
                agent.name = temp.name
                agent.estate_name = temp.estate_name
                agent.phone_number = temp.phone_number
                agent.lic_number = temp.lic_number
                agent.reg_number = temp.reg_number
                agent.save()
                print agent.id
                error_num = 0
            else:
                error_num += 1
                if error_num > ERROR_TOLERANT:
                    sys.exit()

            time.sleep(0.5)


def write_agents_csv(filename):
    with open(filename, "wb") as csvfile:
        field_names = ["Agent Name", "Estate Agents Name", "Phone Number", "Estate Agents License Number", "Agent Registration Number"]
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(field_names)
        agents = Agent.objects.filter(name__isnull=False)
        for agent in agents:
            if agent.estate_name:
                agent.estate_name = agent.estate_name.encode('ascii', 'ignore').decode('ascii')
            while agent.lic_number and agent.lic_number[0] != 'L':
                agent.lic_number = agent.lic_number[1:]
                agent.save()
            # print agent.url
            # print agent.name, agent.estate_name, agent.lic_number, agent.reg_number
            writer.writerow([agent.name, agent.estate_name, str(agent.phone_number)[3:], agent.lic_number, agent.reg_number])


if __name__ == "__main__":
    # get_all_agents()
    # get_all_agents_info()
    write_agents_csv(AGENT_CSV_FILENAME)
