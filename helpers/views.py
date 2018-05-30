import django.core.exceptions
import django.forms
import django.views.generic


class CreateWithParentView(django.views.generic.CreateView):
    parent_field = None

    def get_initial(self):
        if self.parent_field is None:
            raise django.core.exceptions.ImproperlyConfigured(
                "Using CreateWithParentView (base class of %s) without "
                "the 'parent_field' attribute is prohibited." % self.__class__.__name__
            )
        if not hasattr(self, self.parent_field):
            raise django.core.exceptions.ImproperlyConfigured(
                "Using CreateWithParentView (base class of %s) without "
                "the parent object attribute %s is prohibited." % (self.__class__.__name__, self.parent_field)
            )
        initial = super().get_initial()
        initial[self.parent_field] = getattr(self, self.parent_field)
        return initial

    # Rewritten from ModelFormMixin.get_form_class
    def get_form_class(self):
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise django.core.exceptions.ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise django.core.exceptions.ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            widgets = {
                self.parent_field: django.forms.HiddenInput,
            }
            if hasattr(self, 'widgets'):
                widgets.update(self.widgets)

            fields: list = self.fields
            if self.fields != django.forms.ALL_FIELDS and self.parent_field not in self.fields:
                fields.append(self.parent_field)

            return django.forms.models.modelform_factory(model, fields=self.fields, widgets=widgets)
