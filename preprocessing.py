class Preprocessing:
    def label_nickname(self, nickname):
        # E - I | N - S | F - T | J - P (alphabet order)
        MBTI_LIST = ["enfj", "enfp", "entj", "entp", "esfj", "esfp", "estj", "estp", "infj", "infp", "intj", "intp", "isfj", "isfp", "istj", "istp"]
        MBTI_KEYWORDS = {
            "엔프제": "enfj",
            "엔프피": "enfp",
            "엥쁘삐": "enfp",
            "엥뿌삐": "enfp",
            "엥뿌피": "enfp",
            "엥쁘피": "enfp",
            "엔티제": "entj", 
            "엔팁": "entp", 
            "엣프제": "esfj", 
            "엣프피": "esfp", 
            "엣티제": "estj", 
            "엣팁": "estp", 
            "인프제": "infj", 
            "인프피": "infp", 
            "인티제": "intj", 
            "인팁": "intp", 
            "잇프제": "isfj", 
            "잇프피": "isfp", 
            "잇티제": "istj", 
            "잇팁": "istp"
        }

        lower_nickname = nickname.lower()

        # searching English mbti substring
        for mbti in MBTI_LIST:
            if lower_nickname.find(mbti) != -1:
                return mbti
            
        # if not, searching Korean mbti keyword
        for keyword in MBTI_KEYWORDS.keys():
            if nickname.find(keyword) != -1:
                return MBTI_KEYWORDS[keyword]
        
        # if there is no keywords, return False
        return False

    def last_n_sentences(self, sentences, n):
        last_n_tuple = sentences[(-1) * n:]

        return '[SEP]'.join([t.text for t in last_n_tuple]) + '[SEP]'

    def first_n_sentences(self, sentences, n):
        first_n_tuple = sentences[:n]
        
        return '[SEP]'.join([t.text for t in first_n_tuple]) + '[SEP]'