from geo_ref_api.serializer import qrun

if __name__ == "__main__":
    queries = [
        {
            "req": "POST",
            "res": 'groups',
            "que": {
                "name": "Группа1", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'modules',
            "que": {
                "name": "Модуль1", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'modules',
            "que": {
                "name": "Модуль2", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'groups',
            "que": {
                "name": "Группа2", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'users',
            "que": {
                "name": "Миша", 
                "group_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'users',
            "que": {
                "name": "Ваня", 
                "group_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'users',
            "que": {
                "name": "Петя", 
                "group_id": 2,
            } 
        }, 
        {
            "req": "GET",
            "res": 'groups',
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'modules',
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'modules_permissions',
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'modules_permissions',
            "que": {
                "group": "Группа2",
                "module": "Модуль2",
            }
        }, 
        {
            "req": "PUT",
            "res": 'groups',
            "que": {
                "api_find_name": "Группа2",
                "name": "Группа Обречённых",
            }
        }, 
        {
            "req": "GET",
            "res": 'users',
            "que": {
                "api_nesting": 1,
            }
        }, 
        #{
            #"req": "DELETE",
            #"res": 'groups',
            #"que": {
                #"api_find_name": "Группа Обречённых",
            #}
        #}, 
        #{
            #"req": "GET",
            #"res": 'groups',
            #"que": {}
        #}, 
        {
            "req": "DELETE",
            "res": 'users',
            "que": {
                "api_find_group": "Группа1",
            }
        }, 
        {
            "req": "GET",
            "res": 'users',
            "que": {}
        }, 
        {
            "req": "POST",
            "res": 'table01',
            "que": {
                "name": "test01", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'table11',
            "que": {
                "name": "test11",
                "table01_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'table12',
            "que": {
                "name": "test12",
                "table01_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'table21',
            "que": {
                "name": "test21",
                "table11_id": 1,
                "table12_id": 1,
            } 
        }, 
        {
            "req": "GET",
            "res": 'table01',
            "que": {
                "api_nesting": 4,
            }
        }, 
        {
            "req": "GET",
            "res": 'table11',
            "que": {}
        }, 
        {
            "req": "GET",
            "res": 'table12',
            "que": {}
        }, 
    ]
    qrun(queries)