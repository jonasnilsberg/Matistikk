from django.contrib import admin
from .models import GeogebraAssignment, GeogebraAnswer, Test, TestView
# Register your models here.

admin.site.register(GeogebraAssignment)
admin.site.register(Test)
admin.site.register(TestView)
admin.site.register(GeogebraAnswer)