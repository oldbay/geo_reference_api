from geo_ref_api.auth_processing import AuthProcessing

auth = AuthProcessing()
print (auth.get_auth('sysadmin', password='sysadmin'))
print (auth.get_auth('guest', password='guest'))
print (auth.get_auth('bla', password='bla'))
print (auth.get_auth('bla', passwords='bla'))
print (auth.auth_args)