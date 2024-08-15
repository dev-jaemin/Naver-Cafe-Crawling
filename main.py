import dotenv
import os
from navercafe import NaverCafe

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

board_ids = [int(n) for n in input("크롤링하고 싶은 게시판의 id를 띄어쓰기로 구분해서 입력해주세요(ex. 11 12 13) : ").split()]
page_count = int(input("크롤링 진행할 페이지 수를 지정해주세요. 시간이 오래 걸리니 우선 작은 숫자로 시작해보는건 어떨까요? : "))

# 1. setup
cafe_name = os.environ['CAFE_NAME']
club_id = os.environ['CAFE_ID']
cafe = NaverCafe(cafe_name, club_id)

# 2. (optional) enter user id and pw
# This is semi-automatic (needs manual authentication)
cafe.enter_id_pw(os.environ['NAVER_ID'], os.environ['NAVER_PW'])

for board_id in board_ids:
    # 3. get article board ids
    article_ids = cafe.get_article_ids(board_id, page_count)

    # 4. get articles, QNA
    cafe.get_articles(board_id, article_ids)
