// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";

import Home from "../pages/HomePage.vue";
import LoanList from "../pages/LoanListPage.vue";
import TestApiPage from "../pages/TestApiPage.vue";
import NewLoanPage from "../pages/NewLoanPage.vue";

const routes = [
  { path: "/", name: "Home", component: Home },

  // 📌 דף כל ההלוואות
  { path: "/loans", name: "LoanList", component: LoanList },

  // 📌 אותו הדף — אבל עם הלוואה פתוחה
  // חשוב! לא מוחקים את הישן, רק מוסיפים את זה
  { path: "/loans/:id", name: "LoanListOpen", component: LoanList },

  // יצירת הלוואה חדשה
  { path: "/loans/new", name: "NewLoan", component: NewLoanPage },

  // ראוט לדיבאג
  { path: "/debug/users", name: "TestApi", component: TestApiPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
