import requests

keyword="doge"
try:
    kv={"q":keyword}
    r=requests.get("http://www.google.com/search",params=kv)
    print(r.request.url)
    r.raise_for_status()
    print(len(r.text))
except:
    print("faild")