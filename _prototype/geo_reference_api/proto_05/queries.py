from geo_ref_api import ApiSerializer
import json

if __name__ == "__main__":
    queries = [
        {
            "req": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "que": {
                "api_find_group": "admins",
                "api_find_module": "test01",
                "permission_level": 3,
            }
        }, 
        {
            "req": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "que": {
                "api_find_group": "admins",
                "api_find_module": "test11",
                "permission_level": 3,
            }
        }, 
        {
            "req": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "que": {
                "api_find_group": "admins",
                "api_find_module": "test12",
                "permission_level": 3,
            }
        }, 
        {
            "req": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "que": {
                "api_find_group": "admins",
                "api_find_module": "test21",
                "permission_level": 3,
            }
        }, 
        {
            "req": "POST",
            "res": 'table01',
            "usr": "admin",
            "que": {
                "name": "test01", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'table01',
            "usr": "admin",
            "que": {
                "name": "test01", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'table11',
            "usr": "admin",
            "que": {
                "name": "test11",
                "table01_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'table12',
            "usr": "admin",
            "que": {
                "name": "test12",
                "table01_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'table21',
            "usr": "admin",
            "que": {
                "name": "test21",
                "table11_id": 1,
                "table12_id": 1,
            } 
        }, 
        {
            "req": "GET",
            "res": 'table01',
            "usr": "admin",
            "que": {
                "api_nesting": 4,
            }
        }, 
        {
            "req": "GET",
            "res": 'table11',
            "usr": "admin",
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'table12',
            "usr": "admin",
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'groups',
            "usr": "admin",
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'users',
            "usr": "admin",
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'modules',
            "usr": "admin",
            "que": {}
        }, 
        {
            "req": "DELETE",
            "res": 'modules',
            "usr": "admin",
            "que": {
                "api_find_name": "test01",
            }
        }, 
        {
            "req": "DELETE",
            "res": 'table12',
            "usr": "admin",
            "que": {
                "api_find_name": "test12",
            }
        }, 
        {
            "req": "GET",
            "res": 'table21',
            "usr": "admin",
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'table01',
            "usr": "admin",
            "que": {
                "api_nesting": 4, 
            }
        }, 
    ]
    
    api_serial = ApiSerializer()
    
    api_serial.print_api_struct()
     
    for query in queries:
        print (api_serial.serialize(query))
        print ("")