import { createRouter, createWebHistory, RouterView } from 'vue-router'
import { h } from 'vue'
import ProtectionGroupView from '../views/ProtectionGroupView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/protection-groups',     
      component: { render: () => h(RouterView) },
      children: [
        { 
          path: '',
          name: 'protection-groups',
          component: ProtectionGroupView,
        },
        { 
          path: ':pg_id',
          name: 'protection-groups-details',
          props: true,
          component: () => import('../views/ProtectionGroupDetailView.vue'),
        }
      ]
    },
    {
      path: '/interfaces',
      name: 'interfaces',
      component: () => import('../views/InterfaceView.vue'),
    },
    {
      path: '/crawlers',
      name: 'crawlers',
      component: () => import('../views/Crawlers.vue'),
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: () => import('../views/Notifications.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/test',
      name: 'test',
      component: () => import('../views/Test.vue'),
    },
  ],
})

export default router
