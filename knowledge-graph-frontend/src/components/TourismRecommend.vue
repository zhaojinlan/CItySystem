<template>
<div class="rec">
  <h2>智能推荐</h2>

  <input v-model="question" placeholder="请输入现居地,请输入你的预算，你想要几天的旅行，你所期望的出行方式，你想旅游的目的地类型（名胜古迹、自然风光、现代都市等）" />

<button @click="getAnswer" class="search-button">
          <span class="icon">🔍</span> 搜索
        </button>


  <div v-if="answer" class="answer">

      <p>{{ answer }}</p>

  </div>>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: 'TourismRecommend',
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
        const response = await axios.post('http://localhost:5007/ask', {question: this.question});
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
.rec{
  width: 80%;
  height: 100vh;
  border: 1px solid #cccccc;
}
input{
  width: 80%;
  padding: 10px;
  margin-bottom: 10px;
  margin-bottom: 10px;

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
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
}

</style>