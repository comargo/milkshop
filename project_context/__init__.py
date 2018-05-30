import django.conf


def context_processors(_request):
    return {
        'project': django.conf.settings.PROJECT
    }
