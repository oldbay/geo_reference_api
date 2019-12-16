import json
import requests
import time

admin_user = 'sysadmin'
admin_pass = 'sysadmin'
admin_group = 'sysadmins'

guest_user = 'guest'
guest_pass = 'guest'
guest_group = 'guests'

RPem = './key/rest.pem'

host_url = 'https://localhost:5444/{}'
req_mets = {
    "GET": requests.get,
    "POST": requests.post,
    "PUT": requests.put,
    "DELETE": requests.delete,
    "OPTIONS": requests.options,
}

def auth(username, password):
    obj = req_mets['GET']
    url = host_url.format('auth')
    data = {
        "username": username,
        "password": password,
    }
    response = obj(
        url,
        verify=RPem, 
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}, 
    )
    return response.status_code, response.json()
    

def req_start(queries, headers):
    for req in queries:
        if isinstance(req, dict):
            obj = req_mets[req['met']]
            url = host_url.format(req['res'])
            data = req['req']
            response = obj(
                url,
                verify=RPem, 
                data=json.dumps(data),
                headers=headers, 
            )
            print ()
            print ('{}:'.format(req['met']), '/{}'.format(req['res']))
            print ("REQUEST:")
            print (
                json.dumps(
                    data,
                    sort_keys=True, 
                    indent=4,
                    separators=(',', ':'), 
                    ensure_ascii=False
                )
            )
            print ("STATUS CODE:", response.status_code)
            if response.status_code != 204:
                print ("RESPONSE:")
                print (
                    json.dumps(
                        response.json(),
                        sort_keys=True, 
                        indent=4,
                        separators=(',', ':'), 
                        ensure_ascii=False
                    )
                )
        else:
            for _ in range(3): print ()
            print ("DESCRIPTION:")
            print ("-"*90)
            print (req)
            print ("-"*90)


