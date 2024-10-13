from django import forms

class DeviceConnectionForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, initial="admin", required=True)
    password = forms.CharField(widget=forms.PasswordInput(), label="Password", required=True)
    method = forms.ChoiceField(choices=[('ssh', 'SSH'), ('telnet', 'Telnet')], label="Connection Method", required=True)
