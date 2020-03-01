from . import common
import datetime
import futsu.hash
import futsu.json
import google.auth
import json
import os

from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    'https://www.googleapis.com/auth/ndev.clouddns.readwrite',
]

def run(request_json, setting_path):

    # check

    request_data = None
    try:
        request_data = json.loads(request_json)
    except:
        return common.e4('JWXOFPHK')

    if 'ACCESS_ID' not in request_data:
        return common.e4('BXDBJSNL')
    if 'DATA' not in request_data:
        return common.e4('HJGZPDCL')
    if 'CHECKSUM' not in request_data:
        return common.e4('PBVYNBOM')

    req_access_id = request_data['ACCESS_ID']
    req_data_json = request_data['DATA']
    req_checksum  = request_data['CHECKSUM']

    setting_data = futsu.json.path_to_data(setting_path)
    if req_access_id not in setting_data['ACCESS_ID_TO_DATA_DICT']:
        return common.e4('LIOPQTIB')
    project_id = setting_data['PROJECT_ID']

    access_secret = setting_data['ACCESS_ID_TO_DATA_DICT'][req_access_id]['SECRET']
    checksum = futsu.hash.sha256_str(access_secret+req_data_json)
    if req_checksum != checksum:
        return common.e4('CFXQASVE')

    req_data = None
    try:
        req_data = json.loads(req_data_json)
    except:
        return common.e4('JWXOFPHK')

    if 'HOSTNAME_LIST' not in req_data:
        return common.e4('IXPHYNRD')
    if 'IP_LIST' not in req_data:
        return common.e4('IEYFFXEV')
    if 'TIMESTAMP' not in req_data:
        return common.e4('ULZTRAVA')

    req_hostname_set  = set(req_data['HOSTNAME_LIST'])
    req_ip_set        = set(req_data['IP_LIST'])
    req_timestamp     = int(req_data['TIMESTAMP'])

    now_ts = datetime.datetime.now().timestamp()
    if abs(now_ts-req_timestamp) > 30:
        return common.e4('JGXDQWHL')

    access_hostname_set = set(setting_data['ACCESS_ID_TO_DATA_DICT'][req_access_id]['HOSTNAME_LIST'])
    if len(req_hostname_set-access_hostname_set) > 0:
        return common.e4('TLCXGDYZ')

    creds = google.auth.default()[0]
    dns_service = discovery.build('dns', 'v1', credentials=creds, cache_discovery=False)

    managed_zone_list = list(get_managed_zone_itr(project_id, dns_service))
    for req_hostname in req_hostname_set:
        good = False
        for managed_zone in managed_zone_list:
            if req_hostname.endswith('.{}'.format(managed_zone['dnsName'])):
                good = True
                break
        if not good:
            return common.e4('AFEPMHFA')

    # process
    
    rrdatas = sorted(list(req_ip_set))
    
    for managed_zone in managed_zone_list:
        zone_dns_name = managed_zone['dnsName']
        req_hostname_list = req_hostname_set
        req_hostname_list = filter(lambda i:i.endswith('.{}'.format(zone_dns_name)), req_hostname_list)
        req_hostname_list = list(req_hostname_list)
        if len(req_hostname_list) <= 0: continue

        zone_name = managed_zone['name']
        host_name_to_resource_record_set_dict = get_resource_record_set_itr(zone_name, project_id, dns_service)
        host_name_to_resource_record_set_dict = filter(lambda i:i['type']=='A', host_name_to_resource_record_set_dict)
        host_name_to_resource_record_set_dict = { i['name']:i for i in host_name_to_resource_record_set_dict }
        #pprint(host_name_to_resource_record_set_dict)

        addition_list = []
        deletion_list = []
        for req_hostname in req_hostname_list:
            if req_hostname in host_name_to_resource_record_set_dict:
                resource_record_set = host_name_to_resource_record_set_dict[req_hostname]
                if sorted(resource_record_set['rrdatas']) == rrdatas:
                    continue
                deletion_list.append(resource_record_set)
            addition_list.append({
                'type': 'A',
                'name': req_hostname,
                'rrdatas': rrdatas,
                'ttl': setting_data['TTL'],
            })
        if (len(addition_list)<=0) and (len(deletion_list)<=0):
            continue

        change_data = {}
        if len(addition_list) > 0:
            change_data['additions'] = addition_list
        if len(deletion_list) > 0:
            change_data['deletions'] = deletion_list
            
        #pprint(change_data)

        request = dns_service.changes().create(project=project_id, managedZone=zone_name, body=change_data)
        ret = request.execute()
        #pprint(ret)
    
    return common.ok()

def get_managed_zone_itr(project_id, dns_service):
    request = dns_service.managedZones().list(project=project_id)
    while request is not None:
        response = request.execute()
        for managed_zone in response['managedZones']:
            yield (managed_zone);
        request = dns_service.managedZones().list_next(previous_request=request, previous_response=response)


def get_resource_record_set_itr(zone_name, project_id, dns_service):
    request = dns_service.resourceRecordSets().list(project=project_id, managedZone=zone_name)
    while request is not None:
        response = request.execute()
        for resource_record_set in response['rrsets']:
            yield (resource_record_set)
        request = dns_service.resourceRecordSets().list_next(previous_request=request, previous_response=response)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting_path')
    parser.add_argument('--request_json')
    args = parser.parse_args()

    print(run(**(args.__dict__)))
