from django.contrib import admin
from .models import Task, MultipleChoiceTask, Category

# Register your models here.
admin.site.register(Task)
admin.site.register(MultipleChoiceTask)
admin.site.register(Category)

