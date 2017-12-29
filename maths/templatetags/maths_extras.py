from django import template
from maths.models import Answer, GeogebraAnswer, MultipleChoiceTask, GeogebraTask, MultipleChoiceOption, \
    InputFieldTask, Directory
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
def get_geogebra_task(task):
    return GeogebraTask.objects.get(task=task)


@register.simple_tag
def get_geogebra_count(test):
    count = 0
    for item in test.task_collection.items.all():
        if item.task.extra == 1:
            count += 1
    return count


@register.simple_tag
def get_mutiplechoice(task):
    """
    Gets multiple choice values of a multiple choice task
    :param task: The task
    :return: The MultipleChoiceTask.
    """
    return MultipleChoiceTask.objects.filter(task=task)


@register.simple_tag
def get_multiplechoice_options_length(multiplechoice_task):
    length = 0
    for option in multiplechoice_task.multiplechoiceoption_set.all():
        length += (len(option.option))
    return length


@register.simple_tag
def get_multiplechoice_options_correct_count(multiplechoice_task):
    return MultipleChoiceOption.objects.filter(MutipleChoiceTask=multiplechoice_task, correct=True).count()

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


@register.simple_tag
def get_variable_count(item):
    """
    Returns the variable count of a task.
    :param item: item of a task
    :return: variable count.
    """
    variable_table = item.variables.split('|||||')
    return variable_table


@register.simple_tag
def multiplechoice_answered(option, answer, index):
    answer_table = answer.split('<--|-->')
    answers = answer_table[index-1].split('|||||')
    if option.option in answers:
        return True
    return False


@register.simple_tag
def task_answered(task):
    answer = False
    for item in task.item_set.all():
        if item.answer_set.all():
            answer = True
    return answer


@register.simple_tag
def insert_params(text, variables):
    variablesTable = variables.split('|||||')
    for i in range(len(variablesTable)):
        text = text.replace('matistikkParameter'+str(i+1), variablesTable[i])
    return text


@register.simple_tag
def get_inputfields(task):
    return InputFieldTask.objects.filter(task=task)


@register.simple_tag
def get_input(answer, nr):
    answer_list = answer.split('|||||')
    return answer_list[nr-1]


@register.simple_tag
def get_margin(fraction):
    if fraction:
        return 0
    else:
        return 10


@register.simple_tag
def get_directory_path(directory_id):
    directory = Directory.objects.get(id=directory_id)
    return directory.__str__()

