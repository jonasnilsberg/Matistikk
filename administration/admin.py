from django.contrib import admin
from .models import School, Grade, Person, Gruppe

# Register your models here.
admin.site.register(School)
admin.site.register(Grade)
admin.site.register(Person)
admin.site.register(Gruppe)
