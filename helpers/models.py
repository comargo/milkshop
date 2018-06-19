import django.db.models
import django.db.models.options
from django.urls import reverse


class BrowseableObjectModel(django.db.models.Model):
    class Meta:
        abstract = True

    urlpattern = None

    def get_urlpattern(self):
        meta = self._meta
        return self.urlpattern or f"{meta.app_label}:{meta.model_name}"

    def get_object_url_kwargs(self):
        kwargs = {f"{self._meta.model_name}_pk": self.pk}
        return kwargs

    def get_absolute_url(self, kind=None):
        urlpattern = self.get_urlpattern()
        if kind:
            urlpattern = f"{urlpattern}-{kind}"
        return reverse(urlpattern, kwargs=self.get_object_url_kwargs())

    def get_edit_url(self):
        return self.get_absolute_url("edit")

    def get_delete_url(self):
        return self.get_absolute_url("delete")
