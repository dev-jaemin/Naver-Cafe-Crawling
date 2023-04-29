from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

import pyperclip
import re
import time
from kiwipiepy import Kiwi
from preprocessing import Preprocessing
from db_helper import ConnectionPool
import os


class NaverCafe:
    def __init__(self, name, clubid):
        self.name = name
        self.clubid = clubid
        self.driver = Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(f"https://cafe.naver.com/{name}")
        self.preprocessing = Preprocessing()
        self.pool = ConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_DATABASE']
        )
        self.kiwi = Kiwi()

    def enter_id_pw(self, userid, userpw):
        self.driver.get('https://nid.naver.com/nidlogin.login')

        div_id = self.driver.find_element(By.ID, 'id')
        div_id.click()
        pyperclip.copy(userid)
        div_id.send_keys(Keys.CONTROL, 'v')

        div_pw = self.driver.find_element(By.ID, 'pw')
        div_pw.click()
        pyperclip.copy(userpw)
        div_pw.send_keys(Keys.CONTROL, 'v')

        self.driver.find_element(By.ID, 'log.login').click()

    def _getElementsAfterWaiting(self, css_selector):
        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        t = 0

        # 찾거나, 일정 시간이 지나면 반복문 정지
        while len(elements) == 0 and t < 2:
            time.sleep(0.01)
            elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
            t += 0.01

        return elements

    def get_article_ids(self, menu_id, num_page):
        boardtype = 'L'
        userDisplay = 50
        articleid_list = []

        for page in range(1, num_page + 1):
            pageurl = f"https://cafe.naver.com/{self.name}?iframe_url=/ArticleList.nhn%3Fsearch.clubid={self.clubid}%26search.menuid={menu_id}%26userDisplay={str(userDisplay)}%26search.boardtype={boardtype}%26search.specialmenutype=%26search.totalCount=62%26search.cafeId=30853297%26search.page={str(page)}"

            self.driver.get(pageurl)

            # for iframe
            self.driver.switch_to.frame("cafe_main")

            table_rows = self._getElementsAfterWaiting(
                '.article-board > table > tbody > tr')
            contents = []
            for row in table_rows:
                # 공지, 추천글 제외
                try:
                    contents.append({
                        "inner_number": int(row.find_element(By.CSS_SELECTOR, '.inner_number').text.strip()),
                        "comment": row.find_element(By.CSS_SELECTOR, '.inner_number') != None,
                        "nickname": self.preprocessing.label_nickname(row.find_element(By.CSS_SELECTOR, '.pers_nick_area').text.strip())
                    })
                except NoSuchElementException:
                    continue

            # append candidate contents if there is a comment or a nickname which has mbti keywords
            articleid_list.extend([content["inner_number"]
                                  for content in contents if content["comment"] or content["nickname"]])

        return articleid_list

    def get_articles(self, menu_id, article_ids):
        boardtype = 'L'
        page = 1

        for count, article_id in enumerate(article_ids):
            pageurl = f"https://cafe.naver.com/mbticafe?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D{self.clubid}%2526page%3D{page}%2526menu_id%3D{menu_id}%2526boardtype%3D{boardtype}%2526articleid%3D{article_id}%2526referrerAllArticles%3Dfalse"
            self.driver.get(pageurl)
            self.driver.switch_to.frame("cafe_main")

            qnas = []
            comments = []

            qna = self._get_QNA(article_id, menu_id)
            # If no reple, do not save
            if qna[2]:
                qnas.append(qna)

            comments = comments + self._get_comments(article_id, menu_id)

            # 100개 단위로 DB에 저장
            if count % 100:
                self.insert_qna_to_DB(qnas)
                self.insert_comments_to_DB(comments)

                qnas.clear()
                comments.clear()

            if len(qnas) > 0:
                self.insert_qna_to_DB(qnas)
                qnas.clear()

            if len(comments) > 0:
                self.insert_comments_to_DB(comments)
                comments.clear()

        print(f"menu : {menu_id}'s {len(article_ids)} articles download done.")

    def _get_QNA(self, article_id, menu_id):
        article_element = self._getElementsAfterWaiting(
            "div.article_viewer")[0]
        comment_elements = self._getElementsAfterWaiting("span.text_comment")
        comment_element = comment_elements[0] if len(
            comment_elements) > 0 else None

        try:
            if comment_element:
                # for double(or more) \n -> single \n
                content = re.sub("\n+", "\n", article_element.text.strip())
                comment = re.sub("\n+", "\n", comment_element.text.strip())
                nickname = self._getElementsAfterWaiting(
                    "div.comment_nick_info")[0].text.strip()

                # For using only first/last n sentences.
                # If you want to change n, change 100 to other number you want. (I recommend last_n = 3, first_n = 2)
                question = self.preprocessing.last_n_sentences(
                    self.kiwi.split_into_sents(content), 3)
                answer = self.preprocessing.first_n_sentences(
                    self.kiwi.split_into_sents(comment), 2)
                label_nickname = self.preprocessing.label_nickname(nickname)

                if label_nickname:
                    return (
                        article_id,
                        menu_id,
                        question,
                        answer,
                        label_nickname
                    )
                else:
                    raise ValueError
            else:
                raise ValueError
        except:
            return (None, None, None, None, None)

    def _get_comments(self, article_id, menu_id):
        comments = []

        comment_elements = self._getElementsAfterWaiting("span.text_comment")

        for comment_element in comment_elements:
            if comment_element:
                # for double(or more) \n -> single \n
                text = re.sub("\n+", "\n", comment_element.text.strip())
                nickname = self._getElementsAfterWaiting(
                    "div.comment_nick_info")[0].text.strip()

                text = self.preprocessing.first_n_sentences(
                    self.kiwi.split_into_sents(text), 2)
                label_nickname = self.preprocessing.label_nickname(
                    nickname)

                if label_nickname:
                    comments.append((
                        article_id,
                        menu_id,
                        text,
                        label_nickname
                    ))

        return comments

    def insert_qna_to_DB(self, data):
        # 데이터 INSERT
        table_name = "qna"
        columns = ["article_id", "menu_id", "q", "a", "mbti"]
        self.pool.insert_data(table_name, columns, data)

    def insert_comments_to_DB(self, data):
        # 데이터 INSERT
        table_name = "comment"
        columns = ["article_id", "menu_id", "text", "mbti"]
        self.pool.insert_data(table_name, columns, data)
