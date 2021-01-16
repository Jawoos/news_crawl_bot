import re
from konlpy.tag import Okt
from konlpy.tag import Twitter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import numpy as np


# Window 의 한글 폰트 설정
# plt.rc('font', family='Malgun Gothic')
# Mac 의 한글 폰트 설정
# plt.rc('font', family='AppleGothic')


def cos_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    l2_norm = (np.sqrt(sum(np.square(v1))) * np.sqrt(sum(np.square(v2))))
    similarity = dot_product / l2_norm

    return similarity


def sub_special(s):  # 한글, 숫자, 영어 빼고 전부 제거
    return re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣0-9a-zA-Z ]', '', s)


def morph_and_stopword(s):
    okt = Okt()
    token_ls = []
    temp_str = ""
    STOP_WORDS = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']
    tmp = okt.morphs(s, stem=True)  # 형태소 분석
    for token in tmp:  # 불용어 처리
        if token not in STOP_WORDS:
            token_ls.append(token)
            temp_str += (token + ' ')
    return temp_str


def max_search(list_s):
    maxValue = 0
    for i in list_s:
        if maxValue < i:
            maxValue = i
    return maxValue


def compare_title(title_list, title_str):
    temp_title_list = title_list
    one_title = morph_and_stopword(sub_special(title_str))
    temp_title_list.append(one_title)
    np_arr = np.array(title_list)
    vect = TfidfVectorizer()
    np_arr = vect.fit_transform(np_arr)
    cosine_similarity_matrix = (np_arr * np_arr.T)
    cosine_similarity_matrix = cosine_similarity_matrix.toarray()[cosine_similarity_matrix.shape[0] - 1]
    cosine_similarity_matrix = cosine_similarity_matrix.tolist()
    cosine_similarity_matrix = cosine_similarity_matrix[:len(cosine_similarity_matrix) - 1]
    # print(cosine_similarity_matrix)
    return max_search(cosine_similarity_matrix)


# doc_list = ["현대 GV80 신차 실내공기 불량...'톨루엔' 권고기준 초과",
#             "베일 벗기 시작하는 현대 핵심 전기차 아이오닉 5···티저 이미지 공개",
#             "美 세단 최강 ‘우뚝’…현대차 아반떼, ‘북미 올해의 차’ 수상",
#             "비대면으로 SUV 흥행 잇는다… 인도 질주하는 현대차"]
#
#
#
# title_list0 = []
# for title in doc_list:
#     temp_title = sub_special(title)
#     title_list0.append(morph_and_stopword(temp_title))
#
# compare_title(title_list0, "현대 아반떼, 2021년 '북미 올해의 차’ 수상")