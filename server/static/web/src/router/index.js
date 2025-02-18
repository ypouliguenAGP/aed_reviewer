import { createRouter, createWebHistory, RouterView } from 'vue-router'
import { h } from 'vue'
import ProtectionGroupView from '../views/ProtectionGroupView.vue'


const router = createRouter({
  // history: createWebHistory('/http://localhost:5000/aed_reviewer/'),
  history: createWebHistory(''),
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
      path: '/:aed_id/global_alerting',
      name: 'global alerting',
      props: true,
      component: () => import('../views/GlobalAlerting.vue'),
    },
    {
      path: '/:aed_id/ip_access',
      name: 'ip_access',
      props: true,
      component: () => import('../views/IPAccess.vue'),
    },
  ],
})

export default router
