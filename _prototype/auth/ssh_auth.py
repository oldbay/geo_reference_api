import paramiko
import sys

host = '127.0.0.1'
port = 22

def paramiko_auth(user, passw):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            port=port, 
            username=user,
            password=passw,
        )
    except paramiko.ssh_exception.AuthenticationException:
        return False
    else:
        stdin, stdout, stderr = client.exec_command('groups')
        data = stdout.readlines()[0].split('\n')[0]
        client.close()
        return data.split(' ')

if __name__ == "__main__":
    user = sys.argv[1]
    passw = sys.argv[2]
    print(paramiko_auth(user, passw))