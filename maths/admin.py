from django.contrib import admin
from .models import Task, MultipleChoiceTask, Category, GeogebraTask, TaskCollection, Test, TaskOrder, Answer, \
    GeogebraAnswer, Item, MultipleChoiceOption

# Register your models here.
admin.site.register(Task)
admin.site.register(MultipleChoiceTask)
admin.site.register(Category)
admin.site.register(GeogebraTask)
admin.site.register(TaskCollection)
admin.site.register(Test)
admin.site.register(TaskOrder)
admin.site.register(Answer)
admin.site.register(GeogebraAnswer)
admin.site.register(Item)
admin.site.register(MultipleChoiceOption)


