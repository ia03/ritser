from django.contrib import admin
from .models import Topic, Debate, Argument

# Register your models here.


class TopicAdmin(admin.ModelAdmin):
    pass


class DebateAdmin(admin.ModelAdmin):
    pass


class ArgumentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Topic, TopicAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Argument, ArgumentAdmin)
