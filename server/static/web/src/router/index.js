import { createRouter, createWebHistory, RouterView } from 'vue-router'
import { h } from 'vue'
import ProtectionGroupView from '../views/ProtectionGroupView.vue'


const router = createRouter({
  history: createWebHistory('/http://localhost:5000/aed_reviewer/'),
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
      path: '/global_alerting',
      name: 'global alerting',
      component: () => import('../views/GlobalAlerting.vue'),
    },
    {
      path: '/ip_access',
      name: 'ip_access',
      component: () => import('../views/IPAccess.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
