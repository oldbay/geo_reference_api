import paramiko
import sys

from geo_ref_api import ApiAuthConstructor, auth_args_test 

########################################################################
class ApiAuth(ApiAuthConstructor):
    """
    SSH Auth module
    """
   
    auth_args = {
        "password": str,
    }
        
    #----------------------------------------------------------------------
    def __init__(self, url, port):
        """Constructor"""
        
        self.__auth_url__ = url
        self.__auth_port__ = port        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )
    
    @auth_args_test
    def auth(self, username, **kwargs):
        try:
            self.client.connect(
                hostname=self.__auth_url__,
                port=self.__auth_port__, 
                username=username,
                password=kwargs['password'],
            )
        except paramiko.ssh_exception.AuthenticationException:
            return False
        else:
            stdin, stdout, stderr = self.client.exec_command('groups')
            data = stdout.readlines()[0].split('\n')[0]
            self.client.close()
            return data.split(' ')