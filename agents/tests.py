# -*- coding: utf-8 -*-
from django.test import TestCase

# Create your tests here.
from agents.crawlers.guru_crawler import get_agent_by_url, get_agent_url_list_from_url, get_num_page
from agents.models import Agent


class CEACrawlerTest(TestCase):
    pass


class GuruCrawlerTest(TestCase):

    def test_get_agent_url_list_by_url(self):
        agent_url_list = get_agent_url_list_from_url("http://www.propertyguru.com.sg/property-agent-directory/firstname/A/1?items_per_page=50")
        self.assertEquals(len(agent_url_list), 50)
        self.assertEquals(agent_url_list[0], "/agent/a-balaji-12016")

        agent_url_list = get_agent_url_list_from_url("http://www.propertyguru.com.sg/property-agent-directory/firstname/A/22/items_per_page=50")
        self.assertEquals(len(agent_url_list), 35)
        self.assertEquals(agent_url_list[0], "/agent/audrey-lee-78239")

    def test_get_num_page(self):
        self.assertEquals(get_num_page("A"), 1085)
        self.assertEquals(get_num_page("Z"), 76)

    def test_get_agent_by_url(self):
        agent = get_agent_by_url("http://www.propertyguru.com.sg/agent/patrik-tam-37198")
        self.assertEquals(agent.name, "Patrik Tam")
        self.assertEquals(agent.estate_name, "Starts Singapore Pte Ltd")
        self.assertEquals(agent.phone_number, "+6593289376")
        self.assertEquals(agent.lic_number, "L3010028Z")
        self.assertEquals(agent.reg_number, "R017272G")

        agent = get_agent_by_url("http://www.propertyguru.com.sg/agent/rachael-tan--22605")
        self.assertEquals(agent.name, "Rachael Tan".decode('utf-8'))
        self.assertEquals(agent.estate_name, "PROPNEX REALTY PTE LTD")
        self.assertEquals(agent.phone_number, "+6590901288")
        self.assertEquals(agent.lic_number, "L3008022J")
        self.assertEquals(agent.reg_number, "R024252J")

    def test_get_all_agent(self):
        first_agent = Agent.objects.get(pk=1)
        self.assertEquals(first_agent.name, "")
        last_agent = Agent.objects.get(pk=11186)
