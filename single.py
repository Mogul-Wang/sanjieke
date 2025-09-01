# -*- coding:utf-8 -*-
"""
作者：mogul
日期：2025年08月28日
"""
from study_course import AutoCourseBot
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# 获取用户名和密码
USERNAME = config.get("login", "username")
PASSWORD = config.get("login", "password")

# 获取学习课程类型
course_type = config.get("course_type","type")

if __name__ == "__main__":
    bot = AutoCourseBot(USERNAME, PASSWORD)
    bot.login()
    links = bot.get_all_course_links(course_type)
    # 包含35课程，想刷哪一个课程可以在links中输入相应的数值单独刷
    for i in (1,5):
        for t, href in links[0:45]:
            bot.study_course(href)