import django_tables2 as tables
from .models import DeviceConnectionLog
from netbox.tables import NetBoxTable

class DeviceConnectionLogTable(NetBoxTable):
    connection_time = tables.Column(verbose_name="Connection Time")
    connection_status = tables.Column(verbose_name="Status")
    hostname = tables.Column(verbose_name="Hostname")
    connection_method = tables.Column(verbose_name="Connection Method")
    actions = tables.Column(orderable=False)

    class Meta(NetBoxTable.Meta):
        model = DeviceConnectionLog
        fields = ('connection_time', 'connection_status', 'hostname', 'connection_method')
        default_columns = ('connection_time', 'connection_status', 'hostname', 'connection_method')

