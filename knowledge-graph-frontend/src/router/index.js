import { createRouter, createWebHistory } from 'vue-router';
import KnowledgeGraph from '../components/KnowledgeGraph.vue';
import QAsystem from '../components/QAsystem.vue';
import TourismRecommend from '../components/TourismRecommend.vue'

const routes = [
  {
    path: '/',
    name: 'KnowledgeGraph',
    component: KnowledgeGraph
  },
  {
    path: '/about',
    name: 'QAsystem',
    component: QAsystem
  },
    {
    path: '/agent',
    name: 'TourismRecommend',
    component: TourismRecommend
  }
  // 可以根据需要添加更多路由
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;