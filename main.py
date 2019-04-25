#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Author : Su18
# @Copyright : <phoebebuffayfan9527@gmail.com>
# @For U : Like knows like.

import time
import random
import datetime
import requests
import linecache
from wxpy import *
from pyquery import PyQuery
from apscheduler.schedulers.background import BackgroundScheduler

# 实例化机器人，设置缓存避免重复登录，将二维码显示在console中
bot = Bot(cache_path=True, console_qr=True)
# 自动消除手机端的新消息小红点提醒
bot.auto_mark_as_read = True
# 指定女朋友微信昵称
girlfriend = bot.friends().search('这里写你女朋友的微信昵称')[0]
# 指定接收记录日志微信昵称
log_friend = bot.friends().search('这里写日志记录的微信名称')[0]
# 实例化图灵机器人，传入自己的api-key
chat_bot = Tuling(api_key='这里写图例API')
# 日志记录模块实例化
logger = get_wechat_logger(log_friend)
# 实例化时间调度类，使用非阻塞BackgroundScheduler
scheduler = BackgroundScheduler()


# 程序启动初次消息提供
girlfriend.send('你好，我是***，现在上线啦，我是一名机器人，有一些简单的基础功能，后续的功能还有待完善哦~')
girlfriend.send('我将会每日提供历史上的今天、每日英文、每日古诗词、微博热搜等功能，以供使用~')
girlfriend.send('你也可以与我进行聊天，我都会尽力回复的，如果你说的话我不理解，那我就学说话~')
girlfriend.send('希望你每天都开心快乐~φ(≧ω≦*)♪')


# 处理聊天逻辑主函数
@bot.register(girlfriend)
def reply_my_friend(msg):
    # 监听女友诉求
    logger.error(msg)
    # 判断关键字
    if msg.text == "微博热搜" or msg.text == '热搜':
        girlfriend.send('还真看微博热搜？吃屎吧你')
        most_searched_hashtags()
    elif msg.text == "我爱你":
        girlfriend.send('诶呀我知道你爱我，你爱我有啥用？来点实际的？')
    elif msg.text == "":
        pass
    else:
        # 若无自定义关键字，转为图灵机器人聊天
        auto_chat(msg)


# 注册使用图灵机器人自动与女友聊天
def auto_chat(msg):
    return chat_bot.do_reply(msg)


# 获取微博热搜榜,女孩子喜欢看热搜，获取榜单，打入标签。
def most_searched_hashtags():
    result = ''
    try:
        r = PyQuery("https://s.weibo.com/top/summary")
        for i in r(".td-02 a").items():
            result += i.text() + '\n'
        girlfriend.send(result)
        girlfriend.send('微博当前热搜前50个，排名按照热度排序')
    except Exception as e:
        logger.warning(e)
        logger.warning('微博热搜发送异常！')


# 获取金山词霸每日一句，英文和翻译（感谢免费接口提供）
@scheduler.scheduled_job('cron', id='get_news', day_of_week='mon-fri', hour=12, minute=00)
def get_news():
    girlfriend.send('要午休了~宝宝有没有乖乖的准备吃饭呢~吃饭之前，先来句英文佳句，据说饥饿的时候记忆力最好哦~')
    try:
        r = requests.get("http://open.iciba.com/dsapi/")
        girlfriend.send(r.json().get('content'))
        girlfriend.send(r.json().get('note'))
        logger.info('每日英语发送完毕。')
    except Exception as e:
        logger.warning(e)
        logger.warning('每日英文发送异常！')


# 获取古诗词API，每日推荐一首古诗词（感谢免费接口提供），周一至周五下午6点定时发送，此时女友快下班了
@scheduler.scheduled_job('cron', id='get_poetry', day_of_week='mon-fri', hour=18, minute=00)
def get_poetry():
    headers = {
        'X-User-Token': '这里写古诗词API token',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
                       Chrome/41.0.2228.0 Safari/537.36'
    }
    girlfriend.send('快下班了，推荐一首古诗词，换换心情~')
    try:
        r = requests.get("https://v2.jinrishici.com/sentence", headers=headers)
        origin_poetry = r.json().get('data').get('origin')
        girlfriend.send('诗名：%s' % origin_poetry.get('title'))
        girlfriend.send('朝代：%s 作者：%s' % (origin_poetry.get('dynasty'), origin_poetry.get('author')))
        girlfriend.send(''.join(origin_poetry.get('content')))
        girlfriend.send('经典佳句：%s' % r.json().get('data')('content'))
        logger.info('每日古诗词发送完毕。')
    except Exception as e:
        logger.warning(e)
        logger.warning('每日英文发送异常！')


