import { createRouter, createWebHistory, RouterView } from 'vue-router'
import { h } from 'vue'
import ProtectionGroupView from '../views/ProtectionGroupView.vue'


const router = createRouter({
  history: createWebHistory('/aed_reviewer/'),
  // history: createWebHistory(''),
  routes: [
    {
      path: '/add',
      name: 'add',
      component: () => import('../views/Add.vue'),
    },
    {
      path: '/link',
      name: 'link',
      component: () => import('../views/Link.vue'),
    },
    {
    path: '/:aed_id',     
    component: { render: () => h(RouterView) },
    props: true,
    children: [
      {
        path: 'protection-groups',     
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
        path: 'statistics/interfaces',
        name: 'statistics/interfaces',
        props: true,
        component: () => import('../views/statistics/Interfaces.vue'),
      },
      {
        path: 'interfaces',
        name: 'interfaces',
        props: true,
        component: () => import('../views/InterfaceView.vue'),
      },
      {
        path: 'routes',
        name: 'routes',
        props: true,
        component: () => import('../views/Routes.vue'),
      },
      {
        path: 'crawlers',
        name: 'crawlers',
        props: true,
        component: () => import('../views/Crawlers.vue'),
      },
      {
        path: 'hardware',
        name: 'hardware',
        props: true,
        component: () => import('../views/Hardware.vue'),
      },
      {
        path: 'licenses',
        name: 'licenses',
        props: true,
        component: () => import('../views/Licenses.vue'),
      },
      {
        path: 'changes',
        name: 'changes',
        props: true,
        component: () => import('../views/Changes.vue'),
      },
      {
        path: 'global_config',
        name: 'global',
        props: true,
        component: () => import('../views/GlobalConfig.vue'),
      },
      {
        path: 'notifications',
        name: 'notifications',
        props: true,
        component: () => import('../views/Notifications.vue'),
      },
      {
        path: 'global_alerting',
        name: 'global alerting',
        props: true,
        component: () => import('../views/GlobalAlerting.vue'),
      },
      {
        path: 'ip_access',
        name: 'ip_access',
        props: true,
        component: () => import('../views/IPAccess.vue'),
      },
      {
        path: 'packet-explorer',
        name: 'packet-explorer',
        props: true,
        component: () => import('../views/PacketExplorer.vue'),
      },
    ]
    },
  ],
})
export default router