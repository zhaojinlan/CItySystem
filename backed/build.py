import csv

from py2neo import Graph, Node, Relationship, Subgraph
from py2neo.matching import NodeMatcher
import pandas as pd

# 连接neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))
df = pd.read_csv('城市信息.csv')
cities = []

tx = graph.begin()
batch_size = 1000
count = 0

for i in range(df.shape[0]):
    cityname_ = df.iat[i, 1]
    englishname_ = df.iat[i, 2]
    anothername_ = df.iat[i, 3]
    population_ = df.iat[i, 4]
    rgdp_ = df.iat[i, 5]
    car_ = df.iat[i, 6]
    level_ = df.iat[i, 7]
    province_ = df.iat[i, 8]
    cities.append(cityname_)
    if  pd.isnull(englishname_):
        englishname_ = 'Unknown'
    if pd.isnull(anothername_):
        anothername_ = '暂无数据'
    if pd.isnull(population_):
        population_ = '暂无数据'
    if pd.isnull(rgdp_):
        rgdp_ = '暂无数据'
    citynode = Node('城市', name = cityname_, englishname = englishname_, anothername = anothername_, population = population_, rgdp = rgdp_, car = car_)
    graph.create(citynode)

    # 创建节点的关系，此处是将各个城市的城市级别进行匹配
    matcher = NodeMatcher(graph)
    matchresult = list(matcher.match('行政级别', level=level_))
    if len(matchresult) == 0:
        levelnode = Node('行政级别', level=level_)
        graph.create(levelnode)
    else:
        levelnode = matchresult[0]
    graph.create(Relationship(citynode, "属于", levelnode))

    # 创建节点的关系，此处是将各个与其对应的省份进行匹配
    matcher = NodeMatcher(graph)
    matchresult = list(matcher.match('省份', province=province_))
    if len(matchresult) == 0:
        provincenode = Node('省份', province=province_)
        graph.create(provincenode)
    else:
        provincenode = matchresult[0]
    graph.create(Relationship(citynode, "位于", provincenode))

df = pd.read_csv('城市接壤数据.csv')
cities = set(cities)
for i in range(df.shape[0]):
    cityname1 = df.iat[i, 0]
    cityname2 = df.iat[i, 1]
    if cityname1 in cities and cityname2 in cities:
        matcher1 = NodeMatcher(graph)
        matcher2 = NodeMatcher(graph)
        match1 = list(matcher1.match('城市', name = cityname1))[0]
        match2 = list(matcher2.match('城市', name = cityname2))[0]
        graph.create(Relationship(match1, "接壤", match2))
        graph.create(Relationship(match2, "接壤", match1))

