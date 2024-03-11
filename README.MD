# 雨课堂自动签到辅助
**1. 本程序仅供学习交流使用，不得用于任何商业用途，否则后果自负。**

目前适用于长江雨课堂，其他雨课堂可能无法直接使用，需要修改元素定位。

## 目前有的功能
 - [x] cookie登陆
 - [ ] 账户密码登陆(TODO: 滑块验证码)
 - [x] 钉钉机器人签到提醒
 - [ ] 答题提醒或自动答题

## 教程

### 共通部分

#### 获得cookie
登陆雨课堂，在读取cookie中的`SESSIONID`和`CSRFTOKEN`，
若使用Docker部署，填入`docker-compose.yml`里面。
若使用python部署，填入`.env`里面。

#### 钉钉机器人WebHook
创建群自定义机器人，得到DING_WEBHOOK_TOKEN，填入`docker-compose.yml`或`.env`里面。
例如https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxx，就只用写后面access_token=后面的xxxxxxxxxx即可。

#### 程序部署方式一、Docker
```shell
docker pull galaxysirius/changjiang-autocheckin-selenium
docker pull selenium/standalone-firefox:latest
docker-compose up
```

#### 程序部署方式二、python
安装Edge，EdgeDriver
```shell
python3 __main__.py
```