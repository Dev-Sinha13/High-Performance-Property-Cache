import grpc
import pandas as pd
import PropertyLookup_pb2_grpc, PropertyLookup_pb2
from concurrent import futures


class dataLookup(PropertyLookup_pb2_grpc.returnAddressServicer):
    def __init__(self):

        self.data = pd.read_csv("addresses.csv.gz", compression='gzip')
        
    def LookupByZip(self, request, context):
        
        zip_code = request.zip
        request_limit = request.limit

        address_list = self.data[self.data['ZipCode'] == zip_code]['Address'].tolist()
        address_list.sort()
        return PropertyLookup_pb2.response(output=address_list[:request_limit])


server = grpc.server(futures.ThreadPoolExecutor(max_workers=1), options=[("grpc.so_reuseport", 0)])

PropertyLookup_pb2_grpc.add_returnAddressServicer_to_server(dataLookup(), server)

server.add_insecure_port("0.0.0.0:5000")

print("Starting the dataset server...")
server.start()
server.wait_for_termination()
