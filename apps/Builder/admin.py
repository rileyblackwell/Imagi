from django.contrib import admin
from .models import Conversation, Message, Project, Page

# Register your models here.
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Project)
admin.site.register(Page)
