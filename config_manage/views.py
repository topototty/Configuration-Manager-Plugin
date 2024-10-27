import difflib
from datetime import timezone
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View
from utilities.views import ViewTab, register_model_view

from .models import DeviceConnectionLog, DevicePollConfig, DeviceConfig
from .tables import DeviceConnectionLogTable
from django_tables2 import RequestConfig

from django.shortcuts import render, redirect, get_object_or_404
from .forms import DeviceConnectionForm
from dcim.models import Device
from .device_connection_manager import DeviceConnectionManager
from django.utils import timezone


def get_diff(latest_config_lines, rendered_config_lines):
    diff = []
    matcher = difflib.SequenceMatcher(None, latest_config_lines, rendered_config_lines)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for line in latest_config_lines[i1:i2]:
                diff.append({'line': line, 'class': 'text-muted'})  # Совпадающие строки
        elif tag == 'replace':
            for line in latest_config_lines[i1:i2]:
                diff.append({'line': f"- {line}", 'class': 'text-danger'})  # Удаленные строки
            for line in rendered_config_lines[j1:j2]:
                diff.append({'line': f"+ {line}", 'class': 'text-success'})  # Новые строки
        elif tag == 'delete':
            for line in latest_config_lines[i1:i2]:
                diff.append({'line': f"- {line}", 'class': 'text-danger'})  # Удаленные строки
        elif tag == 'insert':
            for line in rendered_config_lines[j1:j2]:
                diff.append({'line': f"+ {line}", 'class': 'text-success'})  # Новые строки
    return diff

@register_model_view(Device, name="Connections")
class DeviceConnectionView(PermissionRequiredMixin, View):
    permission_required = "dcim.view_device"
    tab = ViewTab(
        label="Connections",
        permission="dcim.view_device",
    )

    def get(self, request, pk):

        device = Device.objects.get(pk=pk)
        connection_logs = DeviceConnectionLog.objects.filter(device=device).order_by('-connection_time')

        table = DeviceConnectionLogTable(connection_logs)

        RequestConfig(request, paginate={"per_page" : 10}).configure(table)

        form = DeviceConnectionForm()

        return render(
            request,
            "config_manage/tab_example.html",
            context={
                "object": device,
                "tab": self.tab,
                "table": table,
                "form": form,
            },
        )

    def post(self, request, pk):

        device = Device.objects.get(pk=pk)
        connection_logs = DeviceConnectionLog.objects.filter(device=device).order_by('-connection_time')
        form = DeviceConnectionForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            method = form.cleaned_data['method']
            command = "show running-config"

            # Инициализация менеджера подключения и выполнение команды
            manager = DeviceConnectionManager(device, username, password)
            connection, status = manager.connect(method)

            output = None
            if connection:
                output = manager.execute_command(connection, command)
                manager.close_connection(connection)

                # Сохранение конфигурации в модель DeviceConfig
                DeviceConfig.objects.create(
                    device=device,
                    config_output=output
                )

            # Запись лога соединения
            DeviceConnectionLog.objects.create(
                device=device,
                connection_status=status,
                hostname=device.name,
                connection_method=method
            )

            # Повторно получаем логи после добавления нового
            connection_logs = DeviceConnectionLog.objects.filter(device=device).order_by('-connection_time')

            # Настройка таблицы после POST-запроса
            table = DeviceConnectionLogTable(connection_logs)
            RequestConfig(request).configure(table)

            return render(
                request,
                "config_manage/tab_example.html",
                context={
                    "object": device,
                    "tab": self.tab,
                    "table": table,
                    "output": output,
                    "form": form
                }
            )

        table = DeviceConnectionLogTable(connection_logs)
        RequestConfig(request).configure(table)

        return render(
            request,
            "config_manage/tab_example.html",
            {
                "object": device,
                "tab": self.tab,
                "table": table,
                "form": form,
            }
        )


