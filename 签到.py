import json
import os
import random
import time
import requests
from urllib.parse import quote
from datetime import datetime, date

nczlck = os.environ.get('elmck')

ck = ''

def tq(txt):
    try:
        txt = txt.replace(" ", "")
        pairs = txt.split(";")[:-1]
        ck_json = {}
        for i in pairs:
            ck_json[i.split("=")[0]] = i.split("=")[1]
        return ck_json
    except Exception as e:
        print(f'❎Cookie解析错误: {e}')
        return {}


class LYB:
    def __init__(self, cki):
        self.name = None
        self.cki = tq(cki)
        self.uid = self.cki.get("unb")
        self.sid = self.cki.get("cookie2")
        self.token = self.cki.get("token")
        self.deviceId = self.cki.get("deviceId")
        self.host = 'https://acs.m.goofish.com'
        self.name1 = self.uid

    def xsign(self, api, data, wua, v):

        body = {

            "data": data,

            "api": api,

            "pageId": '',

            "uid": self.uid,

            'sid': self.sid,

            "deviceId": '',

            "utdid": '',

            "wua": wua,

            'ttid': '1551089129819@eleme_android_10.14.3',

            "v": v

        }

        try:

            r = requests.post(

                "http://172.29.112.1:9922/api/getXSign",

                json=body

            )

            r.raise_for_status()

            return r.json()

        except requests.exceptions.HTTPError as e:

            print(f'❎请求签名服务器失败: {e}')

            return None

        except requests.exceptions.RequestException as e:

            print(f'❎请求签名服务器错误: {e}')

            return self.xsign(api, data, wua, v)

    def req(self, api, data, wua='False', v="1.0"):
        try:
            if type(data) == dict:
                data = json.dumps(data)
            wua = str(wua)
            sign = self.xsign(api, data, wua, v)
            url = f"{self.host}/gw/{api}/{v}/"
            headers = {
                "x-sgext": quote(sign.get('x-sgext')),
                "x-sign": quote(sign.get('x-sign')),
                'x-sid': self.sid,
                'x-uid': self.uid,
                'x-pv': '6.3',
                'x-features': '1051',
                'x-mini-wua': quote(sign.get('x-mini-wua')),
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'x-t': sign.get('x-t'),
                'x-extdata': 'openappkey%3DDEFAULT_AUTH',
                'x-ttid': '1551089129819@eleme_android_10.14.3',
                'x-utdid': '',
                'x-appkey': '24895413',
                'x-devid': '',
               
            }

            params = {"data": data}
            if 'wua' in sign:
                params["wua"] = sign.get('wua')

            max_retries = 9999
            retries = 0
            while retries < max_retries:
                try:
                    res = requests.post(url, headers=headers, data=params, timeout=5)
                    return res
                except requests.exceptions.Timeout:
                    print("❎接口请求超时")
                except requests.exceptions.RequestException as e:
                    print(f"❎请求异常: {e}")
                retries += 1
                print(f"❎重试次数: {retries}")
                if retries >= max_retries:
                    print("❎重试次数上限")
                    return None
        except Exception as e:
            print(f'❎请求接口失败: {e}')
            return None

    def login(self):
        api1 = 'mtop.alsc.user.detail.query'
        try:
            res1 = self.req(api1, json.dumps({}), 'False', "1.0")
            if res1.json()['ret'][0] == 'SUCCESS::调用成功':
                self.name = res1.json()["data"]["encryptMobile"]
                api = 'mtop.koubei.interaction.center.common.queryintegralproperty.v2'
                data = json.dumps({"templateIds": "[\"1404\"]"})
                try:
                    res = self.req(api, data, 'False', "1.0")
                    if res.json()['ret'][0] == 'SUCCESS::调用成功':
                        print(f'[{self.name}] ✅登录成功,乐园币----[{res.json()["data"]["data"]["1404"]["count"]}]')
                        return True
                    else:
                        if res.json()['ret'][0] == 'FAIL_SYS_SESSION_EXPIRED::Session过期':
                            print(f"[{self.name1}] ❎cookie已过期，请重新获取")
                            return False
                        else:
                            print(f'[{self.name1}] ❌登录失败,原因:{res.text}')
                            return False
                except Exception as e:
                    print(f"[{self.name1}] ❎登录失败: {e}")
                    return False
            else:
                if res1.json()['ret'][0] == 'FAIL_SYS_SESSION_EXPIRED::Session过期':
                    print(f"[{self.name1}] ❎cookie已过期，请重新获取")
                    return False
                else:
                    print(f'[{self.name1}] ❌登录失败,原因:{res1.text}')
                    return False
        except Exception as e:
            print(f"[{self.name1}] ❎登录失败: {e}")
            return False

    
    

    def signinfo(self):
        api = 'mtop.koubei.interactioncenter.orchard.sign.querysigninfo'
        data = json.dumps(
        {"latitude": "99.597472842782736", "longitude": "99.75325090438128", "bizScene": "orchard_signin"})
        try:
            res = self.req(api, data, 'False', "1.0")
            if res.json()["ret"][0] == "SUCCESS::调用成功":
                date_time = datetime.now().strftime("%Y%m%d")
                for entry in res.json().get("data", {}).get("data", {}).get("signInPrizeList", []):
                    if entry["dayName"] == '今日':
                        for award in entry.get("ext", {}).get("awardInfo", []):
                            if award.get("status") != 'HAS_RECIVE':
                                prizeNumId = award.get("prizeNumId")
                            # 确保传递 prizeNumId 和 date_time 作为参数
                                self.sign(prizeNumId, date_time)
                            
        except Exception as e:
            print(f"[{self.name}] ❎请求错误{e}")
            return None

    def sign(self, prizeNumId, date_time):
        api = 'mtop.koubei.interactioncenter.orchard.sign.receivesigninaward'
        data = json.dumps({"latitude": "99.597472842782736", "longitude": "99.75325090438128", "signInDate": date_time,
                       "bizScene": "orchard_signin", "extInfo": "{\"prizeNumId\":\"" + prizeNumId + "\"}","asac": "2A20C2377ALBCAMWFHTDTC"}) 
        
        try:
            res = self.req(api, data, 'False', "1.0")
            if res.json()["ret"][0] == "SUCCESS::调用成功":
                title = res.json()['data']['data']['ext']['uppSendResult'][0]['materialInfo']['title']
                    
                    
                
                print(f"[{self.name}] ✅签到奖励领取成功，获得--[{title}]")
            else:
                if res.json()["ret"][0] == "FAIL_SYS_SESSION_EXPIRED::Session过期":
                    print(f"[{self.name1}] ❎cookie已过期，请重新获取")
                else:
                    print(f"[{self.name}] ❎签到奖励领取失败:{res.text}")
        except Exception as e:
            print(f"[{self.name}] ❎签到奖励领取失败{e}")
            return None

    
    
        

    def main(self):
        try:
            if self.login():
                #self.kb()
                self.signinfo()
               # self.prize()
                #self.pk()
              #  self.task1()
        except Exception as e:
            print(f"[{self.name1}] 请求错误{e}")


def get_ck_usid(ck1):
    try:
        key_value_pairs = ck1.split(";")
        for pair in key_value_pairs:
            key, value = pair.split("=")
            if key.lower() == "userid":
                return value
    except Exception:
        return 'y'


if __name__ == '__main__':
    today = date.today()
    today_str = today.strftime('%Y%m%d')
    filename = f'{today_str}nc.json'
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
        print("今日助力json文件不存在，已创建")
    else:
        print("今日助力json文件已存在")

    with open(filename, 'r') as file:
        data = json.load(file)

    if 'elmck' in os.environ:
        cookie = os.environ.get('elmck')
    else:
        print("❎环境变量中不存在[elmck],启用本地变量模式")
        cookie = ck
    if cookie == "":
        print("❎本地变量为空，请设置其中一个变量后再运行")
        exit(-1)
    cookies = cookie.split("&")

    print(f"饿了么共获取到 {len(cookies)} 个账号")
    for i, ck in enumerate(cookies):
        print(f"======开始第{i + 1}个账号======")
        LYB(ck).main()
        print("2s后进行下一个账号")
        
