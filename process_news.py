"""
新闻数据预处理（大小写转换、停用词、分词、去除低频词、词形统一化）并构建词汇表
"""

import copy
import re
from collections import Counter
import pandas as pd
from nltk.stem import WordNetLemmatizer


def all_to_lower(s):
    return re.sub('[^A-Za-z]+', ' ', s).lower()


def remove_stopwards(s):
    s = s.split(' ')
    return ' '.join(z for z in s if z not in stop_words)


# 读取csv文件
df = pd.read_csv('all_news.csv')

# 全部字母转换为小写
df['body'] = df['body'].astype(str).apply(all_to_lower)

# 去除停用词
with open('./english_stopwords', 'r') as f:
    stop_words = f.readlines()
stop_words = set(i.strip('\n') for i in stop_words)
df['body'] = df['body'].astype(str).apply(remove_stopwards)
df.to_csv('./processed_news.csv')

# 将成句新闻分词
words_df = df['body'].str.split(' ', expand=True).stack().rename('word').reset_index()
df = pd.merge(df, words_df, left_index=True, right_on='level_0').drop(
    columns=['level_0', 'title', 'body', 'topic'])

# 词形统一化
words = df['word'].values.tolist()
lemmatizer = WordNetLemmatizer()
for i in range(len(words)):
    words[i] = lemmatizer.lemmatize(words[i])
df['word'] = words

# 删除低频词
word_min_times = 3
words_ct = Counter(words)
new_words_ct = copy.deepcopy(words_ct)
for i in words_ct:
    if words_ct[i] < word_min_times:
        del new_words_ct[i]

# 构建并保存词汇表
words_list = sorted(list(new_words_ct))
with open('./vocab.txt', 'w') as f:
    for word in words_list:
        if word == '':
            continue 
        print(word, file=f)

# 将去除低频词后的dataframe保存为csv文件
words = df['word'].values.tolist()
mask = []
for word in words:
    mask.append(True if word in words_list else False)
df = df[mask]
df.to_csv('./words_in_news.csv')


