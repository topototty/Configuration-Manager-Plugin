from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views.generic import View
from dcim.models import Device
from utilities.views import ViewTab, register_model_view
from .models import DeviceConnectionLog
from .device_connection_manager import DeviceConnectionManager

@register_model_view(Device, name="Connections")
class DeviceConnectionView(PermissionRequiredMixin, View):
    permission_required = "dcim.view_device"
    tab = ViewTab(
        label="Connections",
        permission="dcim.view_device",
    )

    def get(self, request, pk):
        device = Device.objects.get(pk=pk)
        connection_logs = DeviceConnectionLog.objects.filter(device=device).order_by('-connection_time')[:15]

        return render(
            request,
            "config_manage/tab_example.html",
            context={
                "object": device,
                "tab": self.tab,
                "connection_logs": connection_logs,
            },
        )

    def post(self, request, pk):
        device = Device.objects.get(pk=pk)
        connection_logs = DeviceConnectionLog.objects.filter(device=device)

        ip = request.POST.get("ip")
        username = request.POST.get("username")
        password = request.POST.get("password")
        connection_method = request.POST.get("method")
        command = request.POST.get("command", "show running-config")

        manager = DeviceConnectionManager(ip, username, password)
        output = None

        if connection_method == "ssh":
            ssh_client, status = manager.connect_ssh()
            if ssh_client:
                output = manager.execute_ssh_command(ssh_client, command)
                manager.close_ssh(ssh_client)
        elif connection_method == "telnet":
            telnet_client, status = manager.connect_telnet()
            if telnet_client:
                output = manager.execute_telnet_command(telnet_client, command)
                manager.close_telnet(telnet_client)
        else:
            status = "Invalid connection method"

        DeviceConnectionLog.objects.create(
            device=device,
            connection_status=status,
            hostname=device.name,
            connection_method=connection_method
        )

        connection_logs = DeviceConnectionLog.objects.filter(device=device)

        return render(
            request,
            "config_manage/tab_example.html",
            context={
                "object": device,
                "tab": self.tab,
                "connection_logs": connection_logs,
                "output": output,
                "command": command,
            },
        )
