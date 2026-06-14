from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import MonthList, MonthlyFin

class IndexView(generic.ListView):
    template_name = "myfinances/index.html"
    context_object_name = "latest_monthlyfin_list"

    def get_queryset(self):
        return MonthlyFin.objects.all().order_by("-end_date")[:5]


class DetailView(generic.DetailView):
    model = MonthlyFin
    template_name = "myfinances/detail.html"
    def get_queryset(self):
        return MonthlyFin.objects.all()


class ResultsView(generic.DetailView):
    model = MonthlyFin
    template_name = "myfinances/results.html"