"""
计算新闻-词汇的tf-idf值矩阵并对该矩阵PCA降维处理
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

# 根据每篇新闻的所有词汇的tf-idf值构建这篇新闻的词汇向量
def get_poem_vec(x):
    x = x.loc[:, ['word', 'TF-IDF']].values
    vec = np.zeros(words_list_len)
    for word_tfidf in x:
        vec[words_list_dict[word_tfidf[0]]] = word_tfidf[1]
    return pd.DataFrame([[vec]], columns=['news_vec'])


# 读取csv文件
df = pd.read_csv('./tf_idf.csv')

# 读取词汇表
f = open('./vocab.txt')
words_list = f.read().splitlines()
words_list_len = len(words_list)
f.close()
words_list_dict = dict(zip(words_list, range(words_list_len)))

# 获取每篇新闻的词汇向量
poem_vecs = df.groupby('id').apply(get_poem_vec)

# 将所有新闻的词汇向量拼成新闻-词汇矩阵
tfidf_matrix = np.array(poem_vecs['news_vec'].values.tolist())
np.save('./tfidf_matrix.npy', tfidf_matrix)

# PCA降维
n_components = 100
pca = PCA(n_components=n_components)
PCAed_tfidf_matrix = pca.fit_transform(tfidf_matrix)
np.save('./PCAed_tfidf_matrix.npy', PCAed_tfidf_matrix)


