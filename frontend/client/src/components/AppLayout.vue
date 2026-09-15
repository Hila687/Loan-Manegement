<template>
  <div
    :dir="dir"
    class="flex h-screen overflow-hidden bg-gradient-to-br from-canvas to-canvas-deep"
  >
    <!-- Desktop sidebar -->
    <aside
      class="hidden lg:flex lg:w-64 xl:w-72 lg:flex-shrink-0 lg:flex-col bg-white/85 backdrop-blur-xl border-e border-line/70 shadow-sm"
    >
      <!-- Brand -->
      <div class="p-6 xl:p-8 border-b border-line/70">
        <router-link
          to="/"
          class="flex items-center gap-3"
        >
          <div
            class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand to-brand-deep flex items-center justify-center shadow-lg shadow-brand/20 flex-shrink-0"
          >
            <svg
              class="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"
              />
            </svg>
          </div>

          <div class="min-w-0">
            <h1
              class="text-xl xl:text-2xl font-bold bg-gradient-to-r from-brand to-brand-deep bg-clip-text text-transparent truncate"
            >
              {{ t("app.title") }}
            </h1>

            <p
              v-if="auth.user.value"
              class="text-xs text-muted mt-0.5 truncate"
            >
              {{ roleLabel }}
            </p>
          </div>
        </router-link>
      </div>

      <!-- Navigation -->
      <nav
        class="flex-1 min-h-0 overflow-y-auto p-4 xl:p-6 space-y-1.5"
        aria-label="Main navigation"
      >
        <router-link
          v-for="item in visibleNavigation"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-4 py-3 xl:py-3.5 rounded-xl transition-all duration-200 group"
          :class="
            isRouteActive(item)
              ? 'bg-gradient-to-r from-brand to-brand-deep text-white shadow-lg shadow-brand/25'
              : 'text-ink-soft hover:bg-surface-muted hover:text-brand'
          "
        >
          <svg
            v-if="item.icon === 'home'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'plus'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'loans'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'dashboard'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 19V9m5 10V5m5 14v-7m5 7V3"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'people'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2m7-10a4 4 0 100-8 4 4 0 000 8zm13 10v-2a4 4 0 00-3-3.87m-2-11.26a4 4 0 010 7.75"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'trustee'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 11c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm7 10v-2a7 7 0 00-14 0v2"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'heart'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 000-7.78z"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'donation'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M5 5h14v14H5z"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'report'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2z"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'bell'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M18 8a6 6 0 00-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9m-8 13h4"
            />
          </svg>

          <svg
            v-else-if="item.icon === 'admin'"
            class="w-5 h-5 xl:w-6 xl:h-6 flex-shrink-0 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 3l7 4v5c0 4.5-2.9 7.9-7 9-4.1-1.1-7-4.5-7-9V7l7-4zm0 6v3m0 4h.01"
            />
          </svg>

          <span class="font-medium text-sm xl:text-base truncate">
            {{ t(item.label) }}
          </span>
        </router-link>
      </nav>

      <!-- Desktop account section -->
      <div class="flex-shrink-0 p-4 xl:p-6 border-t border-line/70">
        <div
          v-if="auth.user.value"
          class="mb-3 px-3 py-2"
        >
          <p class="text-sm font-semibold text-ink truncate">
            {{ auth.displayName.value }}
          </p>

          <p class="text-xs text-muted truncate">
            {{ auth.user.value.username }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <button
            v-if="showLanguageToggle"
            type="button"
            class="h-10 rounded-xl border border-line bg-white text-sm font-medium text-ink-soft hover:border-brand hover:text-brand transition-all active:scale-95"
            @click="toggleLanguage"
          >
            {{ locale === "he" ? "EN" : "HE" }}
          </button>

          <button
            type="button"
            class="h-10 rounded-xl border border-red-100 bg-red-50 text-sm font-medium text-red-600 hover:bg-red-100 transition-all active:scale-95"
            @click="performLogout"
          >
            {{ t("nav.logout") }}
          </button>
        </div>
      </div>
    </aside>

    <!-- Main application area -->
    <div class="flex-1 min-w-0 flex flex-col h-screen overflow-hidden">
      <!-- Desktop header -->
      <header
        class="hidden lg:flex flex-shrink-0 items-center justify-between bg-white/70 backdrop-blur-xl px-6 xl:px-8 py-4 xl:py-5 border-b border-line/70 shadow-sm z-30"
      >
        <div class="flex items-center gap-4 min-w-0">
          <button
            v-if="showBackButton"
            type="button"
            class="w-10 h-10 xl:w-11 xl:h-11 flex-shrink-0 flex items-center justify-center rounded-xl hover:bg-canvas-deep transition-all active:scale-95"
            :aria-label="t('common.back')"
            @click="goBack"
          >
            <svg
              class="h-5 w-5 xl:h-6 xl:w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              :class="isRTL ? 'rotate-180' : ''"
            >
              <path
                d="M15 19l-7-7 7-7"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>

          <div
            class="min-w-0"
            :class="isRTL ? 'text-right' : 'text-left'"
          >
            <h1
              v-if="title"
              class="text-xl xl:text-2xl font-bold text-ink truncate"
            >
              {{ title }}
            </h1>

            <p
              v-if="subtitle"
              class="text-sm xl:text-base text-muted mt-0.5 line-clamp-1"
            >
              {{ subtitle }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3 flex-shrink-0">
          <div
            v-if="auth.user.value"
            class="hidden xl:block text-end"
          >
            <p class="text-sm font-semibold text-ink">
              {{ auth.displayName.value }}
            </p>

            <p class="text-xs text-muted">
              {{ roleLabel }}
            </p>
          </div>

          <button
            v-if="showLanguageToggle"
            type="button"
            class="flex items-center gap-2 px-4 py-2 xl:px-5 xl:py-2.5 rounded-xl border-2 border-line bg-white text-sm xl:text-base font-medium transition-all hover:bg-surface-muted hover:border-brand hover:text-brand active:scale-95"
            @click="toggleLanguage"
          >
            <svg
              class="w-4 h-4 xl:w-5 xl:h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10"
              />
            </svg>

            <span>
              {{ locale === "he" ? "EN" : "HE" }}
            </span>
          </button>
        </div>
      </header>

      <!-- Mobile header -->
      <header
        class="lg:hidden flex-shrink-0 flex items-center justify-between bg-white/95 backdrop-blur-xl border-b border-line/70 px-4 py-3 shadow-sm z-30"
      >
        <div class="flex items-center gap-2 min-w-0">
          <button
            v-if="showBackButton"
            type="button"
            class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-lg hover:bg-canvas-deep transition-all active:scale-95"
            :aria-label="t('common.back')"
            @click="goBack"
          >
            <svg
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              :class="isRTL ? 'rotate-180' : ''"
            >
              <path
                d="M15 19l-7-7 7-7"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>

          <div class="min-w-0">
            <h2
              v-if="title"
              class="text-base font-bold text-ink truncate"
            >
              {{ title }}
            </h2>

            <p
              v-if="auth.user.value"
              class="text-[11px] text-muted truncate"
            >
              {{ auth.displayName.value }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 flex-shrink-0">
          <button
            v-if="showLanguageToggle"
            type="button"
            class="px-3 py-1.5 rounded-lg border border-line bg-white text-xs font-medium text-ink-soft hover:border-brand hover:text-brand transition-all active:scale-95"
            @click="toggleLanguage"
          >
            {{ locale === "he" ? "EN" : "HE" }}
          </button>

          <button
            type="button"
            class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-canvas-deep transition-all active:scale-95"
            :aria-label="t('nav.menu')"
            @click="mobileMenuOpen = true"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </header>

      <!-- Scrollable page content -->
      <main
        class="flex-1 min-h-0 overflow-y-auto overscroll-contain px-4 py-4 sm:px-6 sm:py-6 lg:px-8 lg:py-8 xl:px-10 xl:py-10"
      >
        <div
          class="w-full mx-auto"
          :class="maxWidthClass"
        >
          <slot />
        </div>
      </main>

      <!-- Optional footer -->
      <footer
        v-if="$slots.footer || footerText"
        class="flex-shrink-0 px-4 sm:px-6 lg:px-8 py-3 lg:py-4 bg-white/80 backdrop-blur-xl border-t border-line/70"
      >
        <div
          class="w-full mx-auto"
          :class="maxWidthClass"
        >
          <slot name="footer">
            <p
              v-if="footerText"
              class="text-xs lg:text-sm text-center text-muted"
            >
              {{ footerText }}
            </p>
          </slot>
        </div>
      </footer>
    </div>

    <!-- Mobile backdrop -->
    <transition name="fade">
      <button
        v-if="mobileMenuOpen"
        type="button"
        class="lg:hidden fixed inset-0 bg-black/45 backdrop-blur-sm z-40 cursor-default"
        aria-label="Close menu"
        @click="mobileMenuOpen = false"
      />
    </transition>

    <!-- Mobile drawer -->
    <transition :name="drawerTransitionName">
      <aside
        v-if="mobileMenuOpen"
        class="lg:hidden fixed top-0 bottom-0 w-[85vw] max-w-80 bg-white shadow-2xl z-50 flex flex-col"
        :class="isRTL ? 'right-0' : 'left-0'"
      >
        <div
          class="p-5 border-b border-line/70 flex items-center justify-between gap-3"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div
              class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand to-brand-deep flex items-center justify-center shadow-lg shadow-brand/20 flex-shrink-0"
            >
              <svg
                class="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"
                />
              </svg>
            </div>

            <div class="min-w-0">
              <h2
                class="text-lg font-bold bg-gradient-to-r from-brand to-brand-deep bg-clip-text text-transparent truncate"
              >
                {{ t("app.title") }}
              </h2>

              <p
                v-if="auth.user.value"
                class="text-xs text-muted truncate"
              >
                {{ auth.displayName.value }}
              </p>
            </div>
          </div>

          <button
            type="button"
            class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-lg hover:bg-canvas-deep transition-all active:scale-95"
            :aria-label="t('nav.closeMenu')"
            @click="mobileMenuOpen = false"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <nav
          class="flex-1 min-h-0 overflow-y-auto p-4 space-y-1.5"
          aria-label="Mobile navigation"
        >
          <router-link
            v-for="item in visibleNavigation"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200"
            :class="
              isRouteActive(item)
                ? 'bg-gradient-to-r from-brand to-brand-deep text-white shadow-lg shadow-brand/25'
                : 'text-ink-soft hover:bg-surface-muted hover:text-brand'
            "
            @click="mobileMenuOpen = false"
          >
            <span class="w-2 h-2 rounded-full bg-current opacity-70" />

            <span class="font-medium">
              {{ t(item.label) }}
            </span>
          </router-link>
        </nav>

        <div
          class="p-4 border-t border-line/70 space-y-3 bg-surface-muted"
        >
          <div
            v-if="auth.user.value"
            class="px-3"
          >
            <p class="text-sm font-semibold text-ink truncate">
              {{ auth.displayName.value }}
            </p>

            <p class="text-xs text-muted mt-0.5">
              {{ roleLabel }}
            </p>
          </div>

          <button
            type="button"
            class="w-full h-11 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm font-semibold hover:bg-red-100 transition-all active:scale-[0.99]"
            @click="performLogout"
          >
            {{ t("nav.logout") }}
          </button>
        </div>
      </aside>
    </transition>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  ref,
  watch,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import {
  useLocale,
} from "../composables/useLocale";

import {
  type UserRole,
  useAuth,
} from "../composables/useAuth";


type NavigationItem = {
  to: string;
  label: string;
  icon:
    | "home"
    | "plus"
    | "loans"
    | "dashboard"
    | "people"
    | "trustee"
    | "heart"
    | "donation"
    | "report"
    | "bell"
    | "admin";
  roles: UserRole[];
  exact?: boolean;
};


const props = withDefaults(
  defineProps<{
    title?: string;
    subtitle?: string;
    showLanguageToggle?: boolean;
    showBackButton?: boolean;
    footerText?: string;
    maxWidth?: string;
  }>(),
  {
    title: "",
    subtitle: "",
    showLanguageToggle: true,
    showBackButton: true,
    footerText: "",
    maxWidth: "4xl",
  }
);


const route = useRoute();
const router = useRouter();

const {
  t,
  locale,
  dir,
  isRTL,
  setLanguage,
} = useLocale();

const auth = useAuth();

const mobileMenuOpen = ref(false);


const navigationItems: NavigationItem[] = [
  {
    to: "/",
    label: "nav.home",
    icon: "home",
    exact: true,
    roles: [
      "admin",
      "trustee",
      "borrower",
      "donor",
    ],
  },
  {
    to: "/loans/new",
    label: "nav.createLoan",
    icon: "plus",
    roles: ["admin"],
  },
  {
    to: "/loans",
    label: "nav.activeLoans",
    icon: "loans",
    roles: [
      "admin",
      "trustee",
      "borrower",
    ],
  },
  {
    to: "/dashboard",
    label: "nav.dashboard",
    icon: "dashboard",
    roles: [
      "admin",
      "trustee",
      "borrower",
      "donor",
    ],
  },
  {
    to: "/borrowers",
    label: "nav.borrowers",
    icon: "people",
    roles: [
      "admin",
      "trustee",
      "borrower",
    ],
  },
  {
    to: "/trustees",
    label: "nav.trustees",
    icon: "trustee",
    roles: [
      "admin",
      "trustee",
      "borrower",
    ],
  },
  {
    to: "/donors",
    label: "nav.donors",
    icon: "heart",
    roles: ["admin"],
  },
  {
    to: "/donations",
    label: "nav.donations",
    icon: "donation",
    roles: [
      "admin",
      "donor",
    ],
  },
  {
    to: "/reports",
    label: "nav.reports",
    icon: "report",
    roles: ["admin"],
  },
  {
    to: "/reminders",
    label: "nav.reminders",
    icon: "bell",
    roles: ["admin"],
  },
  {
    to: "/admins",
    label: "nav.admins",
    icon: "admin",
    roles: ["admin"],
  },
];


const visibleNavigation = computed(() => {
  const role = auth.user.value?.role;

  if (!role) {
    return [];
  }

  return navigationItems.filter(
    (item) =>
      item.roles.includes(role)
  );
});


const roleLabel = computed(() => {
  const role = auth.user.value?.role;

  if (!role) {
    return "";
  }

  return t(`roles.${role}`);
});


const maxWidthClass = computed(() => {
  const widths: Record<
    string,
    string
  > = {
    full: "max-w-[1600px]",
    "7xl": "max-w-7xl",
    "6xl": "max-w-6xl",
    "5xl": "max-w-5xl",
    "4xl": "max-w-4xl",
    "3xl": "max-w-3xl",
    "2xl": "max-w-2xl",
  };

  return (
    widths[props.maxWidth] ||
    widths["4xl"]
  );
});


const drawerTransitionName =
  computed(() =>
    isRTL.value
      ? "slide-right"
      : "slide-left"
  );


function isRouteActive(
  item: NavigationItem
): boolean {
  if (item.exact) {
    return route.path === item.to;
  }

  return (
    route.path === item.to ||
    route.path.startsWith(
      `${item.to}/`
    )
  );
}


function toggleLanguage() {
  setLanguage(
    locale.value === "he"
      ? "en"
      : "he"
  );
}


function goBack() {
  if (window.history.length > 1) {
    router.back();
    return;
  }

  router.push("/");
}


async function performLogout() {
  mobileMenuOpen.value = false;

  try {
    await auth.logout();
  } finally {
    await router.replace({
      name: "Login",
    });
  }
}


watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false;
  }
);
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-right-enter-active,
.slide-right-leave-active,
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.28s ease;
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}

.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(-100%);
}
</style>