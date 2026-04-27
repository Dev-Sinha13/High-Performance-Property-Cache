import flask
from flask import Flask
import grpc
import PropertyLookup_pb2, PropertyLookup_pb2_grpc
import os
import time

project_path = os.environ["PROJECT"]

dataset_channel_1 = grpc.insecure_channel(project_path + "-dataset-1:5000")
dataset_channel_2 = grpc.insecure_channel(project_path + "-dataset-2:5000")

stub_dataset_1 = PropertyLookup_pb2_grpc.returnAddressStub(dataset_channel_1)
stub_dataset_2 = PropertyLookup_pb2_grpc.returnAddressStub(dataset_channel_2)

app = Flask("property-cache")

last_used_server = "2"
cache_storage = {}
recent_requests = []

def query_dataset_1(zip_code, limit):
    return stub_dataset_1.LookupByZip(PropertyLookup_pb2.Reqs(zip=zip_code, limit=limit)).output

def query_dataset_2(zip_code, limit):
    return stub_dataset_2.LookupByZip(PropertyLookup_pb2.Reqs(zip=zip_code, limit=limit)).output

def toggle_server():
    global last_used_server
    last_used_server = "1" if last_used_server == "2" else "2"

def store_in_cache(zip_code, addresses):
    global cache_storage
    cache_storage[zip_code] = addresses

def update_recent_requests(zip_code, exists):
    global recent_requests
    if exists:
        recent_requests.remove(zip_code)
        recent_requests.append(zip_code)
    else:
        if len(recent_requests) == 3:
            recent_requests.pop(0)
        recent_requests.append(zip_code)

@app.route("/lookup/<zip_code>")
def lookup(zip_code):
    zip_code = int(zip_code)
    limit = flask.request.args.get("limit", default=4, type=int)
    addresses = None

    global last_used_server

    is_cached = zip_code in recent_requests

    if limit <= 8 and is_cached:
        addresses = cache_storage[zip_code]
        update_recent_requests(zip_code, True)
        return flask.jsonify({"addrs": addresses[:limit], "source": "cache", "error": None})
    
    try:
        actual_limit = max(limit, 8)
        addresses = query_dataset_1(zip_code, actual_limit) if last_used_server == "2" else query_dataset_2(zip_code, actual_limit)
        toggle_server()
    except grpc.RpcError as error:
        toggle_server()
        time.sleep(0.1)
        
        for _ in range(5):
            try:
                addresses = query_dataset_2(zip_code, actual_limit) if last_used_server == "1" else query_dataset_1(zip_code, actual_limit)
                last_used_server = "1" if last_used_server == "2" else "2"
                break
            except grpc.RpcError:
                toggle_server()
                time.sleep(0.1)
                if _ == 4:
                    return flask.jsonify({"addrs": None, "source": last_used_server, "error": str(error)})

    if is_cached:
        update_recent_requests(zip_code, True)
    else:
        update_recent_requests(zip_code, False)
        store_in_cache(zip_code, addresses[:8])
    
    return flask.jsonify({"addrs": addresses[:limit], "source": last_used_server, "error": None})

def main():
    app.run("0.0.0.0", port=8080, debug=False, threaded=False)

if __name__ == "__main__":
    print("starting")
    main()
