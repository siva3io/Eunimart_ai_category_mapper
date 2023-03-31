import os
import uuid
import logging
import datetime

"""
----> Refer this https://github.com/sacrud/sacrud
To understand the queries 
"""
from sacrud.action import CRUD

from app.utils import catch_exceptions
from app.models.service import Service
from app.models.scopes import Scopes
from app.models.services_scopes_map import ServicesScopesMap

from app.models.profiles import Profiles
from app.models.profile_user_account_map import ProfileUserAccountMap
from app.models.profile_scope_action_map import ProfileScopeActionMap
from app import redis
import json 

logger = logging.getLogger(name=__name__)

PERMISSION_MAPPING = {
    "No Access":0,
    "Viewer":1,
    "Editor":2,
    "Admin":3
}

class Profile(object):

    def __init__(self):
        pass

    @catch_exceptions
    def _result_to_json(self, rows, withnested=True):
        converted_rows = []
        for row in rows:
            row = row.to_dict(nested=withnested)
            converted_rows.append(row)
        return converted_rows

    @catch_exceptions
    def _validate_profile(self, profile_name, account_id):
        """
        Chech wether the profile name is already present or not.
        If want to add another validations for profile you can add here
        """
        account_records = ProfileUserAccountMap.smart_query(filters={
            "account_id":account_id    
        }).all()

        if not account_records:
            return {"status":True}
        else:
            for record in account_records:
                if profile_name == record.profile.profile_name:
                    return {"status":False, "error_code":"PROFILE_NAME_EXISTS"}
            

        return {"status":True}

    @catch_exceptions
    def _validate_profile_id(self, profile_id, profile_name=""):

        profile_record = Profiles.smart_query(filters={
            "id":profile_id
        }).first()

        if profile_record:
            if profile_name == profile_record.profile_name :
                return {"status":False, "error_code":"PROFILE_NAME_EXISTS"}
            return {"status":True}
        return { "stauts":False, "error_code":"PROFILE_NOT_FOUND"}

    @catch_exceptions
    def _validate_user_in_profile(self, account_id, user_id):
        if (account_id != "default" and user_id != "default"):
            mapping_obj = ProfileUserAccountMap.smart_query(filters={
                "account_id":account_id,
                "user_id":user_id
            }).first()

            if mapping_obj:
                return {"status":False, "error_code":"USER_ALREADY_LINKED"}
        return {"status":True}

    @catch_exceptions
    def _create_profile_record(self, profile_obj, update_flag=False):
        try:
            if update_flag:
                profile_id = profile_obj["profile_id"]
                
                del profile_obj["profile_id"]

                service_obj = CRUD(Profiles.session, Profiles).update( { "id":profile_id }, profile_obj)
            else:
                service_obj = CRUD(Profiles.session, Profiles).create(profile_obj)
            
            return {"status":True, "message":"Sucessfully created profile"}
        except Exception as e :
            logger.error(e,exc_info=True)
            return {"status":False,"error_code":"PROFILE_ID_EXITS"}

    @catch_exceptions
    def _create_profile_user_account_map(self, mapped_obj, update_flag=False, validate_user=False):
        try:
            if(validate_user):
                validate_mapped_obj_status = self._validate_user_in_profile(mapped_obj["account_id"], mapped_obj["user_id"])
            else:
                validate_mapped_obj_status = {"status":True}
            if validate_mapped_obj_status["status"]:
                mapped_result = CRUD(ProfileUserAccountMap.session,ProfileUserAccountMap).create(mapped_obj)
            
                return {"status":True, "message":"Sucessfully the user is added to profile"}
            else:
                return validate_mapped_obj_status
        except Exception as e:
            logger.error(e,exc_info=True)
            return {"status":False,"error_code":"INCORRECT_MAPPING_FORMAT"}

    @catch_exceptions
    def _create_profile_scope_action_map(self,profile_id, current_user_id, acls, update_flag=False):
        
         
        error_obj = []
        for acl in acls:
            acl["profile_id"] = profile_id
            acl["updated_by"] = current_user_id
            try:
                if update_flag:
                    update_obj = {}
                    update_obj["permission_level"] = acl["permission_level"]
                    update_obj["updated_by"] = current_user_id

                    del acl["permission_level"], acl["updated_by"]

                    query_obj = acl

                    """
                    refer this link https://sacrud.readthedocs.io/en/master/plain_usage.html#update-action
                    """

                    service_obj = CRUD(ProfileScopeActionMap.session, ProfileScopeActionMap).update(query_obj, update_obj)
                else:    
                    service_obj = CRUD(ProfileScopeActionMap.session, ProfileScopeActionMap).create(acl)
            except Exception as e:
                temp_error_obj = {
                        "reason":e
                    }
                error_obj.append(temp_error_obj)
                logger.error(e,exc_info=True)

        return {"status":True}

    @catch_exceptions
    def create_profile(self, profile_obj):
        user_info = profile_obj["user_info"]
        profile_info = profile_obj["data"]["profile_info"]
        acls = profile_obj["data"]["acls"]

        create_user_map = profile_obj["data"]["create_user_map"]

        profile_id = str(uuid.uuid4())
        current_user_id = user_info["current_user_id"]

        validation_result = self._validate_profile( profile_info["profile_name"], user_info["account_id"] )

        if validation_result["status"]:

            profile_info["id"] = profile_id
            profile_info["updated_by"] = current_user_id

            profile_creation_status = self._create_profile_record( profile_info )

            if profile_creation_status:
                acls_map_status = self._create_profile_scope_action_map( profile_id, current_user_id, acls )

                if acls_map_status["status"]:
                    if create_user_map:
                        del user_info["current_user_id"]
                        user_info["updated_by"] = current_user_id
                        user_info["profile_id"] = profile_id
                        user_profile_map_status = self._create_profile_user_account_map(user_info)
                        return user_profile_map_status
                    else:
                        return acls_map_status
                else:
                    return acls_map_status
            else:
                return profile_creation_status
            
        else:
            return validation_result

        return validation_result
        
    @catch_exceptions
    def update_profiles(self, profile_obj):
        user_info = profile_obj["user_info"]
        profile_id = profile_obj["data"]["profile_id"]
        acls = profile_obj["data"]["acls"]

        current_user_id = user_info["current_user_id"]

        profile_validation_status = self._validate_profile_id(profile_id)

        if profile_validation_status["status"]:
            acls_map_status = self._create_profile_scope_action_map( profile_id, current_user_id, acls ,update_flag=True)
            
            return acls_map_status
            
        else:
            return profile_validation_status

    @catch_exceptions
    def update_profile_info(self, profile_obj):
        user_info = profile_obj["user_info"]
        profile_id = profile_obj["data"]["profile_id"]
        profile_info = profile_obj["data"]["profile_info"]

        current_user_id = user_info["current_user_id"]

        profile_update_obj = profile_info

        profile_update_obj["profile_id"] = profile_id
        profile_update_obj["updated_by"] = current_user_id

        profile_validation_status = self._validate_profile_id(profile_id, profile_name=profile_info.get("profile_name",""))

        if profile_validation_status["status"]:
            profile_update_obj_status = self._create_profile_record(profile_update_obj, update_flag=True)
            
            return profile_update_obj_status
            
        else:
            return profile_validation_status

    @catch_exceptions
    def add_user_to_profile(self, profile_map_obj):
        
        user_info = profile_map_obj["user_info"]
        
        profile_map_obj = profile_map_obj["data"]

        account_id = user_info["account_id"]
        user_id = profile_map_obj["user_id"]
        
        user_profile_map_validation_status = self._validate_user_in_profile(account_id, user_id)
    

        return user_profile_map_validation_status

    @catch_exceptions
    def get_profiles(self,account_id):
        
        profiles_map_obj = ProfileUserAccountMap.smart_query(filters={
            "account_id":account_id,
        }).all()

        if profiles_map_obj:
            profiles_map = self._result_to_json(profiles_map_obj)
            
            profiles = {}

            #removing duplicates
            for profile_obj in profiles_map:
                profile = profile_obj["profile"]
                profiles[profile["id"]] = profile

            #reformating the payload
            profiles = [ profiles[key] for key in profiles.keys() ] 

            return { 
                "status":True, "data":profiles
            }
        else:
            return {
                "status":False,
                "error_code":"ACCOUNT_ID_NOT_FOUND"
            }
    
    @catch_exceptions
    def get_profiles_acls(self,profile_id):
        
        profiles_services_map_obj = ProfileScopeActionMap.smart_query(filters={
            "profile_id":profile_id,
        }).all()

        if profiles_services_map_obj:
            profiles_services_map = self._result_to_json(profiles_services_map_obj)

            services = {}
            scopes = {} 

            # reformating the payload required for api response
            for profiles_service in profiles_services_map:
                
                # Unpacking key values.
                service = profiles_service["services"]
                scope = profiles_service["scopes"]

                # Moving these keys and value to scopes dict so that creating payload from frontend becomes easy.  
                
                scope["permission_level"] = profiles_service["permission_level"]
                scope["service_id"] = service["id"]
                scope["scope_id"] = scope["id"]

                # Delete this key to avoid confusion. 
                del scope["id"]
                
                # Adding the service obj to new service obj
                services[service["id"]] = services.get(service["id"], service)
                
                # Adding the scope obj to new scope obj
                scopes[service["service_key"]] =  scopes.get(service["service_key"],[])
                scopes[service["service_key"]].append(scope)

            
            services = [ services[key] for key in services.keys()]
                
        else:
            return {
                "status":False,
                "error_code":"PROFILE_ID_NOT_FOUND"
            }


    @catch_exceptions
    def json_date_time(self,json_obj):
        if isinstance(json_obj, datetime.datetime):
            return json_obj.__str__()
    @catch_exceptions
    def get_user_profile(self,account_id,user_id):
        user_profile = redis.hget(account_id+":"+user_id,"acl")
        if user_profile:
            return { "status":True, "data":json.loads(user_profile.decode('utf-8'))}
        else:
            profiles_user_map_obj = ProfileUserAccountMap.smart_query(filters={
                "account_id":account_id,
                "user_id":user_id
            }).all()
            if(profiles_user_map_obj):
                profiles_user_map = self._result_to_json(profiles_user_map_obj)[0]
                result = self.get_profiles_acls(profiles_user_map['profile_id'])
                redis.hset(account_id+":"+user_id,"acl",json.dumps(result['data'],default = self.json_date_time))
                return result
            else:
                return {"status":False,"error_code":"USER_ACL_NOT_FOUND"}
            
            



    
ProfileOperations = Profile()