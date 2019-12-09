import paramiko
import sys

from geo_ref_api import ApiAuthConstructor 

########################################################################
class ApiAuth(ApiAuthConstructor):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, url, port):
        """Constructor"""
        
        self. __auth_url__ = url
        self.__auth_port__ = port        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )
    
    def auth(self, username, passwd): 
        try:
            self.client.connect(
                hostname=self.__auth_url__,
                port=self.__auth_port__, 
                username=username,
                password=passwd,
            )
        except paramiko.ssh_exception.AuthenticationException:
            return False
        else:
            stdin, stdout, stderr = self.client.exec_command('groups')
            data = stdout.readlines()[0].split('\n')[0]
            self.client.close()
            return data.split(' ')