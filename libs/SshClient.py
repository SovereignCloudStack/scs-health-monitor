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

    def test_internet_connectivity(self, domain='google.com'):
        command = f"ping -c 5 {domain}"
        try:
            output = self.execute_command(command)

            # Check for packet loss in the output
            packet_loss_percentage = self.parse_packet_loss(output)
            if packet_loss_percentage == 100:
                raise Exception(f"100% packet loss detected to {domain}")
        
            print(f"Internet connectivity test passed for server {self.host}, Output: {output}")
        except Exception as e:
            print(f"Failed to test internet connectivity for server {self.host}\nError --> {e}")
            raise

    def install_ping(self):
        command = "sudo apt-get update -y && sudo apt-get install -y iputils-ping"
        self.execute_command(command, True)

    def print_working_directory(self):
        command = "pwd"
        directory = self.execute_command(command)
        print(f"Current working directory on server {self.host}: {directory}")
    
    def parse_packet_loss(self, output):
    # Parse the output to find the packet loss percentage
        lines = output.split('\n')
        for line in lines:
            if "packet loss" in line:
                packet_loss_str = line.split(',')[2].strip().split()[0]
                packet_loss_percentage = int(packet_loss_str[:-1])  # Extracting the percentage value
                return packet_loss_percentage
        return None  # If packet loss percentage not found

    