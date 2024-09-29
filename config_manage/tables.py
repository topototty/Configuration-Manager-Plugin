import django_tables2 as tables
from netbox.tables import NetBoxTable
from .models import DeviceConnectionLog

class DeviceConnectionLogTable(NetBoxTable):
    connection_time = tables.DateTimeColumn(verbose_name='Connection Time')
    connection_status = tables.Column(verbose_name='Connection Status')
    hostname = tables.Column(verbose_name='Hostname')
    connection_method = tables.Column(verbose_name='Connection Method')

    class Meta(NetBoxTable.Meta):
        model = DeviceConnectionLog
        fields = ('connection_time', 'connection_status', 'hostname', 'connection_method')
        default_columns = ('connection_time', 'connection_status', 'hostname', 'connection_method')