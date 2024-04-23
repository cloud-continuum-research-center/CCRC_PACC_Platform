import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Tables from "../views/Tables.vue";
import Signup from "../views/Signup.vue";
import Signin from "../views/Signin.vue";
import store from "../store/index.js";
import Monitoring from "../views/components/Monitoring.vue";

const routes = [
  {
    path: "/",
    name: "/",
    redirect: "/signin",
  },
  {
    path: "/dashboard-default",
    name: "Dashboard",
    component: Dashboard,
    // 이 라인 추가: 대시보드 페이지는 로그인이 필요
    meta: { requiresAuth: true },
  },
  {
    path: "/tables",
    name: "Tables",
    component: Tables,
    // 이 라인 추가: 테이블 페이지는 로그인이 필요
    meta: { requiresAuth: true },
  },
  {
    path: "/signin",
    name: "Signin",
    component: Signin,
  },
  {
    path: "/signup",
    name: "Signup",
    component: Signup,
  },
  {
    path:"/monitoring",
    name:"Monitoring",
    component: Monitoring,
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  linkActiveClass: "active",
});

router.beforeEach((to, from, next) => {
  if (
    to.matched.some((record) => record.meta.requiresAuth) &&
    !store.state.authToken
  ) {
    // 이 페이지는 인증이 필요하고, 사용자가 로그인하지 않았습니다.
    console.log("Redirecting to login...");
    next("/signin");
  } else {
    // 인증이 필요 없는 페이지이거나, 이미 로그인되어 있습니다.
    console.log("Proceeding to route:", to.path);
    next();
  }
});

export default router;
