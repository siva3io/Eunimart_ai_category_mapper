import logging
from flask import Blueprint, jsonify, request
from app.services.profiles import ProfileOperations

profiles = Blueprint('profiles', __name__)

logger = logging.getLogger(__name__)


@profiles.route('/profiles/create_profile', methods=['POST'])
def create_profiles():

    request_data = request.get_json()
    
    data = ProfileOperations.create_profile(request_data)
    print(data)
    if not data:
        data = {}
    return jsonify(data)

@profiles.route('/profiles/update_profile', methods=['POST'])
def update_profiles():

    request_data = request.get_json()
    
    data = ProfileOperations.update_profiles(request_data)
    return jsonify(data)

@profiles.route('/profiles/update_profile_info', methods=['POST'])
def update_profile_info():

    request_data = request.get_json()
    
    data = ProfileOperations.update_profile_info(request_data)
    return jsonify(data)


@profiles.route("/profiles/add_user_to_profile", methods=['POST'])
def add_user_to_profile():

    request_data = request.get_json()
    
    data = ProfileOperations.add_user_to_profile(request_data)
    print(data)
    if not data:
        data = {}
    return jsonify(data)


@profiles.route('/profiles/get_profiles/<account_id>', methods=['GET'])
def get_profiles(account_id):
    print(account_id)
    data = ProfileOperations.get_profiles(account_id)
    if not data:
        data = {}
    return jsonify(data)

@profiles.route('/profiles/get_profiles_acls/<profile_id>', methods=['GET'])
def get_profiles_acls(profile_id):
    print(profile_id)
    data = ProfileOperations.get_profiles_acls(profile_id)
    if not data:
        data = {}
    return jsonify(data)

@profiles.route('/profiles/get_default_profiles', methods=['GET'])
def get_default_profiles():
    account_id = "default"
    data = ProfileOperations.get_profiles(account_id)
    if not data:
        data = {}
    return jsonify(data)

@profiles.route('/profiles/create_default_profile', methods=['POST'])
def create_default_profiles():

    request_data = request.get_json()

    request_data["user_info"]["account_id"] = "default"
    data = ProfileOperations.create_profile(request_data)
    if not data:
        data = {}
    return jsonify(data)

@profiles.route('/profiles/get_user_profile/<account_id>/<user_id>', methods=['GET'])
def get_user_profile(account_id,user_id):
    # print(profile_id)
    data = ProfileOperations.get_user_profile(account_id,user_id)
    if not data:
        data = {}
    return jsonify(data)