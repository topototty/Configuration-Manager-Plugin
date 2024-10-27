from __future__ import absolute_import, unicode_literals
from netbox.plugins import PluginConfig
from .celery import app as celery_app
from .version import __version__

class ConfigManagePlugin(PluginConfig):
    name = "config_manage"
    verbose_name = "Configuration Management"
    version = __version__
    required_settings = []
    default_settings = {}

config = ConfigManagePlugin

__all__ = ('celery_app',)
