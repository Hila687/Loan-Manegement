// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";

import Home from "../pages/HomePage.vue";
import LoanList from "../pages/LoanListPage.vue";
import LoanDetails from "../pages/LoanDetailsPage.vue";
import TestApiPage from "../pages/TestApiPage.vue";
import NewLoanPage from "../pages/NewLoanPage.vue";
import EditLoanPage from "../pages/EditLoanPage.vue";


const routes = [
  { path: "/", name: "Home", component: Home },

  { path: "/loans/:id/edit", name: "EditLoan", component: EditLoanPage },

  // ✅ אותו מסך גם ל-/loans וגם ל-/loans/:id
  { path: "/loans/:id?", name: "LoanList", component: LoanList },

  { path: "/loans/new", name: "NewLoan", component: NewLoanPage },

  // ✅ לשמור את דף הפרטים הישן בנתיב נפרד (לא חובה להשתמש בו)
  { path: "/loans/:id/details", name: "LoanDetails", component: LoanDetails },

  { path: "/debug/users", name: "TestApi", component: TestApiPage },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});