if __name__ == "__main__":
    queries = [
        """
        посмотрим всю структуру ресурсов api
        """,
        {
            "met": "OPTIONS",
            "res": '',
            "req": {}
        },
        """
        посмотрим информацию о распределении ресурсов api по модулям, зависимости, доки
        """,
        {
            "met": "GET",
            "res": 'struct_info',
            "req": {}
        },
        """
        посмотрим структуру ресурса api аудентификация 
        """,
        {
            "met": "OPTIONS",
            "res": 'auth',
            "req": {}
        },
        """
        пройдём аутентификацию, получим заголовок с тикетом для пользователя
        """,
        {
            "met": "GET",
            "res": 'auth',
            "req": {
                "username": admin_user,
                "password": admin_pass,
            }
        },
        """
        посмотрим информацию о аутентифицированном пользователе
        """,
        {
            "met": "GET",
            "res": 'user_info',
            "req": {}
        },
        """
        посмотрим ресурсы api доступные для данного пользователя
        пользователь admin дефолтный - у него послный доступ на все ресурсы модуля base
        но ему пока недоступны все модули test<номер>
        """,
        {
            "met": "OPTIONS",
            "res": '',
            "req": {
                "filter": {
                    "api_user": "admin",
                },
            }
        },
        """
        посмотрим права групп(ы) пользователя на модули
        права выставляются числовым кодрм 0-4, сейчас
        0: [],
        1: ["GET"],
        2: ["GET", "PUT"],
        3: ["GET", "POST", "PUT", "DELETE"]
        количество уровней и состав методов http запросов выставляется в конфиге
        метод OPTIONS по умолчанию открыт для всех
        """,
        {
            "met": "GET",
            "res": 'modules_permissions',
            "req": {
                "filter": {
                    "group": "admins",
                },
            }
        }, 
        """
        дадим пользователю через группу полные права на все модули test<номер>
        """,
        {
            "met": "PUT",
            "res": 'modules_permissions',
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
        """
        теперь работа с ресурсами этих модулей админу доступна, пример:
        """,
        {
            "met": "OPTIONS",
            "res": 'table01',
            "req": {
                "filter": {
                    "api_user": "admin",
                },
            }
        },
        """
        заполним ресурсы данными: 
        """,
        {
            "met": "POST",
            "res": 'table01',
            "req": {
                "data": {
                    "name": "test01", 
                },
            } 
        }, 
        {
            "met": "POST",
            "res": 'table11',
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
            "req": {
                "data": {
                    "name": "test21",
                    "table11_id": 1,
                    "table12_id": 1,
                },
            } 
        },
        """
        посмотрим что получилось 
        """,
        {
            "met": "GET",
            "res": 'table11',
            "req": {}
        }, 
        {
            "met": "GET",
            "res": 'table12',
            "req": {}
        },
        """
        обратим внимание на параметр api_nesting, он показывает на какую глубину 
        возможна рекурсия сериализатора при выполнении запроса
        """,
        {
            "met": "GET",
            "res": 'table01',
            "req": {
                "filter": {
                    "api_nesting": 4,
                }
            }
        }, 
        """
        попробуем повторно создать запись с ием же name для ресурса table01 
        и вызываем исключение целосности 
        """,
        {
            "met": "POST",
            "res": 'table01',
            "req": {
                "data": {
                    "name": "test01", 
                },
            } 
        },
        """
        Создадим группу для непривелегированных пользователей 
        """,
        {
            "met": "POST",
            "res": 'groups',
            "req": {
                "data": {
                    "name": "guests",
                    "auth_name": guest_group,
                }
            }
        }, 
        """
        и зададим ей права на доступ к модулям
        """,
        {
            "met": "PUT",
            "res": 'modules_permissions',
            "req": {
                "filter": {
                    "group": "guests",
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
            "req": {
                "filter": {
                    "group": "guests",
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
            "req": {
                "filter": {
                    "group": "guests",
                    "module": "test12",
                },
                "data": {
                    "permission_level": 3,
                },
            }
        },
        """
        посмотрим структуру API для группы guests 
        """,
        {
            "met": "OPTIONS",
            "res": '',
            "req": {
                "filter": {
                    "api_group": "guests",
                },
            }
        },
    ]
    
    resp_auth = auth(admin_user, admin_pass)
    if resp_auth[0] == 200:
        req_start(queries, resp_auth[-1])
    
    queries = [
        """
        пройдём аутентификацию новым пользователем
        """,
        {
            "met": "GET",
            "res": 'auth',
            "req": {
                "username": guest_user,
                "password": guest_pass,
            }
        },
        """
        Посмотрим информацию о данном пользователе:
        Его раньше не было в базе но в результате аутентификации для него была создана 
        запись пользователя и он был включён в заренее созданныую группу guests, 
        так как сервис аутентификации вернул системную группу с тем же названием 
        для данного пользователя 
        """,
        {
            "met": "GET",
            "res": 'user_info',
            "req": {}
        },
        """
        попробуем добавить разрешённый ресурс пользователю ресурс
        """,
        {
            "met": "POST",
            "res": 'table12',
            "req": {
                "data": {
                    "name": "test12_from_guest",
                    "table01_id": 1,
                },
            } 
        },
        """
        изменим добавленный (разрешённый) ресурс 
        """,
        {
            "met": "PUT",
            "res": 'table12',
            "req": {
                "filter": {
                    "name": "test12_from_guest",
                },
                "data": {
                    "name": "test12_from_guest_new",
                },
            }
        }, 
        """
        удалим добавленный (разрешённый) ресурс
        """,
        {
            "met": "DELETE",
            "res": 'table12',
            "req": {
                "filter": {
                    "name": "test12_from_guest_new",
                },
            },
        }, 
        """
        а теперь попробуем удалить неразрешённый ресурс
        """,
        {
            "met": "DELETE",
            "res": 'table11',
            "req": {
                "filter": {
                    "name": "test11",
                },
            },
        }, 
    ]
    resp_auth = auth(guest_user, guest_pass)
    if resp_auth[0] == 200:
        req_start(queries, resp_auth[-1])
    
    queries = [
        """
        Приложение:
        Работа с ресурсом modules
        """,
        {
            "met": "GET",
            "res": 'modules',
            "req": {}
        }, 
        {
            "met": "PUT",
            "res": 'modules',
            "req": {
                "filter": {
                    "name": "test12",
                },
                "data": {
                    "delete": True,
                }
            },
        }, 
        
    ]
    resp_auth = auth(admin_user, admin_pass)
    if resp_auth[0] == 200:
        req_start(queries, resp_auth[-1])
