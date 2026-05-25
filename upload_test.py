import requests, os
BASE='http://127.0.0.1:8000'
# register user
r = requests.post(BASE+'/api/register/', json={'username':'ingest_tester','email':'ingest@example.com','password':'pass1234'})
print('register', r.status_code, r.text)
if r.status_code!=200:
    # try login
    r = requests.post(BASE+'/api/token/', json={'username':'ingest_tester','password':'pass1234'})
    print('token', r.status_code, r.text)
    token = r.json().get('access')
else:
    token = r.json().get('access')

headers={'Authorization': f'Bearer {token}'}
# upload sample file
here = os.path.dirname(__file__)
samples_dir = os.path.abspath(os.path.join(here, 'breathe_esg', 'samples'))
sample = os.path.join(samples_dir, 'sample_utility.csv')
print('sample path', sample, os.path.exists(sample))
files={'file': open(sample,'rb')}
resp = requests.post(BASE+"/api/ingestion/upload/", headers=headers, files=files, data={'tenant_id':'1'})
print('upload', resp.status_code, resp.text)
