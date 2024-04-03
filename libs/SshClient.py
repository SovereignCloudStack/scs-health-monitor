import paramiko

class SshClient:
    def __init__(self, host, username, key_path):
        self.host = host
        self.username = username
        self.client = paramiko.SSHClient()
        policy = paramiko.AutoAddPolicy()
        self.client.set_missing_host_key_policy(policy)
        self.private_key = paramiko.RSAKey.from_private_key_file(key_path)

    def log(self, level, message):
        if self.logger and level >= self.min_log_level:
            self.logger.log(level, message)

    def execute_command(self, command, ignore_error_output=False):
        try:
            _stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            err_output = stderr.read().decode().strip()

            if err_output and not ignore_error_output:
                raise Exception(err_output)
            
            return output
        except Exception as e:
            raise RuntimeError(f"Failed to execute command '{command}' on server {self.host}: {e}")
    
    def connect(self):
        self.client.connect(self.host, username=self.username, pkey=self.private_key)

    def close_conn(self):
        self.client.close()

    def test_internet_connectivity(self):
        command = "ping -c 10 google.com"
        try:
            output = self.execute_command(command)
            print(f"Internet connectivity test passed for server {self.host}, Output: {output}")
        except Exception as e:
            print(f"Failed to test internet connectivity for server {self.host}\nError-->{e}")

    def install_ping(self):
        command = "sudo apt-get update -y && sudo apt-get install -y iputils-ping"
        self.execute_command(command, True)

    def print_working_directory(self):
        command = "pwd"
        directory = self.execute_command(command)
        print(f"Current working directory on server {self.host}: {directory}")

    