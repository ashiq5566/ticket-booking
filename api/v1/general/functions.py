import string
import random
from django.conf import settings
import base64
from random import randint


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += f"{key} - {error_message} | "

    return message[:-3]


def get_auto_id(model_class):
    last_activity = model_class.objects.order_by('-auto_id').first()
    return 1 if not last_activity else last_activity.auto_id + 1


def randomnumber(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def generate_unique_id(size=15, chars=string.ascii_lowercase + string.digits):
    
    return ''.join(random.choice(chars) for _ in range(size))


def random_password(n):
    password = []

    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    random.shuffle(characters)

    for i in range(n):
        password.append(random.choice(characters))
    random.shuffle(password)

    return "".join(password)