import argparse
import datetime
import futsu.hash
import futsu.json
import json
import os
from pprint import pprint
import urllib.request

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

json_path = os.path.join(PROJECT_PATH,'conf','client.json')
json_data = futsu.json.path_to_data(json_path)

my_ip_data = futsu.json.path_to_data('https://api.ipify.org?format=json')

TIMESTAMP=int(datetime.datetime.now().timestamp())
data={
    'HOSTNAME_LIST':json_data['HOSTNAME_LIST'],
    'IP_LIST':[my_ip_data['ip']],
    'TIMESTAMP':TIMESTAMP,
}
data_json = json.dumps(data)
checksum = futsu.hash.sha256_str(json_data['SECRET']+data_json)
request_data = {
    'ACCESS_ID':json_data['ACCESS_ID'],
    'DATA':data_json,
    'CHECKSUM':checksum,
}
post_json = json.dumps(request_data).encode('utf-8')

req = urllib.request.Request(
    url=json_data['SET_A_URL'],
    data=post_json,
    method='POST'
)
try:
    with urllib.request.urlopen(req) as fin:
        print(fin.read())
except urllib.error.HTTPError as e:
    pprint(e.fp.read())
    exit(1)
