from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .forms import MonthListForm, MonthlyFinForm
from .models import MonthlyFin


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
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class DetailView(generic.DetailView):
    model = MonthlyFin
    template_name = "myfinances/detail.html"

    def get_queryset(self):
        return MonthlyFin.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MonthListForm()
        return context

    def post(self, request, *args, **kwargs):
        monthlyfin = self.get_object()
        form = MonthListForm(request.POST)
        if form.is_valid():
            monthlist = form.save(commit=False)
            monthlist.month = monthlyfin
            monthlist.save()
            return HttpResponseRedirect(
                reverse("myfinances:detail", args=(monthlyfin.pk,))
            )
        self.object = monthlyfin
        context = self.get_context_data(object=monthlyfin)
        context["form"] = form
        return self.render_to_response(context)


class ResultsView(generic.DetailView):
    model = MonthlyFin
    template_name = "myfinances/results.html"
