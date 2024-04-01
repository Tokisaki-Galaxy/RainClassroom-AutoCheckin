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

dmsg=0 #上一条信息，防止大量重复发送

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
    global dmsg
    if Msg==dmsg:
        print("检测到重复发送同一条信息,已经停止这条信息的发送");return 1
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
        print(result.text)
        if result.json().get('errcode') != 0:
            print("钉钉机器人发送错误:", result.json().get('errmsg'))
        print("已发送信息:",Msg)
        dmsg = Msg
    except Exception as e:
        print("钉钉机器人发送错误:",str(e))

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

# 每节课中的节的处理
def refresh_section(driver):
    data=[]
    # 找到所有的section元素
    sections = driver.find_elements_by_css_selector('div.nav__list > div.timeline__wrap > div.timeline__item')
    # 遍历所有的section元素
    for section in sections:
        # 获取data-index属性
        ppt_num = section.get_attribute('data-index')
        try:
            ppt_time = section.find_element_by_css_selector('div.timeline__footer.box-between').text
        except:
            ppt_time = -1
        data.append((ppt_num,ppt_time,section))
    DingMsg(data)
    return data

# 对弹幕列表的处理
def refresh_danmu(driver):
    # 如果短时间内大量重复弹幕，超过两条，自动发送同样内容弹幕
    #<section data-v-2e8450a6="" class="danmu__container"><section data-v-2e8450a6="" class="danmu__wrap"><ul data-v-2e8450a6="" class="danmu__list"><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">1</span></p></li><li data-v-2e8450a6="" class="danmu__item J_danmu enter"><p data-v-2e8450a6="" class="danmu--text f12"><!----> <span data-v-2e8450a6="">2</span></p></li></ul></section></section>
    #<input data-v-2e8450a6="" type="text" placeholder="说点什么" class="danmu__ipt J_input f12 cfff">
    #<p data-v-76a19726="" title="弹幕" class="action__danmu box-center f12 cfff active">弹</p>
    #<p data-v-76a19726="" title="弹幕" class="action__danmu box-center f12 cfff">弹</p>
    #<p data-v-2e8450a6="" class="danmu__send box-center cfff">发送</p>
    # 找到元素
    element = driver.find_element_by_css_selector('p.action__danmu.box-center.f12.cfff')
    # 检查类是否包含active
    if 'active' not in element.get_attribute('class').split():
        # 如果不包含，点击元素
        element.click()
    # 检测弹幕列表
    # 找到所有的span元素
    spans = driver.find_elements_by_xpath('//section[@class="danmu__container"]/section[@class="danmu__wrap"]//span')
    # 创建一个列表来保存数据
    data = []
    # 遍历所有的span元素
    for span in spans:
        # 获取span元素的文本
        text = span.text
        data.append(text)
        print(data)
    from collections import Counter
    # 统计data列表中每个元素出现的次数
    counter = Counter(data)
    # 找到出现次数最多的元素
    most_common_element, count = counter.most_common(1)[0]
    # 检查出现次数是否大于2
    if count > 2:
        print(most_common_element)
        # 找到元素并填充
        driver.find_element_by_css_selector('input.danmu__ipt.J_input').send_keys(most_common_element)
        # 发送弹幕
        driver.find_element_by_css_selector('p.danmu__send.box-center').click()

def inlesson(driver):
    try:
        # 保存当前窗口的句柄
        current_window = driver.current_window_handle
        isLesson = False
        section_data={}
        sleep(20)
        try:
            driver.find_element_by_xpath('//div[@class="name-box"]/span[@class="name"]').click()
            # 切换到新的窗口
            driver.switch_to.window(driver.window_handles[-1])
            sleep(5)

            h3_elements = driver.find_elements_by_tag_name('h3')
            for h3 in h3_elements:
                span_elements = h3.find_elements_by_xpath('.//span[text()="课堂动态"]')
                if span_elements:
                    isLesson = True
            #<div title="上课啦！" class="timeline__msg f12">上课啦！</div>
            #<h3 data-v-4c2a6625="" class="nav__header box-between"><span data-v-4c2a6625="">课堂动态</span> <i data-v-4c2a6625="" class="iconfont icon-guanbi1 f16 c9b pointer"></i></h3>
            if driver.find_elements_by_xpath('//div[starts-with(@title, "上课啦")]') and isLesson:
                DingMsg("课程："+driver.title+" "+driver.find_elements_by_tag_name('h3')[0].text+"开始")
        except Exception as e:
            DingMsg("签到出错，尝试重试"+str(e))
            pass

        # 在新的窗口中检查元素，有没有上课了的提示
        while(1):
            sleep(10)
            if False:
                driver.refresh()
                try:
                    driver.switch_to.alert.accept()
                except:
                    pass
            try:
                section_data=refresh_section(driver)
                print(section_data)
                section_data[-2][2].click()
                section_data[-1][2].click()
            except:
                pass

            if driver.find_elements_by_css_selector('section.danmu__container'):
                refresh_danmu(driver)
            # 如果有题目发布
            if driver.find_elements_by_css_selector('div.time-box'):
                DingMsg("有题目发布，"+driver.find_element_by_css_selector('div.time-box > div.timing.timing--number').text)
            # 如果有随机点名
            #<div title="随机点名选中：傅玉权2306020108" class="timeline__msg f12">随机点名选中：傅玉权2306020108</div>
            if driver.find_elements_by_xpath('//div[starts-with(@title, "随机点名选中：")]'):
                DingMsg(driver.find_element_by_xpath('//div[starts-with(@title, "随机点名选中：")]').text)
            # 如果有下课的提示
            #<div title="下课啦！" class="timeline__msg f12">下课啦！</div>
            if driver.find_elements_by_xpath('//div[@title="下课啦！" and text()="下课啦！"]'):
                DingMsg("课程结束")
                break
        driver.close()
        try:
            driver.switch_to.alert.accept()
        except:
            pass
        driver.switch_to.window(current_window)
    except Exception as e:
        DingMsg("上课时碰到问题"+str(e))
        driver.switch_to.window(current_window)
        pass

