# import csv
#
# # 加载城市数据
# def load_city_data(file_path):
#     cities = []
#     with open(file_path, 'r', encoding='utf-8') as file:
#         csv_reader = csv.DictReader(file)
#         for row in csv_reader:
#             cities.append(row)
#     return cities
#
# # 简单问答系统
# def simple_qa_system(cities):
#     print("欢迎使用城市信息问答系统！")
#     print("你可以问我关于城市的信息，例如：人口数量、地区生产总值、车牌号等。")
#     print("输入 '退出' 退出程序。")
#
#     while True:
#         user_input = input("\n请输入你的问题：")
#
#         if user_input == "退出":
#             print("感谢使用城市信息问答系统！再见！")
#             break
#
#         # 简单的自然语言处理逻辑
#         if "人口数量" in user_input or "人口" in user_input:
#             keyword = "人口数量"
#         elif "地区生产总值" in user_input or "GDP" in user_input:
#             keyword = "地区生产总值"
#         elif "车牌号" in user_input:
#             keyword = "车牌号"
#         elif "行政级别" in user_input:
#             keyword = "行政级别"
#         elif "省份" in user_input:
#             keyword = "省份"
#         elif "英文名" in user_input:
#             keyword = "英文名"
#         elif "别名" in user_input:
#             keyword = "别名"
#         else:
#             print("抱歉，我不太明白你的问题。请尝试以下问题：")
#             print("- 某个城市的人口数量是多少？")
#             print("- 某个城市的地区生产总值是多少？")
#             print("- 某个城市的车牌号是什么？")
#             print("- 某个城市的行政级别是什么？")
#             print("- 某个城市属于哪个省份？")
#             continue
#
#         # 提取城市名称
#         city_name = None
#         for city in cities:
#             if city["城市名"] in user_input:
#                 city_name = city["城市名"]
#                 break
#
#         if not city_name:
#             print("抱歉，我没有找到你提到的城市。请尝试其他城市。")
#             continue
#
#         # 查找并返回答案
#         for city in cities:
#             if city["城市名"] == city_name:
#                 answer = city.get(keyword, "信息未提供")
#                 print(f"{city_name}的{keyword}是：{answer}")
#                 break
#
# # 主函数
# if __name__ == "__main__":
#     # 假设CSV文件路径为 '城市信息.csv'
#     file_path = '城市信息.csv'
#     cities = load_city_data(file_path)
#     simple_qa_system(cities)
