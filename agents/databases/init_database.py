import os
import sys
import requests
import xlrd

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spms_site.settings")
import django
django.setup()

from agents.models import Agent, AgentStProperty


def read_agent_list(input_path='agents/SalesPersons.xlsx'):

    book = xlrd.open_workbook(input_path)
    sheet = book.sheet_by_index(0)

    for row in range(2, sheet.nrows):
        reg_number = sheet.cell(row, 0).value
        name = sheet.cell(row, 1).value
        estate_name = sheet.cell(row, 2).value
        lic_number = sheet.cell(row, 3).value
        agent = Agent(reg_number=reg_number,
                      name=name,
                      estate_name=estate_name,
                      lic_number=lic_number)
        agent.save()
        print "done %d" % row
    print "done"

if __name__ == "__main__":
    # read_agent_list()
    print len(Agent.objects.filter(phone_number__isnull=False))
    print len(AgentStProperty.objects.all())