def main():
    # 创建一个浏览器实例
    if os.getenv("RUNNING_IN_DOCKER"):
        try:
            sleep(10)
            options = webdriver.FirefoxOptions()
            options.set_preference("intl.accept_languages", "zh-CN")
            driver = webdriver.Remote(os.getenv("REMOTE_FIREFOX"), DesiredCapabilities.FIREFOX,options=options)
        except Exception as e:
            DingMsg("连接远程selenium出错:", str(e))
    else:
        driver = webdriver.Edge()
        
    # 打开网页
    try:
        driver.get(r'https://changjiang.yuketang.cn/web/?next=/v2/web/index')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//img[@class="changeImg"]')))
    except Exception as e:
        DingMsg("=====网络连接错误，无法连接到雨课堂=====",str(e))

    login(driver)

    try:
        driver.get(r'https://changjiang.yuketang.cn/v2/web/index')

        DingMsg("监测开始")
        cre_i=0
        #<div class="name-box"><span class="tag">考</span> <span class="name">第一次数模实战</span></div>
        #<div class="name-box"><span class="tag">听</span> <span class="name">第一次数模实战</span></div>
        #<div class="name-box"><span class="tag">教</span> <span class="name">第一次数模实战</span></div>
        #如果有多个项目会出现<i class="iconfont icon icon--shuangjiantouxiangxia"></i>
        while(1):
            cre_i+=1
            # 找到name-box元素
            name_box =   driver.find_elements_by_css_selector('.name-box')
            both_class = driver.find_elements_by_css_selector('.iconfont.icon.icon--shuangjiantouxiangxia')
            # 检查是否找到了name-box元素
            if name_box or both_class:
                if both_class:
                    #<div class="onlessonlist"><div class="lessonlist"><div class="left"><p class="lessonTitle">s</p> <span class="status">教</span> <span class="teacher">医疗产品管理一班</span></div> <div class="right"><i class="iconfont icon--yinpinbofang"></i></div></div> <div class="lessonlist"><div class="left"><p class="lessonTitle">第一次数模实战</p> <span class="status">考试</span> <span class="teacher">校创数模学习小组</span></div> <div class="right"><i class="iconfont icon--danjiantouxiangyou f16"></i></div></div></div>
                    both_class[0].click()
                    sleep(2)
                    # 找到onlessonlist元素
                    onlessonlist = driver.find_element_by_css_selector('.onlessonlist')
                    onless_lessonlists = onlessonlist.find_elements_by_css_selector('.lessonlist>.left')
                    # 创建列表
                    result = []
                    for lessonlist in onless_lessonlists:
                        # 找到所有的span元素
                        lesson_spans = lessonlist.find_elements_by_tag_name('span')
                        lesson_ps = lessonlist.find_element_by_tag_name('p')
                        # 添加到结果列表
                        result.append([lesson_spans[0].text, lesson_ps.text, lesson_spans[1].text])
                    for i in result:
                        if i[0]=='听':
                            DingMsg("雨课堂开始上课了,这节课是"+i[1]+",20秒后自动签到。\
                                    \n请注意,当前有多个课程：\n"+'\n'.join(map(str, result)))
                            inlesson(driver)
                        elif i[0]=='考试':
                            DingMsg("处于考试状态，将停止监控上课。当前正在考试科目："+i[2]+"\
                                    \n请注意,当前有多个课程：\n"+'\n'.join(map(str, result)))
                elif name_box:
                    # 找到所有的span元素
                    spans = name_box[0].find_elements_by_tag_name('span')
                    # 检查第一个span元素的文本是否为"考"
                    if spans[0].text == "考":
                        DingMsg("处于考试状态，将停止监控上课。当前正在考试科目："+spans[1].text)
                    elif spans[0].text == '听':
                        DingMsg("雨课堂开始上课了,20秒后自动签到")
                        inlesson(driver)
            sleep(10)
            name_box=0;both_class=0
            driver.refresh()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'tab-student')))
            if cre_i>=10:
                try:
                    check_cred_valid(driver)
                except:
                    login(driver)
    except Exception as e:
        print("未知错误，即将退出:",str(e))
        sleep(5)
        driver.close()

if '__main__' == __name__:
    # 用于直接运行py调试的时候环境变量设置
    if not os.getenv("RUNNING_IN_DOCKER"):
        import dotenv
        dotenv.load_dotenv('.env')
    main()
