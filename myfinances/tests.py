import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import MonthlyFin, MonthList


def create_monthlyfin(month_text: str, start_date, end_date):
    return MonthlyFin.objects.create(
        month_text=month_text, start_date=start_date, end_date=end_date
    )


class MonthlyFinModelTests(TestCase):
    def test_str_returns_month_text(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        self.assertEqual(str(monthlyfin), "Test")

    def test_last_montly_fin_start_date_less_then_end_date(self):
        start = timezone.now().date() - datetime.timedelta(days=1)
        end = timezone.now().date() + datetime.timedelta(days=1)
        monthlyfin = create_monthlyfin("Range", start, end)
        self.assertTrue(monthlyfin.start_date < monthlyfin.end_date)
        self.assertTrue(monthlyfin.last_montly_fin())

    def test_last_montly_fin_within_range(self):
        start = timezone.now().date() - datetime.timedelta(days=1)
        end = timezone.now().date() + datetime.timedelta(days=1)
        monthlyfin = create_monthlyfin("Current", start, end)
        self.assertTrue(monthlyfin.last_montly_fin())

    def test_last_montly_fin_before_range(self):
        start = timezone.now().date() + datetime.timedelta(days=1)
        end = timezone.now().date() + datetime.timedelta(days=2)
        monthlyfin = create_monthlyfin("Future", start, end)
        self.assertFalse(monthlyfin.last_montly_fin())

    def test_last_montly_fin_after_range(self):
        start = timezone.now().date() - datetime.timedelta(days=2)
        end = timezone.now().date() - datetime.timedelta(days=1)
        monthlyfin = create_monthlyfin("Past", start, end)
        self.assertFalse(monthlyfin.last_montly_fin())

    def test_sum_defaults_to_zero(self):
        monthlyfin = create_monthlyfin("Default", timezone.now().date(), timezone.now().date())
        self.assertEqual(monthlyfin.summ, 0)

    def test_get_latest_by_end_date_desc(self):
        early = create_monthlyfin("Early", timezone.now().date(), timezone.now().date() - datetime.timedelta(days=1))
        late = create_monthlyfin("Late", timezone.now().date(), timezone.now().date() + datetime.timedelta(days=1))
        self.assertEqual(MonthlyFin.objects.latest(), early)


class MonthListModelTests(TestCase):
    def test_str_returns_formatted_date(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        monthlist = MonthList.objects.create(
            month=monthlyfin, check_price=100
        )
        expected = monthlist.check_date.strftime("%Y-%m-%d %H:%M")
        self.assertEqual(str(monthlist), expected)

    def test_check_price_defaults_to_zero(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        monthlist = MonthList.objects.create(month=monthlyfin)
        self.assertEqual(monthlist.check_price, 0)

    def test_check_date_defaults_to_now(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        monthlist = MonthList.objects.create(month=monthlyfin, check_price=50)
        self.assertIsNotNone(monthlist.check_date)

    def test_cascade_delete(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        MonthList.objects.create(month=monthlyfin, check_price=50)
        monthlyfin.delete()
        self.assertEqual(MonthList.objects.count(), 0)


class MonthlyFinIndexViewTests(TestCase):
    def test_no_monthlyfin(self):
        response = self.client.get(reverse("myfinances:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No monthly finances available.")
        self.assertQuerySetEqual(response.context["latest_monthlyfin_list"], [])

    def test_displays_monthlyfins(self):
        create_monthlyfin("Jan", timezone.now().date(), timezone.now().date())
        response = self.client.get(reverse("myfinances:index"))
        self.assertContains(response, "Jan")

    def test_form_in_context(self):
        response = self.client.get(reverse("myfinances:index"))
        self.assertIn("form", response.context)

    def test_post_valid_creates_monthlyfin(self):
        start = timezone.now().date()
        end = timezone.now().date() + datetime.timedelta(days=30)
        response = self.client.post(
            reverse("myfinances:index"),
            {"start_date": start.isoformat(), "end_date": end.isoformat()},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MonthlyFin.objects.count(), 1)

    def test_post_invalid_shows_errors(self):
        response = self.client.post(reverse("myfinances:index"), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)

    def test_index_limits_to_five(self):
        for i in range(6):
            d = timezone.now().date() + datetime.timedelta(days=i)
            create_monthlyfin(f"Month {i}", d, d)
        response = self.client.get(reverse("myfinances:index"))
        self.assertEqual(len(response.context["latest_monthlyfin_list"]), 5)


class DetailViewTests(TestCase):
    def test_get_valid_pk(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        response = self.client.get(reverse("myfinances:detail", args=(monthlyfin.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Period statistic")
        self.assertContains(response, "Test")

    def test_get_invalid_pk_returns_404(self):
        response = self.client.get(reverse("myfinances:detail", args=(999,)))
        self.assertEqual(response.status_code, 404)

    def test_form_in_context(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        response = self.client.get(reverse("myfinances:detail", args=(monthlyfin.pk,)))
        self.assertIn("form", response.context)

    def test_post_valid_creates_monthlist(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        response = self.client.post(
            reverse("myfinances:detail", args=(monthlyfin.pk,)),
            {"check_price": "99.99", "check_date": "2026-06-20T12:00"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(monthlyfin.monthlist_set.count(), 1)

    def test_post_invalid_shows_errors(self):
        monthlyfin = create_monthlyfin("Test", timezone.now().date(), timezone.now().date())
        response = self.client.post(reverse("myfinances:detail", args=(monthlyfin.pk,)), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
