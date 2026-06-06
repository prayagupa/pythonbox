import json
import urllib
from urllib.request import Request, urlopen
import ssl                                                                                             

context = ssl._create_unverified_context()                                                             
REST_url = 'https://api.github.com/'

response = json.load(urlopen(REST_url, context = context))

print(response)
