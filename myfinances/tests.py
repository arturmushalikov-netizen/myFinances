import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import MonthlyFin, MonthList


def create_monthlyfin(month_text, start_date, end_date):
    """
    Create a monthlyfin with the given `month_text`, 'start_date', 'end_date'.
    """
    return MonthlyFin.objects.create(month_text=month_text, start_date=start_date, end_date=end_date)


class MonthlyFinIndexViewTests(TestCase):
    def test_no_monthlyfin(self):
        """
        If no monthlyfin exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("myfinances:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No monthly finances are available.")
        self.assertQuerySetEqual(response.context["latest_monthlyfin_list"], [])

    def test_future_monthlyfin(self):
        """
        MonthlyFin with a start_date in the future aren't displayed on
        the index page.
        """
        create_monthlyfin(month_text="Future month.", days=30)
        response = self.client.get(reverse("myfinances:index"))
        self.assertContains(response, "No monthly finances are available.")
        self.assertQuerySetEqual(response.context["latest_monthlyfin_list"], [])
