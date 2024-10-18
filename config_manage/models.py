from django.db import models
from dcim.models import Device

class DeviceConnectionLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="connection_logs")
    connection_time = models.DateTimeField(auto_now_add=True)
    connection_status = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    connection_method = models.CharField(max_length=10, choices=(('ssh', 'SSH'), ('telnet', 'Telnet')))

    class Meta:
        ordering = ['-connection_time']


class DeviceConfig(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="configs")
    config_output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Конфигурация устройства"
        verbose_name_plural = "Конфигурации устройств"

    def __str__(self):
        return f"Конфигурация {self.device.name} от {self.created_at}"
