# -*- coding:utf-8 -*-
"""
作者：mogul
日期：2025年08月27日
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from study_course import AutoCourseBot
import configparser
import time

# 读取配置文件
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# 获取用户名和密码
USERNAME = config.get("login", "username")
PASSWORD = config.get("login", "password")

if __name__ == "__main__":
    bot = AutoCourseBot(USERNAME, PASSWORD)
    bot.login()
    links = bot.get_all_course_links()
    t, href = links[3]
    bot.study_course(href)