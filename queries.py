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
    ]
    qrun(queries)