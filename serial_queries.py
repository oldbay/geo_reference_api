from geo_ref_api import ApiSerializer
import json

if __name__ == "__main__":
    queries = [
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "group": "admins",
                    "module": "test01",
                },
                "data": {
                    "permission_level": 3,
                },
            }
        }, 
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "group": "admins",
                    "module": "test11",
                },
                "data": {
                    "permission_level": 3,
                },
            }
        }, 
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "group": "admins",
                    "module": "test12",
                },
                "data": {
                    "permission_level": 3,
                },
            }
        }, 
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "group": "admins",
                    "module": "test21",
                },
                "data": {
                    "permission_level": 3,
                },
            }
        }, 
        {
            "met": "POST",
            "res": 'table01',
            "usr": "admin",
            "req": {
                "data": {
                    "name": "test01", 
                },
            } 
        }, 
        {
            "met": "POST",
            "res": 'table01',
            "usr": "admin",
            "req": {
                "data": {
                    "name": "test01", 
                },
            } 
        }, 
        {
            "met": "POST",
            "res": 'table11',
            "usr": "admin",
            "req": {
                "data": {
                    "name": "test11",
                    "table01_id": 1,
                },
            } 
        }, 
        {
            "met": "POST",
            "res": 'table12',
            "usr": "admin",
            "req": {
                "data": {
                    "name": "test12",
                    "table01_id": 1,
                },
            } 
        }, 
        {
            "met": "POST",
            "res": 'table21',
            "usr": "admin",
            "req": {
                "data": {
                    "name": "test21",
                    "table11_id": 1,
                    "table12_id": 1,
                },
            } 
        }, 
        {
            "met": "GET",
            "res": 'table01',
            "usr": "admin",
            "req": {
                "filter": {
                    "api_nesting": 4,
                }
            }
        }, 
        {
            "met": "GET",
            "res": 'table11',
            "usr": "admin",
            "req": {}
        }, 
        {
            "met": "GET",
            "res": 'table12',
            "usr": "admin",
            "req": {}
        }, 
        {
            "met": "GET",
            "res": 'groups',
            "usr": "admin",
            "req": {}
        }, 
        {
            "met": "GET",
            "res": 'users',
            "usr": "admin",
            "req": {}
        }, 
        {
            "met": "GET",
            "res": 'modules',
            "usr": "admin",
            "req": {}
        }, 
        {
            "met": "DELETE",
            "res": 'modules',
            "usr": "admin",
            "req": {
                "filter": {
                    "name": "test01",
                }
            }
        }, 
        {
            "met": "DELETE",
            "res": 'table12',
            "usr": "admin",
            "req": {
                "filter": {
                    "name": "test12",
                }
            }
        }, 
        {
            "met": "GET",
            "res": 'table21',
            "usr": "admin",
            "req": {}
        }, 
        {
            "met": "GET",
            "res": 'table01',
            "usr": "admin",
            "req": {
                "filter": {
                    "api_nesting": 4,
                }
            }
        }, 
        {
            "met": "POST",
            "res": 'groups',
            "usr": "admin",
            "req": {
                "data": {
                    "name": "guest",
                }
            }
        }, 
        {
            "met": "POST",
            "res": 'users',
            "usr": "admin",
            "req": {
                "data": {
                    "name": "guest",
                    "group_id": 2,
                }
            }
        }, 
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "group": "guest",
                    "module": "test01",
                },
                "data": {
                    "permission_level": 1,
                },
            }
        }, 
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "group": "guest",
                    "module": "test11",
                },
                "data": {
                    "permission_level": 2,
                },
            }
        }, 
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "group": "guest",
                    "module": "test12",
                },
                "data": {
                    "permission_level": 3,
                },
            }
        }, 
    ]
    
    api_serial = ApiSerializer()
    
    api_serial.print_api_modules_struct()
    api_serial.print_api_resources_struct()
     
    for query in queries:
        print (api_serial.serialize(query))
        print ("")
        
    api_serial.print_api_resources_struct('guest')
