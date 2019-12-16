#!/usr/bin/python3

from geo_ref_api import RestApi
from geo_ref_api import config

RKey = './key/rest.key'
RCert = './key/rest.cert'

if __name__ == "__main__":
    context = (RCert, RKey)
    rest = RestApi()
    rest.run_test_server(
        host='0.0.0.0',
        port=5444,
        debug=True,
        ssl_context=context, 
    )