# 历史上的今天，去掉返回结果中的广告（感谢免费接口提供），周一至周五早9点定时发送，此时女友在地铁上
@scheduler.scheduled_job('cron', id='get_today', day_of_week='mon-fri', hour=9, minute=00)
def get_today():
    girlfriend.send('在地铁上辛苦了，看看历史上的今天，涨涨知识~')
    try:
        r = requests.get("http://www.ipip5.com/today/api.php?type=txt")
        girlfriend.send(r.text[:-24])
        logger.info('每日历史上的今天发送完毕')
    except Exception as e:
        logger.warning(e)
        logger.warning('历史上的今天发送异常！')


# 随机早安语句，周一至周五早7点50定时发送，此时女友还在赖床
@scheduler.scheduled_job('cron', id='morning', day_of_week='mon-fri', hour=7, minute=50)
def morning():
    # 指定文件路径
    file_path = './greeting/morning.txt'

    try:
        # 随机选取行数读取文件
        count = len(open(file_path, 'r', encoding='utf-8').readlines())
        random_count = random.randrange(1, count, 1)
        result = linecache.getline(file_path, random_count)
        # 发送消息
        girlfriend.send(result)
        logger.info('每日早安发送完毕，今天发送的是%s' % result)
    except Exception as e:
        logger.warning(e)
        logger.warning('早安发送失败！')


# 随机晚安语句，加晚安心语，周一至周五晚22点30定时发送，此时准备睡觉了
@scheduler.scheduled_job('cron', id='night', day_of_week='mon-fri', hour=22, minute=30)
def night():
    # 指定文件路径
    file_path = './greeting/night.txt'
    try:
        # 随机选取行数读取文件
        count = len(open(file_path, 'r', encoding='utf-8').readlines())
        random_count = random.randrange(1, count, 1)
        result = linecache.getline(file_path, random_count)
        # 发送晚安
        girlfriend.send(result)
        logger.info('每日晚安发送完毕，今天发送的是%s' % result)
    except Exception as e:
        logger.warning(e)
        logger.warning('晚安发送失败！')


# 计算在一起的时间，发送表白，周一至周五早9点30定时发送，此时女友刚刚开始上班
@scheduler.scheduled_job('cron', id='love_time', day_of_week='mon-fri', hour=9, minute=30)
def love_time():
    now_time = datetime.datetime.now()
    first_time = datetime.datetime(**, **, **) # 这里写你跟女朋友在一起的那一天
    love = (now_time-first_time).days
    try:
        girlfriend.send('今天是我们在一起的第 %s 天，今天的你，有没有像昨天一样爱我呢？' % love)
        girlfriend.send('带着爱我的心情，好好上班呦~')
        logger.info('表白发送成功')
    except Exception as e:
        logger.warning(e)
        logger.warning('表白发送失败！')


# 获取北京天气，格式化字符串，周一至周五早8点定时发送，此时女友还未出门
@scheduler.scheduled_job('cron', id='get_weather_info', day_of_week='mon-fri', hour=8, minute=00)
def get_weather_info():
    try:
        # 获取API信息
        weather = requests.get('http://t.weather.sojson.com/api/weather/city/101010100')
        w = weather.json().get('data').get('forecast')[1]
        # 格式化天气消息
        today_weather = "今日天气：\n温度：%s/%s\n%s:%s\n空气指数：%s\n日出时间：%s\n日落时间：%s\n天气：%s\n%s" % \
                        (w.get('low'), w.get('high'), w.get('fx'), w.get('fl'),
                         w.get('aqi'), w.get('sunrise'), w.get('sunset'), w.get('type'), w.get('notice'))
        # 发送格式化后天气
        girlfriend.send(today_weather)
        logger.info('天气发送成功')
    except Exception as e:
        logger.warning(e)
        logger.warning('天气发送失败！')


# 获取bing每日图片故事，周一至周五晚22点29定时发送，此时女友准备睡觉
@scheduler.scheduled_job('cron', id='night', day_of_week='mon-fri', hour=22, minute=29)
def bing_picture():
    # 由于bing接口目前停止提供，根据日期调用三年前的接口
    now_time = int(time.strftime("%Y%m%d", time.localtime())) - 30000
    # 以时间作为文件名
    filename = '%s.jpg' % str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    try:
        girlfriend.send('已经晚上啦，要准备睡觉啦，到了图片故事环节了，看完就睡觉吧~')
        r = requests.get('https://cn.bing.com/cnhp/coverstory?d=%s' % now_time).json()
        girlfriend.send('图片标题：%s\n图片故事：%s\n提供者：%s\n地区：%s %s' %
                        (r.get('title'), r.get('para1'), r.get('provider'), r.get('Country'), r.get('City')))
        # 获取图片并保存
        with open('./bing_images/%s' % filename, 'wb') as file:
            file.write(requests.get(r.get('imageUrl')).content)
        # 发送图片
        girlfriend.send_image('./bing_images/%s' % filename)
        logger.info('每日图片故事发送成功')
    except Exception as e:
        logger.warning(e)
        logger.warning('每日图片故事发送失败！')


# 启动时间调度
scheduler.start()
# 阻塞线程
embed()
