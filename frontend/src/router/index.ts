import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { isAuthenticated } from '../api';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
    meta: {
      title: '首页 - LiveMirror'
    }
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('../views/Upload.vue'),
    meta: {
      title: '上传 - LiveMirror',
      requiresAuth: true
    }
  },
  {
    path: '/report/:taskId?',
    name: 'report',
    component: () => import('../views/Report.vue'),
    meta: {
      title: '报告 - LiveMirror',
      requiresAuth: true
    }
  },
  {
    path: '/attribution',
    name: 'attribution',
    component: () => import('../views/AttributionAnalysis.vue'),
    meta: {
      title: '归因 - LiveMirror',
      requiresAuth: true
    }
  },
  {
    path: '/suggestions',
    name: 'suggestions',
    component: () => import('../views/SuggestionAnalysis.vue'),
    meta: {
      title: '建议 - LiveMirror',
      requiresAuth: true
    }
  },
  {
    path: '/trends',
    name: 'trends',
    component: () => import('../views/TrendsAnalysis.vue'),
    meta: {
      title: '趋势 - LiveMirror',
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '登录 - LiveMirror'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
    meta: {
      title: '注册 - LiveMirror'
    }
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../views/History.vue'),
    meta: {
      title: '历史记录 - LiveMirror',
      requiresAuth: true
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/Profile.vue'),
    meta: {
      title: '个人中心 - LiveMirror',
      requiresAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

router.beforeEach((to) => {
  document.title = (to.meta.title as string) || 'LiveMirror';

  if (to.meta.requiresAuth && !isAuthenticated()) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath
      }
    };
  }

  if ((to.name === 'login' || to.name === 'register') && isAuthenticated()) {
    return { name: 'home' };
  }

  return true;
});

export default router;
