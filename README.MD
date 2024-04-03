# 雨课堂自动签到辅助
**1. 本程序仅供学习交流使用，不得用于任何商业用途，否则后果自负。**

目前适用于长江雨课堂，其他雨课堂可能无法直接使用，需要修改元素定位。

## TODO: 写完现有部分，然后尝试改写为nodejs，使用puppeteer。方便部署

## 目前有的功能
 - [x] cookie登陆
 - [ ] 账户密码登陆(TODO: 滑块验证码)
 - [x] 钉钉机器人签到提醒
 - [x] 答题提醒
 - [x] 自动回复弹幕（自动跟风发送）

## 教程

### 共通部分

#### 获得cookie
登陆雨课堂，在读取cookie中的`SESSIONID`和`CSRFTOKEN`，
若使用Docker部署，填入`docker-compose.yml`里面。
若使用python部署，填入`.env`里面。

#### 钉钉机器人WebHook
创建群自定义机器人，得到DING_WEBHOOK_TOKEN，填入`docker-compose.yml`或`.env`里面。
例如https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxx，就只用写后面access_token=后面的xxxxxxxxxx即可。

#### 程序部署方式一、Docker(不推荐，容器运行占用极高，非常卡)
```shell
docker pull galaxysirius/changjiang-autocheckin-selenium
docker pull selenium/standalone-firefox:latest
docker-compose up
```

#### 程序部署方式二、python(推荐，资源占用合理)
安装Firefox，GeckoDriver。记得ubuntu不要安装snap版的firefox，那个和docker一样运行很慢，容器本身占用很高
```shell
# 安装firefox
wget https://download-ssl.firefox.com.cn/releases/firefox/esr/115.1/zh-CN/Firefox-latest-x86_64.tar.bz2
tar xvf Firefox-latest-x86_64.tar.bz2
sudo mv firefox/ /opt
sudo ln -s /opt/firefox/firefox /usr/bin/firefox

# 安装GeckoDriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
tar xvf geckodriver-v0.34.0-linux64.tar.gz
sudo mv geckodriver /usr/bin
```
输入`firefox`如果出现下面的就代表正常，如果出现其他的请百度，安装相应的运行库
```shell
Error: no DISPLAY environment variable specified
```