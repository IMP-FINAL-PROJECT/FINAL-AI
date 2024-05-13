import urllib.request
from config.Config_list import NAVER_CONFIG
import json

def en_to_ko(text):
    client_id = NAVER_CONFIG['CLIENT_ID']
    client_secret = NAVER_CONFIG['CLIENT_SECRET']
    encText = urllib.parse.quote(text)
    data = "source=en&target=ko&text=" + encText + "&honorific=true"
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
    request.add_header("X-NCP-APIGW-API-KEY",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        result = response_body.decode('utf-8')
        translate_text = json.loads(result)
        return (translate_text['message']['result']['translatedText'])
    else:
        print("Error Code:" + rescode)

def ko_to_en(text):
    client_id = NAVER_CONFIG['CLIENT_ID']
    client_secret = NAVER_CONFIG['CLIENT_SECRET']
    koText = urllib.parse.quote(text)
    data = "source=ko&target=en&text=" + koText + "&honorific=true"
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
    request.add_header("X-NCP-APIGW-API-KEY",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        result = response_body.decode('utf-8')
        translate_text = json.loads(result)
        return (translate_text['message']['result']['translatedText'])
    else:
        print("Error Code:" + rescode)