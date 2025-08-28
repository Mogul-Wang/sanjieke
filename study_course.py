# -*- coding:utf-8 -*-
"""
作者：mogul
日期：2025年08月28日
功能：自动学习课程（刷时长）
"""
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# 获取用户名和密码
USERNAME = config.get("login", "username")
PASSWORD = config.get("login", "password")


class AutoCourseBot:
    def __init__(self, username, password):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 15)
        self.username = username
        self.password = password

    # ========== 工具函数 ==========
    def handle_popup(self):
        """处理学习过程中的弹窗"""
        try:
            popup_btn = self.driver.find_element(By.CSS_SELECTOR, "div.score-popup button.close-btn")
            if popup_btn.is_displayed():
                popup_btn.click()
                print("⚡ 弹窗已关闭，继续学习")
                time.sleep(3)
        except NoSuchElementException:
            pass

    def have_cretificate(self):
        try:
            # 查找父标签
            parent_element = self.driver.find_element(By.CSS_SELECTOR,"div.course-left")
            try:
                # 在父标签下查找目标子标签
                parent_element.find_element(By.CSS_SELECTOR, "div.certInfo")
                # 如果找到子标签，返回True
                return True
            except NoSuchElementException:
                # 未找到子标签
                return False
        except NoSuchElementException:
            # 未找到父标签
            return False

    def get_progress(self):
        """获取课程进度（已完成节数，总节数）"""
        try:
            finished_text = self.driver.find_element(By.CSS_SELECTOR, "span.section-finish").text
            finished_num = int("".join(filter(str.isdigit, finished_text)))
        except:
            finished_num = 0
        total_text = self.driver.find_element(By.CSS_SELECTOR, "span.section-total").text
        total_num = int("".join(filter(str.isdigit, total_text)))

        return finished_num, total_num

    # ========== 核心功能 ==========
    def login(self):
        self.driver.get("https://sntelelearning.b.sanjieke.cn/login/sign_in")

        username_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#rc_select_0"))
        )
        username_input.send_keys(self.username)

        password_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.input-text[type='password']"))
        )
        password_input.send_keys(self.password)

        login_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.confirm-btn"))
        )
        login_btn.click()
        print("✅ 登录成功")

    def get_all_course_links(self):
        """翻页获取所有课程链接"""
        card_module = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.card-item-container"))
        )
        time.sleep(5)
        # 找到课程卡片里的所有入口 <a class="card-item">
        course_links = card_module.find_elements(By.CSS_SELECTOR, "a.card-item")
        if course_links:
            course_links[0].click()
            print("点击第一个课程入口，进入学习页面。")
            time.sleep(5)
            # 获取所有 a 标签
            all_links = []  # 存储所有 a 标签
        while True:
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            a_tags = self.driver.find_elements(By.TAG_NAME, "a")
            for a in a_tags:
                href = a.get_attribute("href")
                text = a.text.strip()
                if href and "/course/" in href:
                    all_links.append((text, href))
            # 翻页
            try:
                next_btn = self.driver.find_element(By.CLASS_NAME, "ant-pagination-next")
                if next_btn.get_attribute("aria-disabled") == "true":
                    break
                else:
                    next_btn.click()
                    time.sleep(5)
            except:
                break
        return all_links

    def study_chapter(self):
        """学习单个章节/小节"""
        try:
            menu_container = self.driver.find_element(By.CSS_SELECTOR, "div.menu-container")
            chapters = menu_container.find_elements(By.CSS_SELECTOR, "div.chapter-container.chapter-item")[:-1]
            sections = menu_container.find_elements(By.CSS_SELECTOR, "div.chapter-container.chapter-section-item")

            # 判断是否是大章节（有子小节）
            if len(sections) > 0 :
                for sid, section in enumerate(sections, start=1):
                    menu_container = self.driver.find_element(By.CSS_SELECTOR, "div.menu-container")
                    sections = menu_container.find_elements(By.CSS_SELECTOR,"div.chapter-container.chapter-section-item")
                    title = sections[sid - 1].find_element(By.CSS_SELECTOR, ".node-name-con").text.strip()
                    print(f"📂 进入大章节: {title}")
                    section_list = sections[sid - 1].find_elements(By.CSS_SELECTOR, ".section-container .node-item")
                    time.sleep(1)
                    sections[sid - 1].click()
                    # 找到子小节
                    for sec_idx, section_sec in enumerate(section_list, start=1):
                        menu_container = self.driver.find_element(By.CSS_SELECTOR, "div.menu-container")
                        sections = menu_container.find_elements(By.CSS_SELECTOR,"div.chapter-container.chapter-section-item")
                        sec_list = sections[sid - 1].find_elements(By.CSS_SELECTOR, ".section-container .node-item")
                        sec_title = sec_list[sec_idx - 1].find_element(By.CSS_SELECTOR, ".node-name-con").text.strip()
                        print(f"➡ 学习子小节 {sec_idx}: {sec_title}")
                        sec_list[sec_idx - 1].click()
                        self.play_video(sec_title, 2, sec_idx, sid)

            if len(chapters) > 0:
                for idx, chapter in enumerate(chapters, 1):
                    menu_container = self.driver.find_element(By.CSS_SELECTOR, "div.menu-container")
                    chapters = menu_container.find_elements(By.CSS_SELECTOR, "div.chapter-container.chapter-item")[:-1]
                    title = chapters[idx - 1].find_element(By.CSS_SELECTOR, ".node-name-con").text.strip()
                    # 判断是否完成
                    if "chapter-finish" in chapters[idx - 1].get_attribute("class"):
                        status = "已完成 ✅"
                        print(title, status)
                    else:
                        status = "未完成 ⭕"
                        print(title, status, "现在即将学习......")
                        chapters[idx - 1].click()
                        self.play_video(title, 1, idx, 0)
        except Exception as e:
            print(f"⚠️ 小节异常，跳过: {e}")

    def play_video(self, title, ctype, index, sid):
        """通用视频播放逻辑"""
        try:
            # 点击播放按钮
            try:
                play_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "xg-start .xgplayer-icon-play"))
                )
                play_btn.click()
            except:
                play_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "xg-play .xgplayer-icon-play"))
                )
                play_btn.click()
            print(f"▶ {title} 播放中...")

            # 模拟学习
            while True:
                time.sleep(random.uniform(5, 8))
                self.handle_popup()
                # 判断是什么类型的课程 section or chapter
                menu_container = self.driver.find_element(By.CSS_SELECTOR, "div.menu-container")
                if ctype == 1:
                    chapters = menu_container.find_elements(By.CSS_SELECTOR, "div.chapter-container")
                    if "chapter-finish" in chapters[index - 1].get_attribute("class"):
                        print(f"✅ {title} 已完成")
                        break
                else:
                    sections = menu_container.find_elements(By.CSS_SELECTOR, "div.chapter-container.chapter-section-item")
                    section_list = sections[sid - 1].find_elements(By.CSS_SELECTOR, ".section-container .node-item")
                    # 检查是否完成
                    if len(section_list[index - 1].find_elements(By.CSS_SELECTOR, "div.status-con.section-finish")) == 1:
                        print(f"✅ {title} 已完成")
                        break

        except Exception as e:
            print(f"⚠️ {title} 播放失败: {e}")

    def study_course(self, href):
        """学习单个课程"""
        self.driver.execute_script("window.open(arguments[0]);", href)
        time.sleep(5)
        # 切换到新标签页操作
        self.driver.switch_to.window(self.driver.window_handles[-1])
        try:
            if self.have_cretificate():
                print("该课程已完成！")
            else:
                self.driver.switch_to.window(self.driver.window_handles[-1])

                h1_text = self.driver.find_element(By.TAG_NAME, "h1").text

                study_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.course-study-button"))
                )

                study_btn.click()
                print(f"🎓 开始学习课程: {h1_text}")
                time.sleep(5)
                finished_num, total_num = self.get_progress()
                if finished_num >= total_num:
                    print(f"✅ 课程 {h1_text} 已完成")
                else:
                    self.study_chapter()

        except Exception as e:
            print(f"⚠️ 课程异常，跳过: {href}, 错误: {e}")
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])


if __name__ == "__main__":
    bot = AutoCourseBot(USERNAME, PASSWORD)
    bot.login()
    links = bot.get_all_course_links()
    for t, href in links:
        bot.study_course(href)
