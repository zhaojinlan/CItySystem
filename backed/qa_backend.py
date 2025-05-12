from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入 CORS
from py2neo import Graph, NodeMatcher
import openai
import time
import logging

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 连接 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))


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
    sorted_cities = sorted(cities, key=lambda x: len(x['name']))
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


@app.route('/show', methods=['POST'])
def show():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    # 将问题转换为小写，以便进行不区分大小写的匹配
    lower_question = question.lower()

    # 遍历数据集，查找匹配的答案
    matcher = NodeMatcher(graph)
    cities = matcher.match('城市')

    for city in cities:
        if city['name'].lower() in lower_question or city['anothername'].lower() in lower_question:
            answer = (
                f"城市名: {city['name']}\n"
                f"英文名: {city['englishname']}\n"
                f"别名: {city['anothername']}\n"
                f"人口: {city['population']}\n"
                f"地区生产总值: {city['rgdp']}\n"
                f"车牌号: {city['car']}\n"
            )
            return jsonify({'info': answer})
    return jsonify({'answer': '未找到相关信息'})


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    # 将问题转换为小写，以便进行不区分大小写的匹配
    lower_question = question.lower()

    # 遍历数据集，查找匹配的答案
    matcher = NodeMatcher(graph)
    cities = matcher.match('城市')
    keyword = recognize_keyword_entity(question)


    for city in cities:
        if city['name'].lower() in lower_question or city['anothername'].lower() in lower_question:
            answer = {
                '城市名': city['name'],
                '英文名': city['englishname'],
                '别名': city['anothername'],
                '人口数量': city['population'],
                '地区生产总值': city['rgdp'],
                '车牌号': city['car'],
                '行政级别': city['level'],
                '省份': city['province']
            }
            result = city.get(keyword, "该信息暂未收录")
            return jsonify({
                'answer': f"{city['name']}的{keyword}是：{result}" if result != "该信息暂未收录"
                else f"暂无{city}的{keyword}数据"
            })

    return jsonify({'answer': '未找到相关答案'})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    lower_question = question.lower()

    openai.api_key = 'sk-H1KHwcp5ayd8LLkPuzPjgF6yd9xAr8z6Et7WLSsp0Af6VhRl'

    openai.api_base = "https://xiaoai.plus/v1"

    def get_completion_with_role(role, instruction, content):
        max_retries = 5
        for i in range(max_retries):
            try:
                messages = [
                    {"role": "system", "content": f"你是一个 {role}."},
                    {"role": "user", "content": f"{instruction}\n{content}"}
                ]
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0
                )
                print(role, response.choices[0].message["content"])
                return response.choices[0].message["content"]
            except (openai.error.RateLimitError,
                    openai.error.ServiceUnavailableError,
                    openai.error.APIError,
                    openai.error.Timeout,
                    openai.error.APIConnectionError,
                    openai.error.InvalidRequestError,
                    openai.error.AuthenticationError):

                if i < max_retries - 1:
                    time.sleep(2)
                else:
                    logging.error('Max retries reached for prompt: ')
                    return "Error"

    role = '旅行规划师'
    instruction = '根据给出的信息来推荐在中国旅游的方案，希望考虑与预算强相关，'
    return jsonify({'answer': get_completion_with_role(role, instruction, lower_question)})

if __name__ == '__main__':
    app.run(port=5007, host='0.0.0.0')