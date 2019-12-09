from geo_ref_api.auth_processing import AuthProcessing

auth = AuthProcessing()
print (auth.get_auth('sysadmin','sysadmin'))
print (auth.get_auth('guest', 'guest'))
print (auth.get_auth('bla', 'bla'))