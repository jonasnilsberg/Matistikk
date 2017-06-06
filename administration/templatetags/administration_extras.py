from django import template
from administration.models import Grade, Person, Gruppe

register = template.Library()


@register.simple_tag
def grade_check(grade, person):
    """
    Check if a person has permission to se the gradeDetailView of a grade.
    :param grade: The grade
    :param person: The person
    :return: Boolean value, true if the person has access.
    """
    if person.role == 4:
        return True
    elif person.role == 3:
        if grade.school.school_administrator == person:
            return True
    elif person.role == 2:
        for teacherGrade in person.grades.all():
            if grade == teacherGrade:
                return True
    return False


@register.simple_tag()
def group_check(group, person):
    if person.role == 4:
        return True
    elif person.role == 3:
        if group.grade.school.school_administrator == person:
            return True
    return False
