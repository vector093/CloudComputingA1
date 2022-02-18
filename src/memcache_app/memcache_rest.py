from memcache_app import memcache_obj, webapp
from app.cache_utils import get_cache_params
from flask import request
import json
from app.db_connection import get_db
import time

@webapp.route('/put', methods = ['POST'])
def put():
    req_json = request.get_json(force=True)
    key, value = list(req_json.items())[0]
    memcache_obj.pushitem(key, value)
    return get_response(True)

@webapp.route('/clear', methods = ['GET', 'POST'])
def clear():
    memcache_obj.clear_cache()
    return get_response(True)

@webapp.route('/get', methods = ['POST'])
def get():
    req_json = request.get_json(force=True)
    key = req_json["keyReq"]
    response=memcache_obj.getitem(key)
    if response==None:
        return "Unknown key"
        #check db and put into memcache
    else:
        return response

@webapp.route('/test/<key>/<value>')
def test(key,value):
    response=memcache_obj.pushitem(key,value)
    return get_response(response)

@webapp.route('/invalidate', methods = ['POST'])
def invalidate():
    req_json = request.get_json(force=True)
    memcache_obj.invalidate(req_json["key"])
    return get_response(True)

@webapp.route('/set_cache_stats', methods = ['POST'])
def set_cache_stats():
    cnx = get_db()
    cursor = cnx.cursor(buffered = True)
    query_add = '''INSERT INTO cache_stats (cache_size, key_count, 
                    request_count, miss_count) VALUES (%s,%s,%s,%s)'''
    cursor.execute(query_add, (memcache_obj.current_size, 
                    memcache_obj.access_count, memcache_obj.hit + memcache_obj.miss, memcache_obj.miss))
    cnx.commit()
    cnx.close()
    return get_response(True)


@webapp.route('/refreshConfiguration', methods = ['POST'])
def refresh_configs():
    cache_params = get_cache_params()
    if not cache_params == None:
        capacity = cache_params[2]
        replacement_policy = cache_params[3]
        memcache_obj.refreshConfiguration(capacity, replacement_policy)
        return get_response(True)
    return None

def get_response(input=False):
    if input:
        response = webapp.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Bad Request"),
            status=400,
            mimetype='application/json'
        )

    return response

def get_response_no_key():
    response = webapp.response_class(
        response=json.dumps("Unknown key"),
        status=400,
        mimetype='application/json'
    )

    return response