@register_model_view(Device, name="Configuration manage")
class DeviceConfigView(PermissionRequiredMixin, View):
    permission_required = "dcim.view_device"
    tab = ViewTab(
        label="Configuration manage",
        permission="dcim.view_device",
    )

    def get(self, request, pk):
        device = Device.objects.get(pk=pk)
        latest_config = DeviceConfig.objects.filter(device=device).order_by('-created_at').first()

        config_template = device.config_template

        context = {
            "device": device,
        }

        if config_template:
            try:
                rendered_config = config_template.render(context).strip()
            except Exception as e:
                rendered_config = f"Error rendering template: {e}"
        else:
            rendered_config = None

        if latest_config:
            config_blocks = self.split_config_into_blocks(latest_config.config_output)
        else:
            config_blocks = []

        latest_config_lines = latest_config.config_output.splitlines() if latest_config else []
        rendered_config_lines = rendered_config.splitlines() if rendered_config else []

        config_diff = get_diff(latest_config_lines, rendered_config_lines)

        return render(
            request,
            "config_manage/config_manage.html",
            context={
                "object": device,
                "config": latest_config,
                "config_template": config_template,
                "rendered_config": rendered_config,
                "config_diff": config_diff,
                "config_blocks": config_blocks,
                "tab": self.tab,
            },
        )

    def split_config_into_blocks(self, config_output):
        block_delimiters = ['interface', 'router', 'line', 'vlan', 'access-list']  # Примеры ключевых слов для разделения блоков
        blocks = []
        current_block = {"title": "", "content": "", "editable": False}

        lines = config_output.splitlines()
        for line in lines:
            for delimiter in block_delimiters:
                if line.startswith(delimiter):
                    if current_block["content"]:
                        blocks.append(current_block)
                    current_block = {
                        "title": line,
                        "content": line + "\n",
                        "editable": self.is_block_editable(line)
                    }
                    break
            else:
                current_block["content"] += line + "\n"

        if current_block["content"]:
            blocks.append(current_block)

        return blocks

    def is_block_editable(self, block_title):
        editable_keywords = ['interface', 'router']
        for keyword in editable_keywords:
            if keyword in block_title:
                return True
        return False

    def post(self, request, pk, block_title=None):
        device = Device.objects.get(pk=pk)
        latest_config = DeviceConfig.objects.filter(device=device).order_by('-created_at').first()

        if not latest_config:
            return JsonResponse({"success": False, "error": "No configuration available to edit."})

        block_content = request.POST.get("block_content", "")

        config_output = self.update_block_in_config(latest_config.config_output, block_title, block_content)

        DeviceConfig.objects.create(
            device=device,
            config_output=config_output
        )

        return JsonResponse({"success": True, "block_title": block_title, "updated_content": block_content})

    def update_block_in_config(self, config_output, block_title, block_content):
        lines = config_output.splitlines()
        new_config = []
        in_block = False

        for line in lines:
            if line.startswith(block_title):
                in_block = True
                new_config.append(block_content)
            elif in_block and any(line.startswith(d) for d in ['interface', 'router', 'line', 'vlan', 'access-list']):
                in_block = False
                new_config.append(line)
            elif not in_block:
                new_config.append(line)

        if in_block:
            new_config.append(block_content)

        return "\n".join(new_config)

def device_connect_view(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    if request.method == 'POST':
        form = DeviceConnectionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            method = form.cleaned_data['method']
            poll_frequency = form.cleaned_data['poll_frequency']

            poll_config, created = DevicePollConfig.objects.get_or_create(device=device)
            poll_config.poll_frequency = poll_frequency
            poll_config.save()

            manager = DeviceConnectionManager(device, username, password)
            connection, status = manager.connect(method)

            if connection:
                command = "show running-config"
                output = manager.execute_command(connection, command)

                manager.close_connection(connection)

                DeviceConfig.objects.create(
                    device=device,
                    config_output=output
                )

                poll_config.last_polled_at = timezone.now()
                poll_config.last_poll_status = "Success"
                poll_config.last_poll_error = ""
                poll_config.save()

                return render(
                    request,
                    "config_manage/tab_example.html",
                    context={
                        'form': form,
                        'device': device,
                        'output': output,
                    }
                )
            else:
                poll_config.last_poll_status = "Failed"
                poll_config.last_poll_error = "Could not connect to device."
                poll_config.save()

                return redirect('dcim:device', pk=device_id)

    else:
        form = DeviceConnectionForm()

    return render(request, 'config_manage/tab_example.html', {'form': form, 'device': device})


