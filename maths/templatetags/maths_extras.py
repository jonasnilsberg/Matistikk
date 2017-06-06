from django import template
from maths.models import Answer, GeogebraAnswer, MultipleChoiceTask
from administration.models import Gruppe, Person, Grade

register = template.Library()


@register.simple_tag
def answered(person, test):
    """
    Checks if a test is answered by a person
    :param person: The person
    :param test: The test
    :return: The answer if found, or an empty string if not
    """
    for answer in person.answer_set.all():
        if answer.test_id == test.id:
            return answer
    return ""


@register.simple_tag
def get_geogebra(answer):
    """
    Gets the geogebra answer from an answer.
    :param answer: The answer
    :return: The geogebra answer.
    """
    return GeogebraAnswer.objects.filter(answer=answer)


@register.simple_tag
def get_mutiplechoice(task):
    """
    Gets multiple choice values of a multiple choice task
    :param task: The task
    :return: The MultipleChoiceTask.
    """
    return MultipleChoiceTask.objects.filter(task=task)


@register.simple_tag
def split_geo(geo):
    """
    Splits the geodata string.
    :param geo: the data
    :return: Table of data splitted
    """
    geotab = str.split(geo, "|||")
    return geotab


@register.simple_tag
def split_geo2(geo):
    """
    Splits the geodata by time.
    :param geo: The data
    :return: table of time and action.
    """
    geotab = str.split(geo, '|')
    return geotab


@register.simple_tag
def get_answered(test, username):
    """
    Returns the first answer from a test and user.
    :param test: The test
    :param username: The username of the user
    :return: The answer object. 
    """
    answer = Answer.objects.filter(test=test, user__username=username).first()
    return answer
