class Preprocessing:
    def label_nickname(self, nickname):
        # E - I | N - S | F - T | J - P (alphabet order)
        MBTI_LIST = ["enfj", "enfp", "entj", "entp", "esfj", "esfp", "estj", "estp", "infj", "infp", "intj", "intp", "isfj", "isfp", "istj", "istp"]
        MBTI_KEYWORDS = self._get_mbti_keywords()

        lower_nickname = nickname.lower()

        # searching English mbti substring
        for mbti in MBTI_LIST:
            if lower_nickname.find(mbti) != -1:
                return mbti
            
        # if not, searching Korean mbti keyword
        for keyword in MBTI_KEYWORDS.keys():
            if nickname.find(keyword) != -1:
                return MBTI_KEYWORDS[keyword]
        
        # if there is no keywords, return None
        return None

    def _get_mbti_keywords(self):
        prefixes = {
            'en': ['엔', '엥'],
            'es': ['엣'],
            'in': ['인', '잉'],
            'is': ['잇']
        }
        suffixes = {
            'fp': ['프피', '뿌피', '뿌삐', '픞', '픕'],
            'fj': ['프제', '픚'],
            'tp': ['팁', '팊', '티피', '티삐'],
            'tj': ['티제', '팆']
        }

        korean_mbti_dic = {}

        for p_eng, p_kors in prefixes.items():
            for s_eng, s_kors in suffixes.items():
                for p in p_kors:
                    for s in s_kors:
                        korean_mbti_dic[p + s] = p_eng + s_eng

        return korean_mbti_dic

    def last_n_sentences(self, sentences, n):
        last_n_tuple = sentences[(-1) * n:]

        return '[SEP]'.join([t.text for t in last_n_tuple]) + '[SEP]'

    def first_n_sentences(self, sentences, n):
        first_n_tuple = sentences[:n]
        
        return '[SEP]'.join([t.text for t in first_n_tuple]) + '[SEP]'