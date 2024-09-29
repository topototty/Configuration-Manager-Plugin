from netbox.plugins import PluginConfig

from .version import __version__

class ConfigManagePlugin(PluginConfig):
    name = "config_manage"
    verbose_name = "Configuration Management"
    version = __version__
    required_settings = []
    default_settings = {}

config = ConfigManagePlugin
