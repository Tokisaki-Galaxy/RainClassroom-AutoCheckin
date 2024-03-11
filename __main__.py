import math
from time import sleep
import requests
import os
import json
import base64
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

changjiang = {
    "changjiang_user": os.getenv("CHANGJIANG_USER"),
    "changjiang_password": os.getenv("CHANGJIANG_PASSWORD"),
    "csrftoken": os.getenv("CSRFTOKEN"),
    "sessionid": os.getenv("SESSIONID"),
}

# 模拟鼠标移动
# TODO: 没做完，但是似乎没必要
def simulate_random_mouse(driver):
    # 创建一个ActionChains实例
    actions = ActionChains(driver)

    # 获取浏览器窗口的大小
    window_size = driver.get_window_size()

    # 计算中心点的位置
    center_x = window_size['width'] // 2
    center_y = window_size['height'] // 2

    # 在中心点画圈
    for i in range(360):
        # 计算圆上的点的坐标
        x = center_x + 100 * math.cos(i * math.pi / 180)
        y = center_y + 100 * math.sin(i * math.pi / 180)
    
        # 移动到计算出的坐标
        actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), x, y)
    
    # 每秒移动20像素
    sleep(0.05)

    # 执行鼠标移动
    actions.perform()

# 账户密码登陆
# TODO: 还没做完，有个滑块验证码没有处理
def userpwd_login(driver):
    driver.find_element_by_xpath('//img[@class="changeImg"]').click()
    driver.find_element_by_xpath('//div[@data-type="phone"]').click()
    # 在输入时解码
    driver.find_element_by_name('loginname').send_keys(base64.b64decode(changjiang.changjiang_user).decode())
    driver.find_element_by_name('password').send_keys(base64.b64decode(changjiang.changjiang_password).decode())
    driver.find_element_by_xpath('//div[@class="submit-btn login-btn customMargin"]').click()

# 钉钉机器人
def DingMsg(Msg):
    # please set charset= utf-8
    HEADERS = {
        "Content-Type": "application/json ;charset=utf-8 "
    }
    # 这里的message是你想要推送的文字消息
    message = "猫猫：\n" + Msg
    stringBody = {
        "msgtype": "text",
        "text": {"content": message},
        "at": {
            "atMobiles": [""],
            "isAtAll": "true"  # @所有人 时为true，上面的atMobiles就失效了
        }
    }
    try:
        MessageBody = json.dumps(stringBody)
        result = requests.post(url=("https://oapi.dingtalk.com/robot/send?access_token="+os.getenv("DING_WEBHOOK_TOKEN")), data=MessageBody, headers=HEADERS)
        print(os.getenv("DING_WEBHOOK_TOKEN"))
        print(result.text)
        if result.json().get('errcode') != 0:
            print("钉钉机器人发送错误:", result.json().get('errmsg'))
        print("已发送信息:",Msg)
    except Exception as e:
        print("钉钉机器人发送错误:",e)

# 检查登陆是否有效
def check_cred_valid(driver):
    if driver.find_elements_by_xpath('//img[@class="changeImg"]'):
        raise(AssertionError)
    
# 尝试登陆
def login(driver):
    print("========Try Login=========")
    # 首先尝试cookie登陆
    try:
        # 删除现有cookie，构造新的cookie
        driver.delete_all_cookies()
        for i in range(2):
            last_item = list(changjiang.items())[-1-i]
            new_dict = {'name': last_item[0], 'value': last_item[1]}
            print(new_dict)
            driver.add_cookie(new_dict)
        driver.get(r'https://changjiang.yuketang.cn/v2/web/index')
        # 检测是否登陆成功
        check_cred_valid(driver)
        print("登陆成功")
    except:
        # 若cookie登陆失败尝试采用用户密码登陆
        try:
            userpwd_login(driver)
            check_cred_valid(driver)
        except Exception as e:
            DingMsg("登陆失败,请更新cookie")
            exit(1)

