from django import template
from administration.models import Person, Grade
from maths.models import Test, Answer, GeogebraAnswer, MultipleChoiceTask

register = template.Library()


@register.simple_tag
def answered(person, test):
    for answer in person.answer_set.all():
        if answer.test_id == test.id:
            return answer
    return ""


@register.simple_tag
def get_geogebra(answer):
    return GeogebraAnswer.objects.filter(answer=answer)


@register.simple_tag
def get_mutiplechoice(task):
    return MultipleChoiceTask.objects.filter(task=task)


@register.simple_tag
def grade_check(grade, person):
    if person.role == 4:
        return True
    elif person.role == 3:
        return True
    elif person.role == 2:
        for teacherGrade in person.grades.all():
            if grade == teacherGrade:
                return True
    return False
