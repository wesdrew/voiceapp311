import urllib3

"""

Set flag HAS_INTERNET_CONNECTION. If HAS_INTERNET_CONNECTION is True, unittests
and integration tests that use a web resource can execute along with tests with
mocked objects and functions

"""

http = urllib3.PoolManager()

try:
    http.request("GET", "www.google.com")
    HAS_INTERNET_CONNECTION = True
except:
    HAS_INTERNET_CONNECTION = False
