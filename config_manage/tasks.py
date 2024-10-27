# tasks.py
from celery import shared_task
from .models import DevicePollConfig
from dcim.models import Device
from django.utils import timezone
from .device_connection_manager import DeviceConnectionManager

@shared_task
def poll_device(device_id, username, password, method):
    """
    Задача для опроса устройства с использованием данных для подключения
    """
    device = Device.objects.get(id=device_id)
    poll_config = device.poll_config

    try:
        manager = DeviceConnectionManager(device, username, password)
        connection, status = manager.connect(method)

        if connection:
            command = "show running-config"
            output = manager.execute_command(connection, command)
            manager.close_connection(connection)

            print(f"Config for {device.name}: {output}")

            poll_config.last_polled_at = timezone.now()
            poll_config.last_poll_status = "Success"
            poll_config.last_poll_error = ""
            poll_config.save()

            return output
        else:
            poll_config.last_poll_status = "Failed"
            poll_config.last_poll_error = f"Failed to connect to {device.name} using {method}."
            poll_config.save()

            print(f"Failed to connect to {device.name}")
            return None

    except Exception as e:
        poll_config.last_poll_status = "Failed"
        poll_config.last_poll_error = str(e)
        poll_config.save()
        print(f"Error during polling device {device.name}: {e}")
        return None
