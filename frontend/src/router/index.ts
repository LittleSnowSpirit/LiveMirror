import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/Login.vue';
import RegisterView from '../views/Register.vue';
import UploadView from '../views/Upload.vue';
import ReportView from '../views/Report.vue';
import AttributionAnalysisView from '../views/AttributionAnalysis.vue';
import SuggestionAnalysisView from '../views/SuggestionAnalysis.vue';
import TrendsAnalysisView from '../views/TrendsAnalysis.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: '首页 - LiveMirror'
    }
  },
  {
    path: '/upload',
    name: 'upload',
    component: UploadView,
    meta: {
      title: '上传 - LiveMirror'
    }
  },
  {
    path: '/report/:taskId?',
    name: 'report',
    component: ReportView,
    meta: {
      title: '报告 - LiveMirror'
    }
  },
  {
    path: '/attribution',
    name: 'attribution',
    component: AttributionAnalysisView,
    meta: {
      title: '归因 - LiveMirror'
    }
  },
  {
    path: '/suggestions',
    name: 'suggestions',
    component: SuggestionAnalysisView,
    meta: {
      title: '建议 - LiveMirror'
    }
  },
  {
    path: '/trends',
    name: 'trends',
    component: TrendsAnalysisView,
    meta: {
      title: '趋势 - LiveMirror'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      title: '登录 - LiveMirror'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: {
      title: '注册 - LiveMirror'
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

router.beforeEach((to, _from, next) => {
  document.title = (to.meta.title as string) || 'LiveMirror';
  next();
});

export default router;
