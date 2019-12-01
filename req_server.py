from geo_ref_api import RestApi
from geo_ref_api import config

if __name__ == "__main__":
    rest = RestApi()
    rest.run_test_server(
        host='0.0.0.0',
        port=5444,
        debug=True
    )