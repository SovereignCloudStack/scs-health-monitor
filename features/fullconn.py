import time
import os
import subprocess
import openstack
import openstack.connection
import paramiko
import yaml

def load_env_from_yaml():
    with open("./env.yaml", 'r+') as file:
        env = yaml.safe_load(file)
    return env

context=load_env_from_yaml()

auth_args = {
    'auth_type': context['OS_AUTH_TYPE'],
    'auth_url': context['OS_AUTH_URL'],
    'cloud_name': context['CLOUD_NAME'],
    'region_name': context['OS_REGION_NAME'],
    'application_credential_id': context['OS_APPLICATION_CREDENTIAL_ID'],
    'application_credential_secret': context['OS_APPLICATION_CREDENTIAL_SECRET'],
    'interface':context['OS_INTERFACE']
}


client = openstack.connection.Connection(**auth_args)
print("connected")
######################### Establish OpenStack connection#########################

# Ping function
def myping(host):
    #print(f"ping {host}")
    response = subprocess.run(['ping', '-c', '1', '-w', '1', host], stdout=subprocess.DEVNULL)
    #print(response.returncode)
    if response.returncode == 0:
        print(".", end="", flush=True)
        return 0
    time.sleep(1)
    response = subprocess.run(['ping', '-c', '1', '-w', '3', host], stdout=subprocess.DEVNULL)
    if response.returncode == 0:
        print("o", end="", flush=True)
        return 1
    print("X", end="", flush=True) # success
    return 2

# Collect IPs from OpenStack
def collect_ips():
    print("collecting ips")
    ports = client.network.ports()
    ips = []
    for port in ports:
        for fixed_ip in port.fixed_ips:
            ips.append(fixed_ip['ip_address'])
    return ips

# Remote command execution
def execute_remote_command(host, port, username, private_key_path, command):
    key = paramiko.RSAKey(filename=private_key_path)
    print("key")
    ssh = paramiko.SSHClient()
    print("ssh-client")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("set_missing_host_key_policy")
    ssh.connect(hostname=host, port=port, username=username, pkey=key)
    print("ssh connected")
    stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"from __main__ import fullconntest; fullconntest()\"")
    print("executed fullconn")
    result = stdout.read().decode().strip()
    print(f"result {result}")
    ssh.close()
    print("ssh closed")
    return result

# Main function to perform connectivity check
def fullconntest():
    ips = collect_ips()
    print(f"ips {ips}")
    print(f"VM2VM Connectivity Check ... ({' '.join(ips)})")

    retries = 0
    fails = 0

    for ip in ips:
        result = myping(ip)
        if result == 1:
            retries += 1
        elif result != 2:
            fails += 1

    print(f"retries: {retries}\nfails{fails}")
    return retries + fails

if __name__ == "__main__":
    # Configure your SSH parameters
    FLOATS = ['localhost'] #'213.131.230.89'
    JHNO = 3 # TODO: generic read jump host quantity
    DEFLTUSER = context['DEFLTUSER']
    DATADIR = context['DATADIR']
    KEYPAIRS = [context['KEYPAIRS']]
    REDIRS = [['tcp,22']] # TODO: generic 
    # for jhno in range(JHNO):
    #     for ports in REDIRS[jhno]:
            # port = int(red.split(',')[1])
            
    for ports in REDIRS[0]:
        port = int(ports.split(',')[1])
    
    print(port)

    fullconntest()
  #  command = f"python3 -c \"from __main__ import fullconntest; fullconntest()\""
  #  result = execute_remote_command(FLOATS[0], int(port), DEFLTUSER, os.path.join(DATADIR, KEYPAIRS[0]), command)
    #response = subprocess.run(['ping', '-c', '1', '-w', '3', '10.8.3.210'], stdout=subprocess.DEVNULL)
    #print(f"response {response}")
    #print(f"returncode {response.returncode}")
    #result = execute_remote_command(FLOATS[0], int(port), DEFLTUSER, os.path.join(DATADIR, KEYPAIRS[0]), fullconntest())
    #print(f"FLOATS {FLOATS} DEFLUSER {DEFLTUSER}")
    print("result"+result)

