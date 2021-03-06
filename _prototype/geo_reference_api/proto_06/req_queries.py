import json
import requests
import jwt

from geo_ref_api import config

host_url = 'http://127.0.0.1:5444/{}'
secret_key = config.AuthSecretKey
req_mets = {
    "GET": requests.get,
    "POST": requests.post,
    "PUT": requests.put,
    "DELETE": requests.delete,
    "OPTIONS": requests.options,
}

def req_start(queries):
    for req in queries:
        obj = req_mets[req['met']]
        url = host_url.format(req['res'])
        data = req['req']
        ticket = jwt.encode(
            {'username': req['usr']},
            secret_key,
            algorithm='HS256'
        )
        headers = {
            'Content-Type': 'application/json', 
            'ticket': ticket,
        }
        response = obj(url, data=json.dumps(data), headers=headers)
        print ()
        print (req['met'], req['res'], data)
        if response.status_code == 204:
            print(response.status_code, response.text)
        else:
            print(response.status_code)
            print (
                json.dumps(
                    response.json(),
                    sort_keys=True, 
                    indent=4,
                    separators=(',', ':'), 
                    ensure_ascii=False
                )
            )


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
        {
            "met": "OPTIONS",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {}
        }, 
        {
            "met": "OPTIONS",
            "res": 'modules_permissions',
            "usr": "admin",
            "req": {
                "filter": {
                    "api_user": "guest",
                },
            }
        }, 
        {
            "met": "OPTIONS",
            "res": 'table01',
            "usr": "admin",
            "req": {
                "filter": {
                    "api_user": "guest",
                },
            }
        }, 
        {
            "met": "OPTIONS",
            "res": 'table12',
            "usr": "admin",
            "req": {
                "filter": {
                    "api_user": "guest",
                },
            }
        }, 
        {
            "met": "OPTIONS",
            "res": '',
            "usr": "admin",
            "req": {
                "filter": {
                    "api_user": "admin",
                },
            }
        }, 
        {
            "met": "OPTIONS",
            "res": '',
            "usr": "admin",
            "req": {
                "filter": {
                    "api_user": "guest",
                },
            }
        }, 
    ]
    
    req_start(queries)