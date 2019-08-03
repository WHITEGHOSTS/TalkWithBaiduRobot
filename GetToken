import urllib.request
import json

# 网址 https://console.bce.baidu.com/ai/#/ai/unit/app/list
# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=your AK&client_secret=your SK'
request = urllib.request.Request(host)
request.add_header('Content-Type', 'application/json; charset=UTF-8')
response = urllib.request.urlopen(request)
content = response.read()
content = json.loads(content)
if (content):
    print(content['access_token'])
