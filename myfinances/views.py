from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .forms import MonthlyFinForm
from .models import MonthList, MonthlyFin

class IndexView(generic.ListView):
    template_name = "myfinances/index.html"
    context_object_name = "latest_monthlyfin_list"

    def get_queryset(self):
        return MonthlyFin.objects.all().order_by("-end_date")[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MonthlyFinForm()
        return context

    def post(self, request, *args, **kwargs):
        form = MonthlyFinForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("myfinances:index"))
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class DetailView(generic.DetailView):
    model = MonthlyFin
    template_name = "myfinances/detail.html"
    def get_queryset(self):
        return MonthlyFin.objects.all()


class ResultsView(generic.DetailView):
    model = MonthlyFin
    template_name = "myfinances/results.html"