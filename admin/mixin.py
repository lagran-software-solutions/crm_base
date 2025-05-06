from django.views.generic.edit import FormMixin, ProcessFormView
from django.views.generic import ListView
from django.db.models import Q
import pickle
import codecs


class FilterMixin(FormMixin, ProcessFormView, ListView):

    def form_valid(self, form):
        print("Form is valid")
        
        # Apply filters from the form
        and_filter = Q()
        for key, value in form.filters.items():
            if value:
                and_filter &= Q(**{key: value})

        # Apply the filter to the queryset
        self.object_list = self.get_queryset().filter(and_filter).distinct()
        print("Object list after filtering:", self.object_list)

        # Return filtered data in context
        context = self.get_context_data()
        context['form'] = form  # Ensure form is passed back to context
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        # Fetch initial queryset
        self.object_list = self.get_queryset()
        print("Object list in get method:", self.object_list)

        # Get the form for filtering
        form = self.get_form()
        
        # If form is valid, apply filters without using session
        if form.is_valid():
            and_filter = Q()
            for key, value in form.filters.items():
                if value:
                    and_filter &= Q(**{key: value})
            
            # Apply filters
            self.object_list = self.object_list.filter(and_filter).distinct()
            print("Filtered object list:", self.object_list)

        # Return the context with object list and form
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


    