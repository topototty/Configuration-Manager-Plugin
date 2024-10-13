from netmiko import ConnectHandler

class DeviceConnectionManager:
    def __init__(self, device, username, password, secret=None):
        self.device = device
        self.username = username
        self.password = password
        self.secret = secret or password

    def connect(self, connection_method):
        ip_address = str(self.device.primary_ip4.address.ip)  # This extracts only the IP part

        device_params = {
            "device_type": "cisco_ios",  # Adjust based on your device type
            "host": ip_address,  # Use the extracted IP address
            "username": self.username,  # Use the username provided by the user
            "password": self.password,  # Use the password provided by the user
            "secret": self.secret,  # Include the secret for enable mode
        }

        if connection_method == "telnet":
            device_params["device_type"] = "cisco_ios_telnet"

        try:
            net_connect = ConnectHandler(**device_params)
            net_connect.enable()  # Enter enable mode
            return net_connect, "Connected"
        except Exception as e:
            return None, f"Connection failed: {e}"

    def execute_command(self, connection, command):
        try:
            output = connection.send_command(command)
            return output
        except Exception as e:
            return f"Failed to execute command: {e}"

    def close_connection(self, connection):
        connection.disconnect()

