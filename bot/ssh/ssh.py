import time
import paramiko


class SSH:
    def __init__(
            self,
            host: str = 'localhost',
            user: str = 'root',
            password: str = '',
            port: int = 22,
            max_bytes: int = 60000,
            small_pause: int = 1,
            max_output: int = 3000
    ):
        self.host = host
        self.user = user
        self.secret = password
        self.port = port
        self.ssh = None

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.max_bytes = max_bytes
        self.small_pause = small_pause
        self.ssh_output = ""
        self.max_output_len = max_output

    def connect(self):
        try:
            if self.get_status():
                self.client.close()

            self.client.connect(
                hostname=self.host,
                username=self.user,
                password=self.secret,
                port=self.port,
                look_for_keys=False,
                allow_agent=False,
            )
            self.ssh = self.client.invoke_shell()
            self.ssh_output = self.ssh.recv(self.max_bytes).decode("utf-8")
            return self.ssh_output
        except:
            return None

    def close(self):
        self.client.close()

    def get_status(self):
        if self.ssh is None: return False
        return self.ssh.get_transport().is_active()

    def exec_command(self, command):
        self.ssh.send(f"{command}\n")
        time.sleep(self.small_pause)
        output = self.ssh.recv(self.max_bytes).decode("utf-8")
        self.ssh_output += output
        self.ssh_output = ('...' + self.ssh_output[:4000]) if len(
            self.ssh_output) > self.max_output_len else self.ssh_output
        return self.ssh_output
