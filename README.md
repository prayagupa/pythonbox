install python

```bash
brew update
brew install python3
pip3 install boto3
```

run
===

```bash

$ python --version
Python 2.7.10

$ python Nucleus.py

```

[python import example](http://docs.python-requests.org/en/master/)
--

```bash

$ python 
Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> r = requests.get('http://172.21.3.9:9200')
>>> print(r)
<Response [200]>
>>> r.text
u'{\n  "name" : "sclogevents1",\n  "cluster_name" : "sclogevents",\n  "cluster_uuid" : "xYfSdkW2TKOC40ZcngVhAw",\n  "version" : {\n    "number" : "5.2.2",\n    "build_hash" : "f9d9b74",\n    "build_date" : "2017-02-24T17:26:45.835Z",\n    "build_snapshot" : false,\n    "lucene_version" : "6.4.1"\n  },\n  "tagline" : "You Know, for Search"\n}\n'

```

```bash
export PYTHONPATH=/home/ubuntu/.local/lib/python2.7/site-packages/
```
