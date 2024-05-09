import hmac
import hashlib
import base64
import urllib.parse
import os
import requests,json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from login_model import LoginModel
from signature_model import SignatureModel
from urllib3 import encode_multipart_formdata
from urllib.parse import quote

def getSignatrue(name: str, bizId: str, accessType: str, secretKey: str):
    key = secretKey.encode('utf-8')
    value = (bizId + '\n' + accessType + '\n' + name).encode('utf-8')
    hmac_sha256 = hmac.new(key, value, hashlib.sha1).digest()
    encoded_hmac = base64.b64encode(hmac_sha256)
    return urllib.parse.quote(encoded_hmac)

def rsaEncode(text: str):
    # 公钥字符串
    public_key_pem = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgvxMorfTl9Rmq0e9tto4qF8JW
HFKaWR96ZDM/OCBluOhifKzCQhYgdID9z9rNhWHKLHwGMqGJFjH/57AK84Thadfu
dlUFATnk46Fwr5vmclTI5HNLSXh/rwGey3kHXavqIaPdn8sEI+kwCh+poVExYl8O
7DmOpeE7McmG0iGLOQIDAQAB
-----END PUBLIC KEY-----"""
    # 加载公钥字符串为公钥对象
    public_key = serialization.load_pem_public_key(public_key_pem.encode(encoding='utf-8'), backend=default_backend()) 
    str = public_key.encrypt(
        text.encode(encoding='utf-8'),
        padding.PKCS1v15()
    )
    return quote(base64.b64encode(str))


#获取登录态
def getUserLoginData():
    data = {
      "args": {
        "username": rsaEncode(text='13538006648'),
        "password": rsaEncode(text='Ab123456.'),
        "platform":"1",
        "pubArgs": "{\"appid\":99,\"appostype\":1,\"channel\":\"app-ai-upload\",\"version\":\"2.5\",\"appversion\":\"1.0.0\",\"idfa\":\"\",\"imei\":\"\",\"systemversion\":\"11\",\"t8t_device_id\":\"dbaefb07de41e1f54856b0c973fe9f8e\",\"firstId\":\"dbaefb07de41e1f54856b0c973fe9f8e\",\"first_id\":\"dbaefb07de41e1f54856b0c973fe9f8e\",\"appName\":\"t8t-zxmd-app\",\"jsversion\":\"1.0.5\",\"miniostype\":1,\"platform\":\"1\",\"cityid\":1130,\"cityName\":\"深圳\"}"
      }
    }
    url = "https://apigw.to8to.com/cgi/user/pwd/login?source=tbt-app&appName=t8t-zxmd-app"

    res = requests.post(
        url=url,
        json=data,
    )
    #print('getUserLoginData=====', res.text)
    loginData = json.loads(res.text)
    uid = loginData['result']['uid']
    to8to_token = loginData['result']['to8to_token']

    detailUrl = "https://apigw.to8to.com/cgi/user/app/detailInfo?appName=t8t-zxmd-app&source=tbt-app&uid" + uid + "&ticket=" + to8to_token
    detailRes = requests.post(
        url=detailUrl,
        json={
            "args": {
                "pubArgs": "{\"appid\":98,\"appostype\":1,\"channel\":\"小米\",\"version\":\"2.5\",\"appversion\":\"1.0.0\",\"idfa\":\"\",\"imei\":\"\",\"systemversion\":\"11\",\"t8t_device_id\":\"dbaefb07de41e1f54856b0c973fe9f8e\",\"firstId\":\"dbaefb07de41e1f54856b0c973fe9f8e\",\"first_id\":\"dbaefb07de41e1f54856b0c973fe9f8e\",\"appName\":\"t8t-zxmd-app\",\"jsversion\":\"1.0.5\",\"miniostype\":1,\"platform\":\"1\",\"cityid\":1130,\"cityName\":\"深圳\"}"
            }
        },
    )
    infoData = json.loads(detailRes.text)
    #print('getUserDetailData=====', detailRes.text)
    accountId = str(infoData['result']['accountId'])
    return LoginModel(
        dataMap={
            'accountId': accountId,
            'uid': uid,
            'ticket': to8to_token,
        }
    )

# 上传文件、互动数据到服务器
def uploadSingleData(model: SignatureModel, filePath: str):
    try:
        dataMap = {
            "key": model.newPath,
            "policy": model.policy,
            "success_action_status": 200,
            "OSSAccessKeyId": model.accessId,
            "Signature": model.signature,
        }
        if isinstance(model.headMap, dict):
            dataMap.update(model.headMap)
        with open(filePath, 'rb') as file:
            file_content = file
            dataMap['file'] = file_content.read()
            encode_data = encode_multipart_formdata(dataMap)
            res = requests.post(
                url=model.host,
                data=encode_data[0],
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "Content-type": encode_data[1],
                },
            )
            #print('uploadSignleData====',res.text)
            if (res.status_code == 200):
                return True
    except Exception as e:
        print('上传图片错误=====', e)
    
    return False

def uploadOss(filePath: str, isTestEnv: bool, loginModel: LoginModel):
    secretKey = 'EF84jdJU89kvnf89hfn2675HMNFH88'
    if (isTestEnv):
        secretKey = 'KC84jdJU89kvnf89hfn2675HMNFH88'
    
    bizId = 'tc'
    accessType = 'public'

    data = {
      "args": {
        "clientAuthenticateAndSignDTO": {
          "accessType": accessType,
          "bizId": bizId,
          "expire": 3600,
          "path": filePath,
          "signature": getSignatrue(filePath, bizId, accessType, secretKey),
          "version": "3",
          'customPath': 'spiders',
          'appName': 't8t-zxmd-app',
          'accountId': loginModel.accountId,
        }
      }
    }
    url = "https://apigw.to8to.com/cgi/oss/loginClient/permission/sign?appName=t8t-zxmd-app&source=tbt-app&uid" + loginModel.uid + "&ticket=" + loginModel.ticket

    res = requests.post(
        url=url,
        json=data,
    )
    jsonData = json.loads(res.text)
    signatureModel = SignatureModel(dataMap=jsonData['result'])
    #("uploadOss===", res.text)

    uploadRes = uploadSingleData(model=signatureModel, filePath=filePath)
    if (uploadRes == True):
        return signatureModel
    return None

def uploadAudioToOSS():
    loginModel: LoginModel = getUserLoginData()
    file_path = os.path.join("oss/files_temp", audio_name)
    for file in docment:
        model = uploadOss(filePath=file_path, isTestEnv=False, loginModel=loginModel)
        if (isinstance(model, SignatureModel)):
            newAudioUrl = 'https://pic.to8to.com/' + model.newPath
            return newAudioUrl
    return None