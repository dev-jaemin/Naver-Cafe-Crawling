from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

import pyperclip
import csv
import re
import time
from kiwipiepy import Kiwi
from preprocessing import Preprocessing


class NaverCafe:
    def __init__(self, name, clubid):
        self.name = name
        self.clubid = clubid
        self.driver = Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(f"https://cafe.naver.com/{name}")
        self.preprocessing = Preprocessing()

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

        while len(elements) == 0:
            time.sleep(0.01)
            elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)

            continue

        return elements

    def get_article_ids(self, menuid, num_page):
        boardtype = 'L'
        userDisplay = 50
        articleid_list = []

        for page in range(1, num_page + 1):
            pageurl = f"https://cafe.naver.com/{self.name}?iframe_url=/ArticleList.nhn%3Fsearch.clubid={self.clubid}%26search.menuid={menuid}%26userDisplay={str(userDisplay)}%26search.boardtype={boardtype}%26search.specialmenutype=%26search.totalCount=62%26search.cafeId=30853297%26search.page={str(page)}"

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

    def get_articles(self, menuid, article_ids):
        boardtype = 'L'
        page = 1

        article_file = open(f"{menuid}_article.csv", 'w',
                            encoding="utf-8", newline='')
        article_wr = csv.writer(article_file)

        qna_file = open(f"{menuid}_qna.csv", 'w', encoding="utf-8", newline='')
        qna_wr = csv.writer(qna_file)

        for article_id in article_ids:
            pageurl = f"https://cafe.naver.com/mbticafe?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D{self.clubid}%2526page%3D{page}%2526menuid%3D{menuid}%2526boardtype%3D{boardtype}%2526articleid%3D{article_id}%2526referrerAllArticles%3Dfalse"
            self.driver.get(pageurl)
            self.driver.switch_to.frame("cafe_main")

            (article_id, content, label_nickname) = self._get_content(article_id)

            # Only labeled nicknames are saved
            if label_nickname:
                article_wr.writerow([article_id, content, label_nickname])

            (question, answer, label_answer_nickname) = self._get_QNA()
            # If no reple, do not save
            if question:
                qna_wr.writerow([question, answer, label_answer_nickname])

        print(f"menu : {menuid}'s {len(article_ids)} articles download done.")

        article_file.close()
        qna_file.close()

    def _get_content(self, article_id):
        article_element = self._getElementsAfterWaiting(".article_viewer")[0]

        # for double(or more) \n -> single \n
        content = re.sub("\n+", "\n", article_element.text.strip())

        nickname = self._getElementsAfterWaiting(
            "button.nickname")[0].text.strip()
        label_nickname = self.preprocessing.label_nickname(nickname)

        return (
            article_id,
            content,
            label_nickname
        )

    def _get_QNA(self):
        kiwi = Kiwi()

        article_element = self._getElementsAfterWaiting(
            "div.article_viewer")[0]
        comment_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "span.text_comment")
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
                    kiwi.split_into_sents(content), 3)
                answer = self.preprocessing.first_n_sentences(
                    kiwi.split_into_sents(comment), 2)
                label_nickname = self.preprocessing.label_nickname(nickname)

                if label_nickname:
                    return (
                        question,
                        answer,
                        label_nickname
                    )
                else:
                    raise ValueError
            else:
                raise ValueError
        except:
            return (None, None, None)
