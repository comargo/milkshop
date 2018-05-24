import django.db.models
from django.urls import reverse
import django.db.models.options


class Model(django.db.models.Model):
    class Meta:
        abstract = True

    urlpattern = None

    def get_urlpattern(self):
        return self.urlpattern or "{meta.app_label}:{meta.model_name}".format(meta = self._meta)

    def get_object_url_kwargs(self):
        kwargs = {"{model_name}_pk".format(model_name=self._meta.model_name): self.pk}
        return kwargs

    def get_absolute_url(self, kind=None):
        urlpattern = self.get_urlpattern()
        if kind:
            urlpattern = "{urlpattern}-{kind}".format(urlpattern=urlpattern, kind=kind)
        return reverse(urlpattern, kwargs=self.get_object_url_kwargs())

    def get_edit_url(self):
        return self.get_absolute_url("edit")

    def get_delete_url(self):
        return self.get_absolute_url("delete")
