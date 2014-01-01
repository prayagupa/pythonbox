import requests
urlTest = 'https://github.com/timeline.json'
r=requests.get(urlTest)
r.json()
