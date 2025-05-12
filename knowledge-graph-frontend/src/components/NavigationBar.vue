<template>
  <nav class="navbar">
    <ul class="nav-list">
      <li v-for="route in routes" :key="route.path">
        <router-link :to="route.path">{{ route.name }}</router-link>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: 'NavigationBar',
  data() {
    return {
      routes: [
        { path: '/', name: '知识图谱' },
        { path: '/about', name: '问答系统' },
        {path:'/agent',name:'旅行推荐'}
        // 可以根据需要添加更多导航项
      ]
    };
  }
};
</script>

<style scoped>
.navbar {
  background-color: #333;
  padding: 10px;
  width: 200px; /* 设置导航栏宽度 */
  position: fixed; /* 固定定位 */
  top: 0;
  left: 0;
  height: 100vh; /* 高度100%视窗高度 */
  display: flex;
  flex-direction: column; /* 垂直排列列表项 */
  align-items: center; /* 垂直居中对齐列表项 */
}

.nav-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.nav-list li a {
  color: white;
  text-decoration: none;
  padding: 10px;
  display: block; /* 使链接占满整个li */
}

.nav-list li a:hover {
  background-color: #555;
}
</style>