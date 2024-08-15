# 네이버 카페 댓글 크롤링 코드

- 네이버 카페의 댓글을 크롤링해서 문답 형식의 데이터를 만드는 코드입니다.
- 게시글이 질문, 댓글이 답변으로 저장됩니다.
- 한 게시글에 여러 댓글이 달리는 경우, 질문 - 댓글 쌍 하나하나가 row로 저장됩니다.

## 사용법
1. PostgreSQL 준비

이 코드는 실행시간이 매우 길기 때문에, 파일시스템이 아닌 DBMS를 사용합니다.

이 코드는 psql 기반으로 작성되었으며, 14버전에서 잘 작동하는 것을 확인했습니다.

2. 필요 라이브러리들 설치

```
pip3 install requiremets.txt
```

3. `.env` 파일 수정

코드를 실행하는데 필요한 설정 파일입니다.

본인 네이버 아이디, 비밀번호 및 1에서 준비한 PostgreSQL 서버와의 접속 정보를 작성하셔야 합니다. (주석 처리 해제 후 작성)

DB는 각자 실행 환경에 맞추어 적절히 수정하시면 됩니다.

- CAFE_NAME 아는 방법

- CAFE_ID 아는 방법

ex
```
CAFE_NAME=mbticafe
CAFE_ID=11856775
NAVER_ID=exampleid
NAVER_PW=examplepw

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=examplepw
DB_DATABASE=crawling
```

4. `main.py` 실행
    - 크롤링하고 싶은 게시판 id를 공백을 구분자로 입력하시면 됩니다.(ex. 11 12 13)
        - 게시판 id 아는 방법
    - 게시판당 크롤링하고 싶은 페이지 수를 입력하세요.

5. 결과 확인
    - 1에서 준비한 postgresql 서버에 접속하면 확인하실 수 있습니다.
        - DB 이름 : crawling
        - 테이블 이름 : multiple_qna