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
        self.umt = self.cki.get("umt")
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
                    print(f"[{self.name}] ❎签到奖励领取失败::{res.json()['ret'][0]}")
        except Exception as e:
            print(f"[{self.name}] ❎签到奖励领取失败{e}")
            return None
    def ylyrw(self):
        timestamp = int(time.time() * 1000)
        api = 'mtop.koubei.interactioncenter.orchard.addwaterpk.query'
        data = json.dumps({"bizScene":"WATER_PK","requestId": timestamp}) 
        
        try:
            res = self.req(api, data, 'False', "1.0")
            
            if res.json()["ret"][0] == "SUCCESS::调用成功":
            
                print(f'[{self.name}] ✅浇水竞赛成功')
                api = 'mtop.koubei.interactioncenter.orchard.addwaterpk.receive'
                data = json.dumps({"bizScene":"WATER_PK","requestId": timestamp})
                res = self.req(api, data, 'False', "1.0")
                
                if res.json()["ret"][0] == "SUCCESS::调用成功":

                    print(f'[{self.name}] ✅竞赛奖励领取成功')
                else:
                    print(f"[{self.name}] ❎竞赛奖励领取失败，原因:{res.json()['data']['errorMsg']}")
            else:
                    print(f"[{self.name}] ❎浇水竞赛失败::{res.json()['ret'][0]}")
        except Exception as e:
            print(f"[{self.name}] ❎任务失败{e}")
            return None                             
                      
                             
                                    
                                                  
    def task(self):
        api = 'mtop.ele.playgame.orchard.futurewater.receive'
        data = json.dumps({"bizScene":"KB_ORCHARD"}) 
        
        try:
            res = self.req(api, data, 'False', "1.0")
            if res.json()["ret"][0] == "SUCCESS::调用成功":
                sd=res.json()['data']['data']['receiveWater']
                
                print(f"[{self.name}] ✅井水奖励领取成功,获得水滴{sd}")
            else:
                if res.json()["ret"][0] == "FAIL_SYS_SESSION_EXPIRED::Session过期":
                    print(f"[{self.name1}] ❎cookie已过期，请重新获取")
                else:
                    print(f"[{self.name}] ❎井水奖励领取失败:{res.json()['ret'][0]}")
        except Exception as e:
            print(f"[{self.name}] ❎井水奖励领取失败{e}")
            return None
    def task1(self):
        types = [16758001,18944001,18998001]
        for t in types:
            api = 'mtop.ele.biz.growth.task.event.pageview'
            data = json.dumps({"bizScene":"drink_treat","accountPlan":"HAVANA_COMMON","collectionId":"937","missionId":str(t),"actionCode":"PAGEVIEW","sync":"false"})
            
            res = self.req(api, data, 'False', "1.0")
            
            if res.json()["ret"][0] == "SUCCESS::接口调用成功":
                print(f'[{self.name}] ✅抽奖任务完成')
                if t == 16758001:
                    count = '5'
                else:
                    count = '1'
                for t in types:
                    api = 'mtop.ele.biz.growth.task.core.receiveprize'
                    data = json.dumps({
                    "bizScene":"drink_treat",
                    "accountPlan":"HAVANA_COMMON",
                    "missionCollectionId":"937",
                    "missionId":str(t),
                    "count":str(count),
                    "locationInfos":"[\"{\\\"lng\\\":\\\"108.36640678346157\\\",\\\"lat\\\":\\\"22.817699946463108\\\"}\"]",
                    "asac":"2A23530Z8CEXYR2809QS5A"
                    })
                    
                    res = self.req(api, data, 'False', "1.0")
                    
                    if res.json()["ret"][0] == "SUCCESS::接口调用成功":
                        print(f'[{self.name}] ✅抽奖次数+1')
                    else:
                        print(f"[{self.name}] ❎领取失败:{res.json()['ret'][0]}")
                        
            else:
                print(f"[{self.name}] ❎任务失败:{res.json()['ret'][0]}")
    def task2(self):
        max_attempts = 4
        attempt = 0
        while attempt < max_attempts:
            api = 'mtop.koubei.interactioncenter.platform.right.lottery'
            data = json.dumps({
            "longitude":"108.36640678346157",
            "latitude":"22.817699946463108",
            "actId":"20230815011206716186127700",
            "collectionId":"20230815011206736917997880",
            "componentId":"20230815011509027382579282",
            "bizScene":"drink_treat",
            "asac":"2A23530Z8CEXYR2809QS5A",
            "bizCode":"lottery",
            "extParams":"{\"bizType\":\"drink_treat_lottery\"}",
            "umidtoken":self.umt
            })
            
            res = self.req(api, data, 'False', "1.0")
            
            if res.json()["ret"][0] == "SUCCESS::调用成功":
                title = res.json()['data']['data']['sendRightList'][0]['materialInfo']['title']
                print(f'[{self.name}] ✅抽奖成功，获得{title}')
            else:
                print(f"[{self.name}] ❎抽奖失败原因:{res.json()['data']['errorMsg']}")
            attempt += 1
    def main(self):
        try:
            if self.login():

                self.signinfo()
                self.ylyrw()
                
                self.task()
                self.task1()
                self.task2()

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
        
