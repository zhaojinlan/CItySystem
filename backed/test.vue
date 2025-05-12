<template>
  <div class="container">
    <h1 class="title">城市信息知识图谱</h1>
    <div class="search-container">
      <div class="search-bar">
        <input 
          v-model="searchQuery" 
          placeholder="输入城市或相关信息..."
          class="search-input"
          @keyup.enter="searchGraph"
        />
        <button @click="searchGraph" class="search-button">
          <span class="icon">🔍</span> 搜索
        </button>
      </div>
    </div>
    
    <div class="info-box" v-if="info">
      <div class="info-content">
        <pre>{{ info }}</pre>
      </div>
    </div>

    <div id="graph-container">
      <div id="graph">
        <h2 class="graph-title">知识图谱可视化展示</h2>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import { query } from '../neo4j';
import axios from "axios";

export default {
 name: 'KnowledgeGraph',
  data() {
    return {
      info:'',
      searchQuery: '', // 用户输入的搜索内容
      nodes: [], // 节点数据
      links: [] // 关系数据
    };
  },
  methods: {
    async searchGraph() {
      if (!this.searchQuery) {
        alert('请输入搜索内容');
        return;
      }

      try {
        const response = await axios.post('http://localhost:5007/show', { question: this.searchQuery });
        this.info = response.data.info;
      } catch (error) {
        console.error('Error fetching answer:', error);
        this.info = '未找到相关答案';
      }

      const cypher = `
        MATCH (n)-[r]->(m)
        WHERE n.name CONTAINS $searchQuery OR m.name CONTAINS $searchQuery
        RETURN n, r, m
      `;

      const records = await query(cypher, { searchQuery: this.searchQuery });

      // 提取节点和关系数据
      const nodesMap = new Map();
      const links = [];

      records.forEach(record => {
        const source = record.get('n');
        const target = record.get('m');
        const relationship = record.get('r');

        if (!nodesMap.has(source.identity.toString())) {
          nodesMap.set(source.identity.toString(), { id: source.identity.toString(), name: source.properties.name });
        }
        if (!nodesMap.has(target.identity.toString())) {
          nodesMap.set(target.identity.toString(), { id: target.identity.toString(), name: target.properties.name });
        }

        links.push({
          source: source.identity.toString(),
          target: target.identity.toString(),
          type: relationship.type
        });
      });

      this.nodes = Array.from(nodesMap.values());
      this.links = links;

      this.renderGraph();
    },
    renderGraph() {
      const container = document.getElementById('graph-container');
      const width = container.clientWidth;
      const height = Math.min(window.innerHeight * 0.6, 600);

      // 创建带箭头标记的SVG定义
      const svg = d3.select("#graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .call(d3.zoom().on("zoom", (event) => {
          svg.attr("transform", event.transform);
        }))
        .append("g");

      // 添加箭头标记
      svg.append("defs").selectAll("marker")
        .data(["arrow"])
        .enter().append("marker")
        .attr("id", d => d)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 25")
        .attr("refY", 0")
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#999");

      // 力导向图配置
      const simulation = d3.forceSimulation(this.nodes)
        .force("link", d3.forceLink(this.links)
          .id(d => d.id)
          .distance(100)
        )
        .force("charge", d3.forceManyBody().strength(-120))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide(30));

      // 绘制边
      const link = svg.append("g")
        .selectAll("line")
        .data(this.links)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke", "#999")
        .attr("stroke-width", 1.5)
        .attr("marker-end", "url(#arrow)");

      // 绘制节点
      const node = svg.append("g")
        .selectAll("circle")
        .data(this.nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", 12)
        .attr("fill", d => this.colorScale(d.group))
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .call(this.drag(simulation));

      // 节点文字标签
      const text = svg.append("g")
        .selectAll("text")
        .data(this.nodes)
        .enter().append("text")
        .attr("class", "node-text")
        .text(d => d.name)
        .attr("dx", 15)
        .attr("dy", ".35em");

      // 边文字标签
      link.append("text")
        .text(d => d.type)
        .attr("class", "link-text")
        .attr("dy", -5);

      // 更新函数
      simulation.on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);

        text
          .attr("x", d => d.x)
          .attr("y", d => d.y);
      });

      // 添加交互效果
      node.on("mouseover", function(event, d) {
          d3.select(this)
            .transition()
            .duration(100)
            .attr("r", 16);
          
          link.transition()
            .duration(100)
            .style("opacity", o => (o.source === d || o.target === d) ? 1 : 0.2);
        })
        .on("mouseout", function() {
          d3.select(this)
            .transition()
            .duration(100)
            .attr("r", 12);
          
          link.transition()
            .duration(100)
            .style("opacity", 1);
        });
    },

    drag(simulation) {
       function dragstarted(event, d) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        }
        function dragged(event, d) {
          d.fx = event.x;
          d.fy = event.y;
        }

        function dragended(event, d) {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }
         return d3.drag()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended);

    }
  },
  mounted() {
    this.colorScale = d3.scaleOrdinal(d3.schemeCategory10);
  }
};
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2.5em;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.search-container {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
}

.search-bar {
  display: flex;
  gap: 10px;
  width: 60%;
  max-width: 600px;
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #3498db;
  border-radius: 25px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #2980b9;
  box-shadow: 0 0 10px rgba(52,152,219,0.3);
}

.search-button {
  padding: 12px 25px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  border: none;
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52,152,219,0.3);
}

.icon {
  margin-right: 8px;
}

.info-box {
  margin: 20px auto;
  width: 80%;
  background: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.info-content {
  padding: 20px;
  max-height: 200px;
  overflow-y: auto;
}

.info-content pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  color: #34495e;
  line-height: 1.6;
}

#graph-container {
  margin-top: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow: hidden;
}

.graph-title {
  text-align: center;
  padding: 15px;
  color: #2c3e50;
  margin: 0;
}

.node:hover {
  cursor: pointer;
}

.node-text {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 12px;
  fill: #34495e;
  font-weight: 500;
  pointer-events: none;
  text-shadow: 1px 1px 2px white;
}

.link-text {
  font-size: 10px;
  fill: #7f8c8d;
  pointer-events: none;
}
</style>