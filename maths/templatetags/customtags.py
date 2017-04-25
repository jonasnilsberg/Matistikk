from django import template
from administration.models import Person
from maths.models import Test

register = template.Library()


@register.simple_tag
def answered(person, test, num):
    for answer in person.answer_set.all():
        if answer.test_id == test.id:
            if num == 1:
                return "success"
            elif num == 2:
                return "list-group-item-success"
    return ""
