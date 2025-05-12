<template>
  <div class="qa-container">
    <h2>问答系统</h2>
    <input v-model="question" placeholder="请输入问题" />
    <button @click="getAnswer">查询</button>
    <div v-if="answer" class="answer">
      <h3>答案：</h3>
      <p>{{ answer }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'QuestionAnswering',
  data() {
    return {
      question: '', // 用户输入的问题
      answer: '' // 答案
    };
  },
  methods: {
    async getAnswer() {
      if (!this.question) {
        alert('请输入问题');
        return;
      }

      try {
        const response = await axios.post('http://localhost:5007/query', { question: this.question });
        this.answer = response.data.answer;
      } catch (error) {
        console.error('Error fetching answer:', error);
        this.answer = '未找到相关答案';
      }


    }
  }
};
</script>

<style scoped>


.qa-container {

  border: 1px solid #ccc;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;

}

input {
  width: 80%;
  padding: 10px;
  margin-bottom: 10px;
}

button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.answer {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
}
</style>