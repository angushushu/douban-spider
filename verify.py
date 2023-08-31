import time, random
from PIL import Image
import requests, json, base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
import os

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get?type=https").json()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

class Douban():

    def __init__(self, proxy):
        print('初始化验证器')
        self.usrnm = 'username'
        self.pswd = 'password'
        self.url = "https://www.douban.com/"
        # 这里配置驱动参数，如增加代理和UA信息
        opt = webdriver.ChromeOptions()
        # 增加代理和UA信息
        # opt.add_argument('--proxy-server=http://223.96.90.216:8085')
        opt.add_argument(
            '--user-agent=' + f"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{proxy.split(':')[0]} Safari/537.36")
        prox = Proxy()
        prox.proxy_type = ProxyType.MANUAL
        prox.http_proxy = proxy
        # prox.socks_proxy = proxy
        # prox.ssl_proxy = proxy
        # 创建webdriver实例
        capabilities = webdriver.DesiredCapabilities.CHROME
        prox.add_to_capabilities(capabilities)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), desired_capabilities=capabilities)
        if self.driver is None:
            print('验证器初始化失败')
            return

    def base64_api(self, img):
        # 图鉴官方提供的接口，这里稍微修改了下，因为自己使用就直接把账号密码放进去了
        with open(img, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            b64 = base64_data.decode()
        data = {"username": self.usrnm, "password": self.pswd, "typeid": 33, "image": b64}
        result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if result['success']:
            return result["data"]["result"]
        else:
            return result["message"]
        return ""

    def input_username_password(self):
        # 实现访问主页，并输入用户名和密码
        self.driver.get(self.url)
        time.sleep(1)
        self.driver.save_screenshot(os.getcwd()+"/reimgs/0.png")
        iframe = self.driver.find_element(By.TAG_NAME, 'iframe')  # 主代码在iframe里面，要先切进去
        self.driver.switch_to.frame(iframe)  # 切到内层
        time.sleep(0.5)
        self.driver.find_element(By.CLASS_NAME, 'account-tab-account').click()  # 模拟鼠标点击
        time.sleep(0.2)
        self.driver.find_element(By.ID, 'username').send_keys(self.usrnm)  # 模拟键盘输入
        time.sleep(0.1)
        self.driver.find_element(By.ID, 'password').send_keys(self.pswd)  # 模拟键盘输入
        time.sleep(0.2)
        self.driver.find_element(By.CSS_SELECTOR, '.btn-account').click()

    def get_img(self):
        """
        获取验证码原图,并获得偏移量和偏移
        :return:
        """
        time.sleep(5)
        iframe = self.driver.find_element(By.TAG_NAME, 'iframe')  # 验证码仍然代码在iframe里面，要先切进去
        # self.driver.switch_to.frame('tcaptcha_iframe')
        self.driver.switch_to.frame(iframe)  # 切到内层
        time.sleep(5)
        # 获取验证码图片
        style_str = self.driver.find_element(By.ID, 'slideBg').get_attribute('style')
        # 获取样式字符串，将该字符串转化为字典
        style_dict = {i.split(':')[0]: i.split(':')[-1] for i in style_str.split('; ')}
        # 组装图片地址
        # src = "https://t.captcha.qq.com" + style_dict['background-image'][6:-2]
        print(style_dict['background-image'])
        src = 'https://'+style_dict['background-image'][2:-2]
        print('img src:',src)
        # 将图片下载到本地
        urlretrieve(src, os.getcwd()+'/reimgs/douban_img1.png')
        # 返回网页图片的宽和高
        return (eval(style_dict['width'][1:-2]), eval(style_dict['height'][1:-3]))

    def get_distance(self, a, b):
        # 实现图片缩放
        captcha = Image.open(os.getcwd()+'/reimgs/douban_img1.png')
        x_scale = captcha.size[0] / a
        y_scale = captcha.size[1] / b
        (x, y) = captcha.size
        x_resize = int(x / x_scale)
        y_resize = int(y / y_scale)
        """
        Image.NEAREST ：低质量
        Image.BILINEAR：双线性
        Image.BICUBIC ：三次样条插值
        Image.ANTIALIAS：高质量 <- removed
        """
        img = captcha.resize((x_resize, y_resize), Image.Resampling.LANCZOS)
        img.save(os.getcwd()+'/reimgs/douban_img2.png')
        time.sleep(0.5)
        # 使用云打码获取x轴偏移量
        distance = self.base64_api(img=os.getcwd()+'/reimgs/douban_img2.png')
        return distance

    def get_track(self, distance):
        """
        计算滑块的移动轨迹
        """
        print('distance:', distance)
        # 通过观察发现滑块并不是从0开始移动，有一个初始值18.6161
        a = int((eval(distance) - 18.6161)/4)
        print('a:', a)
        # 构造每次的滑动参数
        # 注意这里的负数作用：1.为了模拟人手，2.以上计算很多取了约数，最终结果存在误差，但误差往往在一定范围内，可以使用这些数值简单调整。
        track = [a, -2.1, a, -1.8, a, -1.5, a]
        return track

    def shake_mouse(self):
        """
        模拟人手释放鼠标抖动
        """
        ActionChains(self.driver).move_by_offset(xoffset=-0.4, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=0.6, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=-1.1, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=0.9, yoffset=0).perform()

    def operate_slider(self, track):
        print('operate_slider')
        # 定位到拖动按钮
        print('track:', track)
        slider_bt = self.driver.find_element(By.CLASS_NAME, 'tc-slider-normal')
        # 点击拖动按钮不放
        ActionChains(self.driver).click_and_hold(slider_bt).perform()
        # 按正向轨迹移动
        # move_by_offset函数是会延续上一步的结束的地方开始移动
        for i in track:
            ActionChains(self.driver).move_by_offset(xoffset=i, yoffset=0).perform()
            self.shake_mouse()  # 模拟人手抖动
            time.sleep(random.random() / 50)  # 每移动一次随机停顿0-1/100秒之间骗过了极验，通过率很高
        time.sleep(random.random())
        # 松开滑块按钮
        ActionChains(self.driver).release().perform()
        time.sleep(4)

    def login(self):
        """
        实现主要的登陆逻辑
        :param account:账号
        :param password: 密码
        :return:
        """
        print('登录中')
        self.input_username_password()
        time.sleep(3)
        # try:
        # 下载图片，并获取网页图片的宽高
        a, b = self.get_img()
        # 计算滑块的移动轨迹,开始拖动滑块移动
        self.operate_slider(self.get_track(self.get_distance(a, b)))
        # except Exception:
        #     print('没找到滑块')
        #     print(Exception)
        # 输出登陆之后的cookies
        print(self.driver.get_cookies())
        time.sleep(0.5)
        self.driver.save_screenshot(os.getcwd()+"/reimgs/douban.png")

    def __del__(self):
        """
        调用内建的稀构方法，在程序退出的时候自动调用
        类似的还可以在文件打开的时候调用close，数据库链接的断开
        """
        self.driver.quit()


if __name__ == "__main__":
    proxy = get_proxy().get("proxy")
    if proxy is None:
        print('bad proxy')
    douban = Douban(proxy)  # 实例化
    douban.login()  # 之后调用登陆方法