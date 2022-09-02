import requests
import re
import time


class NjuUiaAuth:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'
        })

        r = self.session.get('https://authserver.nju.edu.cn/authserver/login')
        self.lt = re.search(r'<input type="hidden" name="lt" value="(.*)"/>', r.text).group(1)
        self.execution = re.search(r'<input type="hidden" name="execution" value="(.*)"/>', r.text).group(1)
        self.qrcode_uuid = None

    def get_qrcode_url(self):
        self.qrcode_uuid = requests.get("https://authserver.nju.edu.cn/authserver/qrCode/get").text
        return 'https://authserver.nju.edu.cn/authserver/qrCode/code?uuid=' + self.qrcode_uuid

    def qrcode_login(self):

        if self.qrcode_uuid is None:
            raise Exception("请先获取二维码链接!")

        while True:
            r = requests.get("https://authserver.nju.edu.cn/authserver/qrCode/status?uuid=" + self.qrcode_uuid)
            if r.text == "0" or r.text == "2":
                pass  # 验证码有效, 等待扫描 或 验证码已扫描, 等待确认
            elif r.text == "3":
                raise Exception("二维码已过期!")
            elif r.text == "1":
                break  # 登录完成
            else:
                raise Exception("未知验证码状态: " + r.text)
            time.sleep(1)


        data = {
            'uuid': self.qrcode_uuid,
            'lt': self.lt,
            'dllt': 'qrLogin',
            'execution': self.execution,
            '_eventId': 'submit',
            'rmShown': '1',
        }

        r = self.session.post('https://authserver.nju.edu.cn/authserver/login', data=data)
        return r.url == 'https://authserver.nju.edu.cn/authserver/index.do'
