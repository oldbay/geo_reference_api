import os
import imp
import importlib
import datetime
import jwt

from sqlalchemy.orm import sessionmaker

from . import config
from .modules_factory import create_engine_db
from .api_modules.base import Users, Groups, UsersGroups

import logging
import logging.config
logging.config.dictConfig(config.Logging)
logger = logging.getLogger("auth_processing")


########################################################################
class AuthProcessing(object):
    """
    Auth Processing Class
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        # import auth module from config
        imp_module = config.AuthModule['module']
        if os.path.isfile(imp_module):
            self.auth_module = imp.load_source("_", imp_module)
        else:
            self.auth_module = importlib.import_module(imp_module)
        
        self.auth_obj = self.auth_module.ApiAuth(
            **config.AuthModule['args']
        )
        
        # add options args from auth module
        self.auth_args = {
            key:self.auth_obj.auth_args[key].__name__
            for key
            in self.auth_obj.auth_args
        }
        self.auth_args.update({
            "username": str.__name__,
        })
        
        # session
        self.engine = create_engine_db('ref')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def get_auth(self, username, *args, **kwargs):
       
        try: 
            result_auth = self.auth_obj(username, *args, **kwargs)
        except Exception as err:
            all_err = "Auth module '{0}' is not worked, error: '{1}'".format(
                config.AuthModule['module'], 
                err,
            ) 
            logger.error(all_err)
            return 500, {"error": all_err}
            
        if result_auth:
            users_query = self.session.query(Users)
            groups_query = self.session.query(Groups)
            user_groups_query = self.session.query(UsersGroups)

            all_groups = []
            for group_obj in groups_query.all():
                all_groups.append(group_obj.auth_name)

            user_id = None
            user_groups = []
            for user_obj in users_query.filter_by(auth_name=username):
                user_id = user_obj.id
                api_user = user_obj.name
                for user_grop_obj in user_obj.groups:
                    for group_obj in groups_query.filter_by(id=user_grop_obj.group_id):
                        user_groups.append(group_obj.auth_name)
            if not user_id:
                new_user = Users()
                new_user.name = username
                new_user.auth_name = username
                new_user.auto_create = True
                self.session.add(new_user)
                self.session.commit()
                for user_obj in users_query.filter_by(auth_name=username):
                    user_id = user_obj.id
                    api_user = user_obj.name

            grp2usr = set(all_groups).intersection(set(user_groups))
            grp2grp = set(all_groups).intersection(set(result_auth))
           
            # add user to group
            group_ids = []
            for grp in grp2grp - grp2usr:
                for group_obj in groups_query.filter_by(auth_name=grp):
                    group_ids.append(group_obj.id)
            for group_id in group_ids:
                new_user_group = UsersGroups()
                new_user_group.user_id = user_id
                new_user_group.group_id = group_id
                new_user_group.auto_create = True
                self.session.add(new_user_group)
                self.session.commit()
                
            # del user from group
            group_ids = []
            for grp in grp2usr - grp2grp:
                for group_obj in groups_query.filter_by(auth_name=grp):
                    group_ids.append(group_obj.id)
            for group_id in group_ids:
                for user_group_obj in user_groups_query.filter_by(
                                                                  group_id=group_id, 
                                                                  user_id=user_id, 
                                                                  auto_create=True): 
                    self.session.delete(user_group_obj)
                    self.session.commit()
           
            # create jwt ticket
            ticket_data = {config.JwtUserKey: api_user}
            if config.JwtTimeout:
                #timeout = datetime.datetime.utcnow() + datetime.timedelta(
                    #seconds=config.JwtTimeout
                #)
                timeout = datetime.datetime.now()
                ticket_data.update({
                    "exp": int(timeout.timestamp())
                })
                
            ticket = jwt.encode(
                ticket_data,
                config.JwtSecretKey,
                algorithm=config.JwtAlgo
            )
            return 200, {
                "Content-Type": "application/json", 
                "ticket": ticket,
            }
        else:
            return 401, {"error": "Authorization field"}
    