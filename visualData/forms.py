"""Public chart query contracts."""

from django import forms


class HistoricalChartQuery(forms.Form):
    symbol = forms.CharField(max_length=10)
    start_date = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    end_date = forms.DateField(required=False, input_formats=["%Y-%m-%d"])

    def clean(self):
        values = super().clean()
        start, end = values.get("start_date"), values.get("end_date")
        if start and end and start > end:
            raise forms.ValidationError("start_date must be on or before end_date.")
        return values


class RecentChartQuery(forms.Form):
    symbol = forms.CharField(max_length=10)
    time_range = forms.ChoiceField(
        choices=[(value, value) for value in ("1d", "3d", "1w", "1m")],
        required=False,
    )

    def clean_time_range(self):
        return self.cleaned_data["time_range"] or "1d"
