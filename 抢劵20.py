import os
import re
import time
import asyncio
import datetime
import requests
from urllib.parse import urlencode, quote
import hashlib
import json
import random
import string

proxy_api_url = "http://v2.api.juliangip.com/dynamic/getips?filter=1&ip_remain=1&num=3&pt=1&result_type=json&trade_no=1393165170262761&sign=7fe01dc4e651433a1858dfa1878187f3"

qgid = "20"

host = 'https://acs.m.goofish.com'

ck = ''
from datetime import datetime

# 假设你有一个时间戳，这里以当前时间为例



def generate_random_string(length=50):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def reorder_ck(s: str) -> str:
    order = ["cookie2", "sgcookie", "unb", "USERID", "SID", "token", "utdid", "deviceId", "umt"]
    cookies = s.split(';')
    cookie_dict = {}
    for cookie in cookies:
        key_value = cookie.split('=', 1)
        if len(key_value) == 2:
            key, value = key_value
            cookie_dict[key.strip()] = value.strip()
    reordered_cookies = []
    for key in order:
        if key in cookie_dict:
            reordered_cookies.append(f"{key}={cookie_dict[key]}")
    return ';'.join(reordered_cookies) + ';'


def get_ck_usid(ck1):
    key_value_pairs = ck1.split(";")
    for pair in key_value_pairs:
        key, value = pair.split("=")
        if key == "USERID":
            return value
        else:
            return '账号'


def hbh5tk(tk_cookie, enc_cookie, cookie_str):
    """
    合并带_m_h5_tk
    """
    txt = cookie_str.replace(" ", "")
    txt = txt.replace("chushi;", "")
    if txt[-1] != ';':
        txt += ';'
    cookie_parts = txt.split(';')[:-1]
    updated = False
    for i, part in enumerate(cookie_parts):
        key_value = part.split('=')
        if key_value[0].strip() in ["_m_h5_tk", " _m_h5_tk"]:
            cookie_parts[i] = tk_cookie
            updated = True
        elif key_value[0].strip() in ["_m_h5_tk_enc", " _m_h5_tk_enc"]:
            cookie_parts[i] = enc_cookie
            updated = True

    if updated:
        return ';'.join(cookie_parts) + ';'
    else:
        return txt + tk_cookie + ';' + enc_cookie + ';'


def tq(cookie_string):
    """
    获取_m_h5_tk
    """
    if not cookie_string:
        return '-1'
    cookie_pairs = cookie_string.split(';')
    for pair in cookie_pairs:
        key_value = pair.split('=')
        if key_value[0].strip() in ["_m_h5_tk", " _m_h5_tk"]:
            return key_value[1]
    return '-1'


def tq1(txt):
    """
    拆分cookie
    """
    try:
        txt = txt.replace(" ", "")
        if txt[-1] != ';':
            txt += ';'
        pairs = txt.split(";")[:-1]
        ck_json = {}
        for pair in pairs:
            key, value = pair.split("=", 1)
            ck_json[key] = value
        return ck_json
    except Exception as e:
        print(f'❎Cookie解析错误: {e}')
        return {}


def md5(text):
    """
    md5加密
    """
    hash_md5 = hashlib.md5()
    hash_md5.update(text.encode())
    return hash_md5.hexdigest()


def check_cookie(cookie):
    url = "https://waimai-guide.ele.me/h5/mtop.alsc.personal.queryminecenter/1.0/?jsv=2.6.2&appKey=12574478"
    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            cookie_jar = response.cookies
            token = cookie_jar.get('_m_h5_tk', '')
            token_cookie = "_m_h5_tk=" + token
            enc_token = cookie_jar.get('_m_h5_tk_enc', '')
            enc_token_cookie = "_m_h5_tk_enc=" + enc_token
            cookie = hbh5tk(token_cookie, enc_token_cookie, cookie)
            return cookie
        else:
            return None
    except Exception as e:
        print("解析ck错误")
        return None


