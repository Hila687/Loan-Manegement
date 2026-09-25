import {
  createRouter,
  createWebHistory,
} from "vue-router";

import HomePage
  from "../pages/HomePage.vue";

import LoginPage
  from "../pages/LoginPage.vue";

import ChangePasswordPage
  from "../pages/ChangePasswordPage.vue";

import DashboardPage
  from "../pages/DashboardPage.vue";

import LoanListPage
  from "../pages/LoanListPage.vue";

import LoanDetailsPage
  from "../pages/LoanDetailsPage.vue";

import NewLoanPage
  from "../pages/NewLoanPage.vue";

import EditLoanPage
  from "../pages/EditLoanPage.vue";

import ReportsPage
  from "../pages/ReportsPage.vue";

import RemindersPage
  from "../pages/RemindersPage.vue";

import ManagementPage
  from "../pages/ManagementPage.vue";

import {
  useAuth,
} from "../composables/useAuth";

const routes = [
  {
    path:
      "/login",

    name:
      "Login",

    component:
      LoginPage,

    meta: {
      publicOnly:
        true,
    },
  },

  {
    path:
      "/change-password",

    name:
      "ChangePassword",

    component:
      ChangePasswordPage,

    meta: {
      requiresAuth:
        true,
    },
  },

  {
    path:
      "/",

    name:
      "Home",

    component:
      HomePage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "trustee",
        "borrower",
        "donor",
      ],
    },
  },

  {
    path:
      "/dashboard",

    name:
      "Dashboard",

    component:
      DashboardPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "trustee",
        "borrower",
        "donor",
      ],
    },
  },

  {
    path:
      "/loans/new",

    name:
      "NewLoan",

    component:
      NewLoanPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
      ],
    },
  },

  {
    path:
      "/archive/:id",

    name:
      "LoanArchiveWithDetails",

    component:
      LoanListPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
      ],
    },
  },

  {
    path:
      "/archive",

    name:
      "LoanArchive",

    component:
      LoanListPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
      ],
    },
  },

  {
    path:
      "/loans/:id/edit",

    name:
      "EditLoan",

    component:
      EditLoanPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
      ],
    },
  },

  {
    path:
      "/loans/:id/details",

    name:
      "LoanDetails",

    component:
      LoanDetailsPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "trustee",
        "borrower",
      ],
    },
  },

  {
    path:
      "/loans/:id",

    name:
      "LoanListWithDetails",

    component:
      LoanListPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "trustee",
        "borrower",
      ],
    },
  },

  {
    path:
      "/loans",

    name:
      "LoanList",

    component:
      LoanListPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "trustee",
        "borrower",
      ],
    },
  },

  {
    path:
      "/reports",

    name:
      "Reports",

    component:
      ReportsPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
      ],
    },
  },

  {
    path:
      "/reminders",

    name:
      "Reminders",

    component:
      RemindersPage,

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
      ],
    },
  },

  {
    path:
      "/borrowers",

    name:
      "Borrowers",

    component:
      ManagementPage,

    props: {
      section:
        "borrowers",
    },

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "trustee",
        "borrower",
      ],
    },
  },

  {
    path:
      "/trustees",

    name:
      "Trustees",

    component:
      ManagementPage,

    props: {
      section:
        "trustees",
    },

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "trustee",
        "borrower",
      ],
    },
  },

  {
    path:
      "/donors",

    name:
      "Donors",

    component:
      ManagementPage,

    props: {
      section:
        "donors",
    },

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "donor",
      ],
    },
  },

  {
    path:
      "/donations",

    name:
      "Donations",

    component:
      ManagementPage,

    props: {
      section:
        "donations",
    },

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
        "donor",
      ],
    },
  },

  {
    path:
      "/admins",

    name:
      "Admins",

    component:
      ManagementPage,

    props: {
      section:
        "admins",
    },

    meta: {
      requiresAuth:
        true,

      roles: [
        "admin",
      ],
    },
  },

  {
    path:
      "/:pathMatch(.*)*",

    redirect:
      "/",
  },
];

const router =
  createRouter({
    history:
      createWebHistory(),

    routes,
  });

router.beforeEach(
  async (
    to
  ) => {
    const auth =
      useAuth();

    if (
      !auth
        .initialized
        .value
    ) {
      await auth
        .initialize();
    }

    if (
      to.meta
        .publicOnly &&
      auth
        .isAuthenticated
        .value
    ) {
      return auth
        .mustChangePassword
        .value
        ? "/change-password"
        : "/";
    }

    if (
      to.meta
        .requiresAuth &&
      !auth
        .isAuthenticated
        .value
    ) {
      return {
        path:
          "/login",

        query: {
          redirect:
            to.fullPath,
        },
      };
    }

    if (
      auth
        .isAuthenticated
        .value &&
      auth
        .mustChangePassword
        .value &&
      to.name !==
        "ChangePassword"
    ) {
      return (
        "/change-password"
      );
    }

    if (
      auth
        .isAuthenticated
        .value &&
      !auth
        .mustChangePassword
        .value &&
      to.name ===
        "ChangePassword"
    ) {
      return "/";
    }

    const allowedRoles =
      Array.isArray(
        to.meta.roles
      )
        ? to.meta.roles
        : [];

    if (
      allowedRoles.length >
        0 &&
      auth.role.value &&
      !allowedRoles.includes(
        auth.role.value
      )
    ) {
      return "/";
    }

    return true;
  }
);

export default router;