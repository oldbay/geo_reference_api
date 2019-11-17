
from sqlalchemy.orm import sessionmaker

from model import engine
from model import User

Session = sessionmaker(bind=engine)
session = Session()

def post(table, qdict):
    que = table.new_from_dict(qdict)
    session.add(que)
    session.commit()

def get(table, qdict):
    find = table.query.get(**qdict)
    result = find.to_dict()
    return result

def qrun(queries):
    for q in queries:
        q["opt"](q["tab"], q["que"])

if __name__ == "__main__":
    queries = [
        {
            "opt": post,
            "tab": User,
            "que": {
                "id": 1,"name": "Misha"
            } 
        }, 
        {
            "opt": post,
            "tab": User,
            "que": {
                "id": 2,"name": "Vanya", 
            } 
        }, 
        {
            "opt": post,
            "tab": User,
            "que": {
                "id": 3,"name": "Petya", 
            } 
        }, 
        #{
            #"opt": get,
            #"tab": User,
            #"que": {}
        #}, 
    ]
    qrun(queries)
