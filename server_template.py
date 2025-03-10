import paramiko
import re

# Create an SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# List of server details
servers = [
    {
        'name'    : '',
        'hostname': 'XXX.XXX.XXX.XXX',
        'port': 22,
        'username': 'user',
        'password': 'pass'
    },

]

for server in servers:
    try:
        # Connect to the server
        #ssh.connect(hostname, port, username, password)
        ssh.connect(
            hostname=server['hostname'], 
            port=server['port'], 
            username=server['username'], 
            password=server['password']
        )

        # Run the 'df -h' command
        stdin, stdout, stderr = ssh.exec_command('df -h')
        output = stdout.read().decode()
        error = stderr.read().decode()

        pattern = r'/dev/mapper.*$'
        match = re.search(pattern, output, re.MULTILINE)

        if error:
            print(f"Server name: {server['name']}")
            print(f"Error: {error}")
        else:
            #print(f"Output:\n{output}")
            print(f"Server name: {server['name']}")
            #print(f"Output :\n{output}")
            print(f"Output regex:\n{match.group(0)}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh.close()
