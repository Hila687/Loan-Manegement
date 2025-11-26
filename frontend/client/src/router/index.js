// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import TestApiPage from "../pages/TestApiPage.vue";
import NewLoanPage from "../pages/NewLoanPage.vue";

const routes = [
  { path: "/", redirect: "/loans/new" },
  { path: "/debug/users", name: "TestApi", component: TestApiPage },
  { path: "/loans/new", name: "NewLoan", component: NewLoanPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
