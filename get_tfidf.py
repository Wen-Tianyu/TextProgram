"""
计算所有新闻中所有词汇的tf-idf值
"""

import pandas as pd
import numpy as np

# 读取csv文件
df = pd.read_csv('./words_in_news.csv')

# 统计词语在每篇新闻中的出现次数
news_word_count = df.groupby(['id', 'word']).count()
del news_word_count['level_1']
news_word_count.columns = ['cnt_word']

# 统计每篇新闻的词语数目
news_words_count = df.groupby('id').count()
del news_words_count['word']
del news_words_count['level_1']
news_words_count.columns = ['cnt_words']

# 计算TF值
df = pd.merge(df, news_word_count, on=['id', 'word'])
df = pd.merge(df, news_words_count, on=['id'])
df['TF'] = df['cnt_word'] / df['cnt_words']
del df['cnt_word']
del df['cnt_words']
df_unique = df.drop_duplicates(subset=['id', 'word'])
word_news = df_unique.groupby('word').count()
del word_news['TF']
del word_news['id']
del word_news['level_1']
word_news.columns = ['word_news']

# 计算IDF值
df = pd.merge(df, word_news, on='word')
df.sort_values(by=['id', 'level_1'], inplace=True)
df['IDF'] = np.log(2225 / df['word_news'])

# 计算TF-IDF值
df['TF-IDF'] = df['TF'] * df['IDF']

# 将新闻id、词语位置、词语、TF值、IDF值、TF-IDF值保存为csv文件
df = df.loc[:, ['id', 'level_1', 'word', 'TF', 'IDF', 'TF-IDF']]
df.to_csv('./tf_idf.csv')
