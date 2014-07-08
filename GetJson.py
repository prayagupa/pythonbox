import requests
urlTest = 'https://github.com/timeline.json'
r=requests.get(urlTest)
# Need the 'print' to produce output when run as a script
print r.json()
