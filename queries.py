from geo_ref_api.serializer import serialize_run

if __name__ == "__main__":
    queries = [
        #{
            #"req": "POST",
            #"res": 'groups',
            #"usr": "admin",
            #"que": {
                #"name": "Группа1", 
            #} 
        #}, 
        #{
            #"req": "POST",
            #"res": 'modules',
            #"usr": "admin",
            #"que": {
                #"name": "Модуль1", 
            #} 
        #}, 
        #{
            #"req": "POST",
            #"res": 'modules',
            #"usr": "admin",
            #"que": {
                #"name": "Модуль2", 
            #} 
        #}, 
        #{
            #"req": "POST",
            #"res": 'groups',
            #"usr": "admin",
            #"que": {
                #"name": "Группа2", 
            #} 
        #}, 
        #{
            #"req": "POST",
            #"res": 'users',
            #"usr": "admin",
            #"que": {
                #"name": "Миша", 
                #"group_id": 1,
            #} 
        #}, 
        #{
            #"req": "POST",
            #"res": 'users',
            #"usr": "admin",
            #"que": {
                #"name": "Ваня", 
                #"group_id": 1,
            #} 
        #}, 
        #{
            #"req": "POST",
            #"res": 'users',
            #"usr": "admin",
            #"que": {
                #"name": "Петя", 
                #"group_id": 2,
            #} 
        #}, 
        #{
            #"req": "GET",
            #"res": 'groups',
            #"usr": "admin",
            #"que": {}
        #}, 
        #{
            #"req": "GET",
            #"res": 'modules',
            #"usr": "admin",
            #"que": {}
        #}, 
        #{
            #"req": "GET",
            #"res": 'modules_permissions',
            #"usr": "admin",
            #"que": {}
        #}, 
        #{
            #"req": "GET",
            #"res": 'modules_permissions',
            #"usr": "admin",
            #"que": {
                #"group": "Группа2",
                #"module": "Модуль2",
            #}
        #}, 
        #{
            #"req": "PUT",
            #"res": 'groups',
            #"usr": "admin",
            #"que": {
                #"api_find_name": "Группа2",
                #"name": "Группа Обречённых",
            #}
        #}, 
        #{
            #"req": "GET",
            #"res": 'users',
            #"usr": "admin",
            #"que": {
                #"api_nesting": 1,
            #}
        #}, 
        #{
            #"req": "DELETE",
            #"res": 'groups',
            #"usr": "admin",
            #"que": {
                #"api_find_name": "Группа Обречённых",
            #}
        #}, 
        #{
            #"req": "GET",
            #"res": 'groups',
            #"usr": "admin",
            #"que": {}
        #}, 
        {
            "req": "DELETE",
            "res": 'users',
            "usr": "admin",
            "que": {
                "api_find_group": "Группа1",
            }
        }, 
        {
            "req": "GET",
            "res": 'users',
            "usr": "admin",
            "que": {}
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
            #"usr": "admin",
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'table12',
            #"usr": "admin",
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
    ]
    
    for query in queries:
        print (serialize_run(query))
        print ("")