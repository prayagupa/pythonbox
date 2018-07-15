'''
curl -d "data" https://httpbin.org/post
{
  "args": {}, 
  "data": "", 
  "files": {}, 
  "form": {
    "data": ""
  }, 
  "headers": {
    "Accept": "*/*", 
    "Connection": "close", 
    "Content-Length": "4", 
    "Content-Type": "application/x-www-form-urlencoded", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.54.0"
  }, 
  "json": null, 
  "origin": "198.22.122.4", 
  "url": "https://httpbin.org/post"
}
'''

from urllib.parse import urlencode                                                                                                                     
from urllib.request import Request, urlopen                                                            
import ssl                                                                                             
                                                                                                       
url = 'https://httpbin.org/post' # Set destination URL here                                            
post_fields = {'foo': 'bar'}     # Set POST fields here                                                
                                                                                                       
context = ssl._create_unverified_context()                                                             
request = Request(url, urlencode(post_fields).encode(), {"Content-Type": "application/json", "X-client-type": "android"}) 

print(request.headers)
json = urlopen(request, context=context).read().decode()                                               
print(json)
