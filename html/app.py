from flask import Flask, jsonify, render_template, request
from py2neo import Graph
import json
import spacy
from flask import jsonify
from flask import jsonify, request

app = Flask(__name__)


# 连接 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))



@app.route('/')
def index():
    return render_template('index.html')

def load_city_data():
    query = "MATCH (n:城市) RETURN n"
    data = graph.run(query)
    cities = []
    for record in data:
        cities.append(record['n'])
    return cities

def process_properties(properties):
    processed_props = {}
    for key, value in properties.items():
        if isinstance(value, str):
            try:
                # 尝试解析为JSON字符串来处理Unicode转义
                decoded_value = json.loads(f'"{value}"')
                processed_props[key] = decoded_value
            except json.JSONDecodeError:
                processed_props[key] = value
        else:
            processed_props[key] = value
    return processed_props

@app.route('/get_graph_data')
def get_graph_data():
    # 获取查询参数
    query_city = request.args.get('city', '')

    # 如果有查询城市，就查询相关联的节点和关系
    if query_city:
        query = """
        MATCH (n)-[r]->(m)
        WHERE n.name CONTAINS $query OR m.name CONTAINS $query
        RETURN n, r, m
        UNION
        MATCH (n)-[r]->(m)
        WHERE n.englishname CONTAINS $query OR m.englishname CONTAINS $query
        RETURN n, r, m
        UNION
        MATCH (n)-[r]->(m)
        WHERE n.anothername CONTAINS $query OR m.anothername CONTAINS $query
        RETURN n, r, m
        """
        data = graph.run(query, query=query_city)
    else:
        # 否则返回整个图谱的根节点和部分连接
        query = """
        MATCH (n)
        WHERE n:行政级别 OR n:省份
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        data = graph.run(query)

    # 构建节点和边的数据结构
    nodes = []
    edges = []
    node_set = set()

    for record in data:
        # 处理节点n的属性
        n_node = record['n']
        n_props = process_properties(dict(n_node))
        n_label = n_props.get('name', n_props.get('level', n_props.get('province', '未知')))

        if n_node not in node_set:
            node_set.add(n_node)
            nodes.append({
                'id': str(n_node.identity),
                'label': n_label,
                'title': f"类型: {list(n_node.labels)[0]}<br>{json.dumps(n_props, ensure_ascii=False)}",
                'group': list(n_node.labels)[0]
            })

        # 处理节点m（如果存在）
        m_node = record.get('m')
        if m_node:
            m_props = process_properties(dict(m_node))
            m_label = m_props.get('name', m_props.get('level', m_props.get('province', '未知')))

            if m_node not in node_set:
                node_set.add(m_node)
                nodes.append({
                    'id': str(m_node.identity),
                    'label': m_label,
                    'title': f"类型: {list(m_node.labels)[0]}<br>{json.dumps(m_props, ensure_ascii=False)}",
                    'group': list(m_node.labels)[0]
                })

        # 处理边
        if 'r' in record and record['r'] is not None:
            edges.append({
                'from': str(n_node.identity),
                'to': str(m_node.identity),
                'label': type(record['r']).__name__,
                'arrows': 'to'
            })

    return jsonify({'nodes': nodes, 'edges': edges})

# # 问答系统 API
# @app.route('/qa', methods=['GET'])
# def qa():
#     """"
#     方案一
#     """
#     user_input = request.args.get('question', '')
#     cities = load_city_data()
#
#     # 提取城市名称
#     city_name = user_input.split("的")[0]
#
#     # 确定关键词
#     if "人口数量" in user_input or "人口" in user_input:
#         keyword = "population"
#     elif "地区生产总值" in user_input or "GDP" in user_input:
#         keyword = "GDP"
#     elif "车牌号" in user_input:
#         keyword = "car"
#     elif "行政级别" in user_input:
#         keyword = "行政级别"
#     elif "省份" in user_input:
#         keyword = "省份"
#     elif "英文名" in user_input:
#         keyword = "englishname"
#     elif "别名" in user_input:
#         keyword = "anothername"
#     else:
#         return jsonify({'answer': "抱歉，我不太明白你的问题。请尝试以下问题：某个城市的人口数量、地区生产总值、车牌号、行政级别、省份、英文名或别名。"})
#
#     # 查找城市信息
#     for city in cities:
#         if city['name'] == city_name:
#             answer = city.get(keyword, "信息未提供")
#             return jsonify({'answer': f"{city_name}的{keyword}是：{answer}"})
#
#     return jsonify({'answer': "抱歉，没有找到相关信息。"})



from flask import jsonify, request

# 预定义关键词到字段的映射表（支持同义词扩展）
KEYWORD_MAPPING = {
    "人口": "population",
    "常住人口": "population",
    "人口数量": "population",
    "GDP": "GDP",
    "地区生产总值": "GDP",
    "经济总量": "GDP",
    "车牌": "car",
    "车牌号": "车牌号",
    "行政级别": "行政级别",
    "级别": "行政级别",
    "所属省份": "省份",
    "省份": "省份",
    "英文名称": "englishname",
    "英文名": "englishname",
    "别称": "anothername",
    "别名": "anothername"
}


def recognize_city_entity(text, cities):
    """城市实体识别（支持包含市/县等后缀）"""
    # 按名称长度降序排序，优先匹配长名称（如"北京市"优先于"北京"）
    sorted_cities = sorted(cities, key=lambda x: -len(x['name']))
    for city in sorted_cities:
        if city['name'] in text:
            return city['name']
    return None


def recognize_keyword_entity(text):
    """关键词实体识别（支持多词表达）"""
    # 按关键词长度降序匹配，避免短词误匹配
    for keyword in sorted(KEYWORD_MAPPING.keys(), key=lambda x: -len(x)):
        if keyword in text:
            return KEYWORD_MAPPING[keyword]
    return None


@app.route('/qa', methods=['GET'])
def ner_qa():
    """方案二：NER模式版本"""
    user_input = request.args.get('question', '').strip()
    cities = load_city_data()
    city_names = [city['name'] for city in cities]

    # 实体识别阶段
    city = recognize_city_entity(user_input, cities)
    keyword = recognize_keyword_entity(user_input)

    # 处理识别失败场景
    if not city:
        return jsonify({'answer': "请明确要查询的城市名称，例如：北京市、上海等"})
    if not keyword:
        return jsonify({'answer': "请指明查询维度，支持：人口、GDP、车牌号等属性查询"})

    # 构建快速查询索引
    city_index = {city['name']: city for city in cities}

    # 获取查询结果
    target_city = city_index.get(city)
    if not target_city:
        return jsonify({'answer': f"未找到{city}的相关数据"})

    result = target_city.get(keyword, "该信息暂未收录")
    return jsonify({
        'answer': f"{city}的{keyword}是：{result}" if result != "该信息暂未收录"
        else f"暂无{city}的{keyword}数据"
    })




if __name__ == '__main__':
    app.run(port=5006, host='0.0.0.0')