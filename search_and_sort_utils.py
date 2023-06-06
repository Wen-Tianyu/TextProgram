"""
检索和排序需要用到的工具函数
"""

import os

import networkx as nx
import numpy as np


def hitsrank_by_news_list(news_list):
    """
    根据新闻的tf-idf向量的余弦相似度构建有权重无向图，在图上运行hits算法得到新闻排序结果
    :param news_list: list[int] 检索得到的待排序新闻下标列表
    :return: list[int] 根据hits算法按重要性排序后的新闻下标列表
    """
    PCAed_tfidf_matrix = np.load('./PCAed_tfidf_matrix.npy')[news_list, :]
    dot_matrix = np.matmul(PCAed_tfidf_matrix, PCAed_tfidf_matrix.T)
    news_vec_norm = np.linalg.norm(PCAed_tfidf_matrix, axis=1, keepdims=True)
    norm_mul_matrix = np.matmul(news_vec_norm, news_vec_norm.T)
    cosine_similarity_matrix = dot_matrix / norm_mul_matrix
    np.save('./news_cosine_similarity_matrix.npy', cosine_similarity_matrix)

    G = nx.from_numpy_matrix(cosine_similarity_matrix)
    _, page_list = nx.hits(G, max_iter=10000)
    return [news_list[i[1]] for i in sorted(zip(page_list.values(), page_list.keys()), reverse=True)]


def find_news_list_by_word(word):
    """
    :param word: str 要检索的词汇
    :return: list[int] 包含该词汇的所有新闻的下标组成的列表
    """
    f = open('./vocab.txt')
    words_list = f.read().splitlines()
    words_list_len = len(words_list)
    f.close()
    words_list_dict = dict(zip(words_list, range(words_list_len)))

    if word not in words_list:
        print('No such word {} in vocabulary.'.format(word))
        return []
    else:
        word_idx = words_list_dict[word]
        tfidf_matrix = np.load('./tfidf_matrix.npy')
        news_idx_vec = tfidf_matrix[:, word_idx].reshape(-1)
        return sorted(np.where(news_idx_vec != 0)[0].tolist())


def find_news_list_by_words_list(words_list):
    """
    :param words_list: list[str] 要检索的词汇列表
    :return: list[int] *同时*包含这些词汇的所有新闻的下标组成的列表
    """
    words_num = len(words_list)
    news_list_intersection = find_news_list_by_word(words_list[0])
    if words_num > 1:
        for word in words_list[1:]:
            news_list_intersection = list(set(news_list_intersection).intersection(set(find_news_list_by_word(word))))
    return sorted(news_list_intersection)


def search_and_sort_by_word(words):
    """
    :param words: str/list[str] 要检索的词汇/词汇列表
    :return: list[int] hits算法排序后的检索结果（新闻下标列表）
    """
    if isinstance(words, str):
        news_idx_list = find_news_list_by_word(words)
    elif isinstance(words, list):
        news_idx_list = find_news_list_by_words_list(words)
    else:
        raise ValueError('Got neither word nor words_list.')

    return hitsrank_by_news_list(news_idx_list)


def get_synonyms(word, k):
    """
    :param word: str 待匹配词语
    :param k: int 匹配相似词数量
    :return: list[str] 相似词列表
    """
    file_path = './synonym.txt'
    if not os.path.exists(file_path):
        raise FileExistsError('No such file saved for k={} before.'.format(k))

    synonym_indices = np.load('./synonym_indices_' + str(k) + '.npy', 'r')
    f = open('./vocab.txt')
    words_list = f.read().splitlines()
    words_list_len = len(words_list)
    f.close()
    words_list_dict = dict(zip(words_list, range(words_list_len)))

    if word not in words_list:
        print('No such word {} in vocabulary.'.format(word))
        return []
    else:
        word_idx = words_list_dict[word]

    synonyms_list = []
    for i in range(1, k + 1):
        synonyms_list.append(words_list[synonym_indices[word_idx, i]])

    return synonyms_list
