import json
import requests
import time

host_url = 'http://127.0.0.1:5444/{}'
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
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    return response.status_code, response.json()
    

def req_start(queries, headers):
    for req in queries:
        obj = req_mets[req['met']]
        url = host_url.format(req['res'])
        data = req['req']
        response = obj(url, data=json.dumps(data), headers=headers)
        print ()
        print (req['met'], '/{}'.format(req['res']), data)
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
        # посмотрим всю стуктуру ресурсов api
        {
            "met": "OPTIONS",
            "res": '',
            "req": {}
        },
        # посмотрим информацию о распределении ресурсов api по модулям, зависимости, доки
        {
            "met": "GET",
            "res": 'struct_info',
            "req": {}
        },
        # посмотрим структуру ресурса api аудентификация 
        {
            "met": "OPTIONS",
            "res": 'auth',
            "req": {}
        },
        # пройдём аудентификацию, получим заголовок с тикетом для пользователя
        {
            "met": "GET",
            "res": 'auth',
            "req": {
                "username": "sysadmin",
                "password": "sysadmin",
            }
        },
        # посмотрим информацию о аутентифицированном пользователе
        {
            "met": "GET",
            "res": 'user_info',
            "req": {}
        },
        # посмотрим ресурсы api доступные для данного пользователя
        # пользователь admin дефолтный - у него послный доступ на все ресурсы модуля base
        # но ему пока недоступны все модули test<номер>
        {
            "met": "OPTIONS",
            "res": '',
            "req": {
                "filter": {
                    "api_user": "admin",
                },
            }
        },
        # посмотрим права групп(ы) пользователя на модули
        # права выставляются числовым кодрм 0-4, сейчас
        #0: [],
        #1: ["GET"],
        #2: ["GET", "PUT"],
        #3: ["GET", "POST", "PUT", "DELETE"]
        # количество уровней и состав методов http запросов выставляется в конфиге
        # метод OPTIONS по умолчанию открыт для всех
        {
            "met": "GET",
            "res": 'modules_permissions',
            "req": {
                "filter": {
                    "group": "admins",
                },
            }
        }, 
        # дадим пользователю через группу полные права на все модули test<номер>
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
        # теперь работа с ресурсами этих модулей админу доступна, пример:
        {
            "met": "OPTIONS",
            "res": 'table01',
            "req": {
                "filter": {
                    "api_user": "admin",
                },
            }
        },
        # заполним ресурсы данными: 
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
        # посмотрим что получилось 
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
        # обратим внимание на параметр api_nesting, он показывает на какую глубину 
        # возсожна рекурсию сериализатора при выполнении запроса
        {
            "met": "GET",
            "res": 'table01',
            "req": {
                "filter": {
                    "api_nesting": 4,
                }
            }
        }, 
        # попробуем повторно создать запись с ием же name для ресурса table01 
        # и вызываем исключение целосности 
        {
            "met": "POST",
            "res": 'table01',
            "req": {
                "data": {
                    "name": "test01", 
                },
            } 
        },
        # Создадим группу для непривелегированных пользователей 
        {
            "met": "POST",
            "res": 'groups',
            "req": {
                "data": {
                    "name": "guests",
                }
            }
        }, 
        # и зададим ей права на доступ к модулям
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
        # посмотрим структуру API для группы guests 
        {
            "met": "OPTIONS",
            "res": '',
            "req": {
                "filter": {
                    "api_group": "guests",
                },
            }
        },
        
        #{
            #"met": "GET",
            #"res": 'groups',
            #"req": {}
        #}, 
        #{
            #"met": "GET",
            #"res": 'users',
            #"req": {}
        #}, 
        #{
            #"met": "GET",
            #"res": 'modules',
            #"req": {}
        #}, 
        #{
            #"met": "DELETE",
            #"res": 'modules',
            #"req": {
                #"filter": {
                    #"name": "test01",
                #}
            #}
        #}, 
        #{
            #"met": "DELETE",
            #"res": 'table12',
            #"req": {
                #"filter": {
                    #"name": "test12",
                #}
            #}
        #}, 
        #{
            #"met": "GET",
            #"res": 'table21',
            #"req": {}
        #}, 
        #{
            #"met": "GET",
            #"res": 'table01',
            #"req": {
                #"filter": {
                    #"api_nesting": 4,
                #}
            #}
        #}, 
        #{
            #"met": "POST",
            #"res": 'users',
            #"req": {
                #"data": {
                    #"name": "guest",
                #}
            #}
        #}, 
        #{
            #"met": "POST",
            #"res": 'users_groups',
            #"req": {
                #"data": {
                    #"user_id": 2,
                    #"group_id": 2,
                #}
            #}
        #}, 
        #{
            #"met": "GET",
            #"res": 'users',
            #"req": {
                #"filter": {
                    #"name": "guest",
                #}
            #}
        #}, 
        #{
            #"met": "OPTIONS",
            #"res": 'modules_permissions',
            #"req": {}
        #}, 
        #{
            #"met": "OPTIONS",
            #"res": 'modules_permissions',
            #"req": {
                #"filter": {
                    #"api_user": "guest",
                #},
            #}
        #}, 
        #{
            #"met": "OPTIONS",
            #"res": 'table01',
            #"req": {
                #"filter": {
                    #"api_user": "guest",
                #},
            #}
        #}, 
        #{
            #"met": "OPTIONS",
            #"res": 'table12',
            #"req": {
                #"filter": {
                    #"api_user": "guest",
                #},
            #}
        #}, 
        #{
            #"met": "OPTIONS",
            #"res": '',
            #"req": {
                #"filter": {
                    #"api_user": "guest",
                #},
            #}
        #}, 
    ]
    
    resp_auth = auth('sysadmin', 'sysadmin')
    if resp_auth[0] == 200:
        req_start(queries, resp_auth[-1])
    
    queries = [
        # пройдём аудентификацию новым пользователем
        {
            "met": "GET",
            "res": 'auth',
            "req": {
                "username": "sysadmin",
                "password": "sysadmin",
            }
        },
        # Посмотрим информацию о данном пользователе:
        # Его раньше не было в базе но в результате аудентификации для него была создана 
        # запись пользователя и он был включён в заренее созданныую группу guests, 
        # так как сервис аудентификации вернул системную группу с тем же названием 
        # для данного пользователя 
        {
            "met": "GET",
            "res": 'user_info',
            "req": {}
        },
    ]
    resp_auth = auth('guest', 'guest')
    if resp_auth[0] == 200:
        req_start(queries, resp_auth[-1])
