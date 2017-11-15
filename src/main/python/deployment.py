from urllib.parse import urlencode                                                                                                                     
from urllib.request import Request, urlopen                                                            
import ssl                                                                                             
                                                                                                       
url = 'https://httpbin.org/post' # Set destination URL here                                            
post_fields = {'foo': 'bar'}     # Set POST fields here                                                
                                                                                                       
context = ssl._create_unverified_context()                                                             
request = Request(url, urlencode(post_fields).encode())                                                
json = urlopen(request, context=context).read().decode()                                               
print(json)
