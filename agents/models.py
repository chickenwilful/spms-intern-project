from django.db import models


class AgentGuru(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    estate_name = models.CharField(max_length=200, null=True)
    lic_number = models.CharField(max_length=20, null=True)
    reg_number = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return "{0}, {1}, {2}, {3}, {4}".format(self.name, self.phone_number, self.estate_name, self.lic_number, self.reg_number)


class AgentIProperty(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    estate_name = models.CharField(max_length=200, null=True)
    lic_number = models.CharField(max_length=20, null=True)
    reg_number = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return "{0}, {1}, {2}, {3}, {4}".format(self.name, self.phone_number, self.estate_name, self.lic_number, self.reg_number)


class AgentStProperty(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    estate_name = models.CharField(max_length=200, null=True)
    lic_number = models.CharField(max_length=20, null=True)
    reg_number = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return "{0}, {1}, {2}, {3}, {4}".format(self.name, self.phone_number, self.estate_name, self.lic_number, self.reg_number)
