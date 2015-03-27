from django.contrib import admin

# Register your models here.
from agents.models import AgentIProperty, AgentStProperty, AgentGuru

admin.site.register(AgentGuru)
admin.site.register(AgentIProperty)
admin.site.register(AgentStProperty)
