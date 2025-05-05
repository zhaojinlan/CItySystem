import re
from py2neo import Graph
question_patterns = [
    {
        "intent": "query_adjacent",
        "patterns": ["(.*?)接壤哪些城市", "(.*?)的相邻城市","哪些城市与(.*?)接壤"],
        "cypher": "MATCH (c:`城市`)-[:接壤]-(n) WHERE c.name = $city RETURN n.name"
    },
    {
        "intent": "check_adjacent",
        "patterns": ["(.*?)和(.*?)是否接壤"],
        "cypher": "MATCH (c1:`城市`)-[:接壤]-(c2:`城市`) WHERE c1.name = $city1 AND c2.name = $city2 RETURN count(*)  "
    },
    {
        "intent": "informantion_adjacent",
        "patterns": ["展示(.*?)的所有信息"],
        "cypher": "MATCH (c:  `城市` {name: $city}) RETURN c.name, c.population,c.rgdp,c.anothername "
    }
]


class QASystem:
    def __init__(self):
        self.graph = Graph("neo4j://localhost:7687", auth=("neo4j", "12345678"))

    def parse_question(self, question):
        for pattern in question_patterns:
            for regex in pattern["patterns"]:
                match = re.match(regex, question)
                if match:
                    # print(f"匹配意图: {pattern['intent']}, 参数: {match.groups()}")
                    return {
                        "intent": pattern["intent"],
                        "params": match.groups(),
                        "template": pattern["cypher"]
                    }
        print("未匹配任何意图")
        return None

    def generate_cypher(self, parsed_data):
        # print(f"生成 Cypher: {parsed_data['template']}, 参数: {parsed_data['params']}")
        if parsed_data["intent"] == "query_adjacent":
            return parsed_data["template"], {"city": parsed_data["params"][0]}
        elif parsed_data["intent"] == "check_adjacent":
            return parsed_data["template"], {
                "city1": parsed_data["params"][0],
                "city2": parsed_data["params"][1]
            }
        elif parsed_data["intent"] == "informantion_adjacent":
            return parsed_data["template"], {"city": parsed_data["params"][0]}

    def execute_query(self, cypher, params):
        # print(f"执行 Cypher: {cypher}, 参数: {params}")
        result = self.graph.run(cypher, params).data()
        # print(f"原始结果: {result}")

        if not result:
            return "未找到相关数据"

        if "WHERE c.name = $city" in cypher:
            exists_query = "MATCH (c:城市) WHERE c.name = $city RETURN count(c) > 0 as exists"
            if not self.graph.run(exists_query, params).data()[0]["exists"]:
                return "该城市不存在于数据库中"

        if "RETURN n.name" in cypher:
            return [item["n.name"] for item in result]
        elif "RETURN count" in cypher:
            return "是" if result[0]["> 0"] else "否"

        if "RETURN c.name, c.population,c.rgdp,c.anothername" in cypher:
            city_info = {}
            for key, value in result[0].items():
                clean_key = key.split(".")[1] if "." in key else key
                city_info[clean_key] = value
            return city_info
        else:
            return "未知查询类型"

    def ask(self, question):
        parsed = self.parse_question(question)
        if not parsed:
            return "暂不支持该类型问题"
        cypher, params = self.generate_cypher(parsed)
        result = self.execute_query(cypher, params)
        return result


# 测试
qa = QASystem()
print(qa.ask("展示北京的所有信息"))
print(qa.ask("安庆市接壤哪些城市？"))