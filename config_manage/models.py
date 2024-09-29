from django.db import models
from dcim.models import Device

class DeviceConnectionLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    connection_time = models.DateTimeField(auto_now_add=True)
    connection_status = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100)
    connection_method = models.CharField(max_length=10, choices=[('ssh', 'SSH'), ('telnet', 'Telnet')], default='ssh')

    def __str__(self):
        return f"{self.device.name} - {self.connection_method} - {self.connection_status}"
