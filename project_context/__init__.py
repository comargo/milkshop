import django.conf


def context_processors(request):
    return {
        'project': django.conf.settings.PROJECT
    }