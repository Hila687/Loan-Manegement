// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import Home from "../pages/HomePage.vue";
import LoanList from "../pages/LoanListPage.vue";
import TestApiPage from "../pages/TestApiPage.vue";
import NewLoanPage from "../pages/NewLoanPage.vue";

const routes = [
  { path: "/", name: "Home", component: Home },
  { path: "/loans", name: "LoanList", component: LoanList },
  { path: "/loans/new", name: "NewLoan", component: NewLoanPage },
  { path: "/debug/users", name: "TestApi", component: TestApiPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