class TCS:
    def __init__(self, cki):
        self.stop = False
        self.ck = cki
        self.cki = tq1(cki)
        self.umt = self.cki.get("umt")
        self.name1 = get_ck_usid(cki)
        self.qg_hour = 9
        self.qg_minute = 59
        self.qg_second = 58
        self.qgname = None
        self.copyId = None

    def ip(self, proxy1):
        try:
            global_proxy = {
                'http': proxy1,
                'https': proxy1,
            }
            r = requests.get('http://httpbin.org/ip', proxies=global_proxy)
            print(r.text)
            if r.status_code == 200:
                ip = r.text
                return True
            else:
                return None
        except requests.RequestException as e:
            print(e)
            return None
        except Exception as e:
            print(e)
            return None
    
    def porxy(self):
        proxy_list = []
        r = requests.get(proxy_api_url).json()
        if r.get("code") == 200:
            list = r["data"]["proxy_list"]
            print(list)
            for dl in list:
                dl = dl.split(",")[0]
                print(dl)
                a = self.ip(dl)
                print(a)
                if a:
                    proxy_list.append(dl)
        return proxy_list
        
    def req(self, api, data, v="1.0"):
        try:
            cookie = check_cookie(self.ck)
            headers = {
                "authority": "shopping.ele.me",
                "accept": "application/json",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "cookie": cookie,
            }
            timestamp = int(time.time() * 1000)
            data_str = json.dumps(data)
            token = tq(cookie)
            token_part = token.split("_")[0]

            sign_str = f"{token_part}&{timestamp}&12574478&{data_str}"
            sign = md5(sign_str)
            url = f"https://guide-acs.m.taobao.com/h5/{api}/{v}/?jsv=2.6.1&appKey=12574478&t={timestamp}&sign={sign}&api={api}&v={v}&type=originaljson&dataType=json&data={data_str}"
            data1 = urlencode({'data': data_str})
            r = requests.get(url, headers=headers)
            if r:
                return r
            else:
                return None
        except Exception as e:
            return None

    def login(self):
        api1 = 'mtop.alsc.user.detail.query'
        data1 = {}
        try:
            res1 = self.req(api1, data1, "1.0")
            if res1.json()['ret'][0] == 'SUCCESS::调用成功':
                self.name = res1.json()["data"]["encryptMobile"]
                api = 'mtop.koubei.interaction.center.common.queryintegralproperty.v2'
                data = {"templateIds": "[\"1404\"]"}
                try:
                    res = self.req(api, data, "1.0")
                    if res.json()['ret'][0] == 'SUCCESS::调用成功':
                        print(f'[{self.name}] ✅登录成功,乐园币----[{res.json()["data"]["data"]["1404"]["count"]}]')
                        if int(res.json()["data"]["data"]["1404"]["count"]) >= 3999:
                            return True
                        else:
                            print("乐园币不够兑换优惠券")
                            return False
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

    async def post_qg(self):
        max_attempts = 10 # 设置最大尝试次数
        attempt = 0
        retry_delay = 0.00000001  # 设置重试等待时间为500毫秒
        

        while attempt < max_attempts:
            api1 = 'mtop.koubei.interactioncenter.platform.right.exchange.v2'
            data1 = {
                "actId": "20221207144029906162546384",
                "collectionId": "20221216181231449964003945",
                "copyId": self.copyId,
                "bizScene": "game_center",
                "channel": "abcd",
                "longitude": 104.098238,
                "latitude": 30.229593,
                "hsf": 1,
                
                "umidToken":self.umt,
               
            }
            current_time = datetime.now()

# 格式化时间，以小时:分钟:秒.毫秒的形式打印
            formatted_time = current_time.strftime('%H:%M:%S.%f')[:-3]
            try:
                res1 = self.req(api1, data1, "1.0")
                
                if res1.json()['ret'][0] == "SUCCESS::调用成功":
                    print(f"[{self.name}]✈️✈️✈️ 抢购[{self.qgname}]成功")
                    
                    break
                else:
                    if res1.json()['ret'][0] == "UNKNOWN_FAIL_CODE::系统开小差了，请稍候重试":
                        print(f'[{formatted_time}][{self.name}] 🚑🚑🚑抢[{self.qgname}]购失败,原因:{res1.json()["data"]["errorMsg"]}')
                    else:
                        print(f'[{self.name}] ❌抢🐲[{self.qgname}]购失败,原因:')
            except Exception as e:
                print(f"[{self.name1}] ❌抢☃️[{self.qgname}]购失败")
            attempt += 1
            await asyncio.sleep(retry_delay)

 

        

            
    async def get_id(self):
        api1 = 'mtop.koubei.interactioncenter.platform.right.exchangelist'
        data1 = {
            "actId": "20221207144029906162546384",
            "collectionId": "20221216181231449964003945",
            "bizScene": "game_center",
            "longitude": "104.05759390443563",
            "latitude": "30.69377588108182"
        }
        try:
            res1 = self.req(api1, data1, "1.0")
            if res1.json()['ret'][0] == "SUCCESS::调用成功":
                for right_info in res1.json()['data']['data']['rightInfoList']:
                    if right_info['rightName'] == "20元支付红包":
                        self.qgname = right_info['rightName']
                        self.copyId = right_info['rightId']
                        print(f"[{self.name}] 获取ID成功")
            else:
                print(f"[{self.name}] ❌获取ID失败，原因: {res1.json()['ret'][0]}")
        except Exception as e:
            print(f"[{self.name1}] ❌获取ID失败，原因: {e}")        
            
    def log(self, message, value):
        print(f"{message} {value:.2f} 秒后发起请求")
    
    async def start(self):
        
        await self.get_id()
        
        await self.post_qg()        

    async def main(self):
        if self.login():
            print(f"----开始抢购----")
            await self.start()
            
async def main(cookies):
    print(f"饿了么共获取到 {len(cookies)} 个账号")
    futures = []
    for i, ck in enumerate(cookies):
        print(f"======开始第{i + 1}个账号======")
        ck = reorder_ck(ck)
        future = asyncio.ensure_future(TCS(ck).main())
        futures.append(future)
        if len(futures) >= 10:
            await asyncio.gather(*futures)
            futures = []
    if futures:
        await asyncio.gather(*futures)

# 主函数
if __name__ == '__main__':
    if 'elmqjck' in os.environ:
        cookie = os.environ.get('elmqjck')
    else:
        print("环境变量中不存在[elmqjck],启用本地变量模式")
        cookie = ck
    if cookie == "":
        print("本地变量为空，请设置其中一个变量后再运行")
        exit(-1)
    cookies = cookie.split("&")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(cookies))