def inlesson(driver):
    try:
        # 保存当前窗口的句柄
        current_window = driver.current_window_handle
        isLesson = False
        DingMsg("雨课堂开始上课了,10秒后自动签到")
        sleep(10)
        try:
            driver.find_element_by_xpath('//div[@class="name-box"]/span[@class="name"]').click()
            # 切换到新的窗口
            driver.switch_to.window(driver.window_handles[-1])

            h3_elements = driver.find_elements_by_tag_name('h3')
            for h3 in h3_elements:
                span_elements = h3.find_elements_by_xpath('.//span[text()="课堂动态"]')
                if span_elements:
                    isLesson = True
            #<div title="上课啦！" class="timeline__msg f12">上课啦！</div>
            #<h3 data-v-4c2a6625="" class="nav__header box-between"><span data-v-4c2a6625="">课堂动态</span> <i data-v-4c2a6625="" class="iconfont icon-guanbi1 f16 c9b pointer"></i></h3>
            if driver.find_element_by_xpath('//div[@title="上课啦！" and text()="上课啦！"]') and isLesson:
                DingMsg("课程："+driver.title+" "+driver.find_element_by_tag_name('h3')[0]+"开始")
        except:
            DingMsg("签到出错，尝试重试")
            pass

        # 在新的窗口中检查元素，有没有上课了的提示
        while(1):
            sleep(10)
            driver.refresh()
            # 如果短时间内大量重复弹幕，超过两条
            #<section data-v-2e8450a6="" class="danmu__container"><section data-v-2e8450a6="" class="danmu__wrap"><ul data-v-2e8450a6="" class="danmu__list"><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">2</span></p></li></ul></section></section>
            #<input data-v-2e8450a6="" type="text" placeholder="说点什么" class="danmu__ipt J_input f12 cfff">
            #<p data-v-76a19726="" title="弹幕" class="action__danmu box-center f12 cfff active">弹</p>
            #<p data-v-76a19726="" title="弹幕" class="action__danmu box-center f12 cfff">弹</p>
            #<p data-v-2e8450a6="" class="danmu__send box-center cfff">发送</p>
            # 如果有题目发布
            if driver.find_elements_by_xpath('//div[@class="name-box"]/span[@class="name"]'):
                DingMsg("有题目发布，距离截止")
            # 如果有随机点名
            #<div title="随机点名选中：傅玉权2306020108" class="timeline__msg f12">随机点名选中：傅玉权2306020108</div>
            if driver.find_elements_by_xpath('//div[@class="name-box"]/span[@class="name"]'):
                DingMsg("课程结束")
            # 如果有下课的提示
            #<div title="下课啦！" class="timeline__msg f12">下课啦！</div>
            if driver.find_element_by_xpath('//div[@title="下课啦！" and text()="上课啦！"]'):
                DingMsg("课程结束")
                break
        driver.switch_to.windows(current_window)
    except Exception as e:
        pass

def main():
    # 创建一个浏览器实例
    if os.getenv("RUNNING_IN_DOCKER"):
        try:
            sleep(10)
            driver = webdriver.Remote(os.getenv("REMOTE_FIREFOX"), DesiredCapabilities.FIREFOX)
        except Exception as e:
            DingMsg("连接远程selenium出错:", e)
    else:
        driver = webdriver.Edge()
        
    # 打开网页
    try:
        driver.get(r'https://changjiang.yuketang.cn/web/?next=/v2/web/index')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//img[@class="changeImg"]')))
    except Exception as e:
        DingMsg("=====网络连接错误，无法连接到雨课堂=====",e)

    login(driver)

    try:
        driver.get(r'https://changjiang.yuketang.cn/v2/web/index')

        DingMsg("监测开始")
        i=0
        while(1):
            i+=1
            if driver.find_elements_by_xpath('//div[@class="name-box"]/span[@class="name"]'):
                inlesson(driver)
            sleep(10)
            driver.refresh()
            if i>=10:
                try:
                    check_cred_valid(driver)
                except:
                    login(driver)
    except Exception as e:
        print("未知错误，即将退出:",e)
        sleep(5)
        driver.close()

if '__main__' == __name__:
    # 用于直接运行py调试的时候环境变量设置
    if not os.getenv("RUNNING_IN_DOCKER"):
        import dotenv
        dotenv.load_dotenv('.env')
    main()
