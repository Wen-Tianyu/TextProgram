"""
新闻聚类验证之前得到的tf-idf新闻向量的合理性
"""
from sklearn.cluster import k_means
import numpy as np
from munkres import Munkres
import pandas as pd


def map_labels(true_labels, gen_labels):
    """
    最优匹配聚类结果和真实标签
    :param true_labels: list[int] 真实标签
    :param gen_labels: list[int] 聚类结果生成标签
    :return: list[int] 最优匹配后的生成标签
    """
    Label1 = np.unique(true_labels)
    Label2 = np.unique(gen_labels)
    nClass = len(Label1)
    G = np.zeros((nClass, nClass))
    for i in range(nClass):
        for j in range(nClass):
            G[i, j] = np.sum((true_labels == Label1[i]).astype(float) * (gen_labels == Label2[j]).astype(float))

    m = Munkres()
    index = np.array(m.compute(-G.T))
    new_labels = np.zeros(gen_labels.shape, dtype=int)
    for i in range(nClass):
        for j in range(len(gen_labels)):
            if gen_labels[j] == index[i, 0]:
                new_labels[j] = index[i, 1]

    return new_labels


def purity(true_labels, gen_labels):
    """
    聚类结果纯度计算
    :param true_labels: list[int] 真实标签
    :param gen_labels: list[int] 生成标签
    :return: 纯度值
    """
    gen_labels = np.array(gen_labels)
    true_labels = np.array(true_labels).reshape(-1)
    id1 = {}
    for i in np.unique(true_labels):
        id1[i] = np.argwhere(true_labels == i)
    id2 = {}
    for j in np.unique(gen_labels):
        id2[j] = np.argwhere(gen_labels == j)

    intersecs_num_all = []
    for i in id1.values():
        intersecs_num = []
        for j in id2.values():
            a = len(np.intersect1d(i, j))
            intersecs_num.append(a)
        intersecs_num_all.append(intersecs_num)

    return sum(np.max(intersecs_num_all, axis=0)) / len(gen_labels)


# 根据PCA降维后的新闻向量做K-means聚类
label_dict = {'business': 0, 'entertainment': 1, 'politics': 2, 'sport': 3, 'tech': 4}
PCAed_tfidf_matrix = np.load('./PCAed_tfidf_matrix.npy')
_, y_pred, _ = k_means(PCAed_tfidf_matrix, len(label_dict))

# 加载真实标签(topic)
df = pd.read_csv('./all_news.csv')
topics = df['topic'].values.tolist()
y_true = np.array([label_dict[topic] for topic in topics])

# 最优标签匹配
mapped_y_pred = map_labels(y_true, y_pred)

# 计算聚类结果纯度
purity_value = purity(y_true, mapped_y_pred)
print(purity_value)
