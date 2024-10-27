from django import forms

from django import forms
from .models import DevicePollConfig

class DeviceConnectionForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, initial="admin", required=True)
    password = forms.CharField(widget=forms.PasswordInput(), label="Password", required=True)
    method = forms.ChoiceField(choices=[('ssh', 'SSH'), ('telnet', 'Telnet')], label="Connection Method", required=True)
    poll_frequency = forms.ChoiceField(choices=[('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly')], label="Polling Frequency", required=False)

