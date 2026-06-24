from django.contrib import admin

from .models import MonthList, MonthlyFin


class ChecksInline(admin.TabularInline):
    model = MonthList
    extra = 3


class MonthlyFinAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["month_text", "summ"]}),
        ("Date information", {"fields": ["start_date", "end_date"]}),
    ]
    inlines = [ChecksInline]
    list_display = ["month_text", "summ", "start_date", "end_date"]
    list_filter = ["start_date"]
    search_fields = ["month_text"]


admin.site.register(MonthlyFin, MonthlyFinAdmin)
