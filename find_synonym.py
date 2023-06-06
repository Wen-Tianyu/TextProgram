"""
寻找相似词
"""
import numpy as np
from sklearn.decomposition import PCA

# 获取单词向量（即新闻向量stack成的tf-idf矩阵的转置）
tfidf_matrix = np.load('./tfidf_matrix.npy')
word_vectors_matrix = tfidf_matrix.T

# 对单词向量做PCA降维方便后续处理
n_components = 100
pca = PCA(n_components=n_components)
PCAed_word_vectors_matrix = pca.fit_transform(word_vectors_matrix)

# 计算单词的余弦相似度矩阵
dot_matrix = np.matmul(word_vectors_matrix, word_vectors_matrix.T)
word_vec_norm = np.linalg.norm(word_vectors_matrix, axis=1, keepdims=True)
norm_mul_matrix = np.matmul(word_vec_norm, word_vec_norm.T) + 1e-9
cosine_similarity_matrix = dot_matrix / norm_mul_matrix

# 将相似度排序，把除自身以外和该词相似度前k大的词汇视为该词的相似词，保存对应下标到文件中
synonym_words_num = 2
synonym_indices = np.argsort(-cosine_similarity_matrix, axis=-1)[:, :(synonym_words_num + 1)]
np.save('./synonym_indices_' + str(synonym_words_num) + '.npy', synonym_indices)

# 加载词汇表
f = open('./vocab.txt')
words_list = f.read().splitlines()
words_list_len = len(words_list)
f.close()

# 保存相似词的txt格式文件(主要是方便预览相似词识别结果）
with open('./synonym.txt', 'w') as f:
    for i in range(words_list_len):
        print(words_list[i], end=': ', file=f)
        for j in range(1, synonym_words_num + 1):
            print(words_list[synonym_indices[i, j]], end=' ', file=f)
        print(file=f)
