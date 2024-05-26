import datetime
import futsu.json
import futsu.storage
import os

timestamp = int(datetime.datetime.now().timestamp())

setting_data = futsu.json.path_to_data('setting.json')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = setting_data['GOOGLE_APPLICATION_CREDENTIALS']
os.environ["GCLOUD_PROJECT"] = setting_data['PROJECT_ID']

futsu.storage.local_to_path(setting_data['SETTING_PATH'], 'setting.json')
futsu.storage.local_to_path(setting_data['SETTING_BACKUP_PATH'].replace('{TIMESTAMP}',str(timestamp)), 'setting.json')
