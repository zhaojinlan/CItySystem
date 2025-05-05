from flask import Flask, jsonify, render_template, request
from py2neo import Graph

graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))


def load_city_data():
    query = "MATCH (n:城市) RETURN n"
    data = graph.run(query)
    cities = []
    for record in data:
        cities.append(record['n'])
    return cities

a=load_city_data()

print(a)