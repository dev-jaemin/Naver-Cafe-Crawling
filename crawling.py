import dotenv
import os
from navercafe import NaverCafe

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# 1. setup
cafe_name = os.environ['CAFE_NAME']
club_id = os.environ['CAFE_ID']
cafe = NaverCafe(cafe_name, club_id)

# 2. (optional) enter user id and pw
# This is semi-automatic (needs manual authentication)
cafe.enter_id_pw(os.environ['NAVER_ID'], os.environ['NAVER_PW'])

board_ids = [11]
for board_id in board_ids:
    # 3. get article board ids
    article_ids = cafe.get_article_ids(board_id, 500)

    # 4. get articles, QNA
    cafe.get_articles(board_id, article_ids)
