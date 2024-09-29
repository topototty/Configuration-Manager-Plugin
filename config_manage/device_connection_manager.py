import paramiko
import telnetlib
import time

class DeviceConnectionManager:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def connect_ssh(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(self.ip, username=self.username, password=self.password)
            return ssh_client, "Connected"
        except Exception as e:
            return None, f"Connection failed: {e}"

    def execute_ssh_command(self, ssh_client, command):
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode('utf-8')
        return output

    def close_ssh(self, ssh_client):
        ssh_client.close()

    def connect_telnet(self):
        try:
            telnet_client = telnetlib.Telnet(self.ip)
            telnet_client.read_until(b"login: ")
            telnet_client.write(self.username.encode('ascii') + b"\n")
            telnet_client.read_until(b"Password: ")
            telnet_client.write(self.password.encode('ascii') + b"\n")
            return telnet_client, "Connected"
        except Exception as e:
            return None, f"Connection failed: {e}"

    def execute_telnet_command(self, telnet_client, command):
        telnet_client.write(command.encode('ascii') + b"\n")
        time.sleep(1)
        output = telnet_client.read_very_eager().decode('ascii')
        return output

    def close_telnet(self, telnet_client):
        telnet_client.close()
