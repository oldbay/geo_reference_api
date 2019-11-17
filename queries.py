
from sqlalchemy.orm import sessionmaker
import json

from model import engine
from model import Users, Groups

def_nesting = 0


Session = sessionmaker(bind=engine)
session = Session()

def post(table, qdict):
    que = table.new_from_json(json.dumps(qdict))
    session.add(que)
    session.commit()

def get(table, qdict):

    max_nesting = qdict.get('max_nesting', def_nesting)
    if max_nesting != def_nesting: del(qdict['max_nesting'])
    
    table_query = session.query(table)
    find_list = table_query.filter_by(**qdict)

    result = []
    for find_obj in find_list:
        result.append(
            json.loads(
                find_obj.to_json(max_nesting=max_nesting)
            )
        )
    return result

def qrun(queries):
    for q in queries:
        print (
            q["opt"](q["tab"], q["que"])
        )

if __name__ == "__main__":
    queries = [
        {
            "opt": post,
            "tab": Groups,
            "que": {
                "name": "Группа1", 
            } 
        }, 
        {
            "opt": post,
            "tab": Groups,
            "que": {
                "name": "Группа2", 
            } 
        }, 
        {
            "opt": post,
            "tab": Users,
            "que": {
                "name": "Миша", 
                "group_id": 1,
            } 
        }, 
        {
            "opt": post,
            "tab": Users,
            "que": {
                "name": "Ваня", 
                "group_id": 1,
            } 
        }, 
        {
            "opt": post,
            "tab": Users,
            "que": {
                "name": "Петя", 
                "group_id": 2,
            } 
        }, 
        #{
            #"opt": get,
            #"tab": Users,
            #"que": {
                #"id": 1,
            #}
        #}, 
        #{
            #"opt": get,
            #"tab": Users,
            #"que": {
                #"name": "Петя",
            #}
        #}, 
        {
            "opt": get,
            "tab": Users,
            "que": {
                "max_nesting": 1,
            }
        }, 
        {
            "opt": get,
            "tab": Groups,
            "que": {
                "max_nesting": 2,
            }
        }, 
    ]
    qrun(queries)
