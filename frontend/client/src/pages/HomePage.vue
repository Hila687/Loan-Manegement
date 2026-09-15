<template>
  <AppLayout
    :title="t('home.title')"
    :subtitle="t('home.subtitle')"
    :show-language-toggle="true"
    :show-back-button="false"
    max-width="full"
  >
    <div
      class="flex flex-col gap-4 sm:gap-5 lg:gap-6"
    >
      <!-- Welcome section -->
      <section
        class="rounded-2xl lg:rounded-3xl bg-gradient-to-br from-brand via-[#0066CC] to-brand-deep p-6 sm:p-8 lg:p-10 text-white shadow-xl"
      >
        <div
          class="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-5 mb-6"
        >
          <div
            class="flex h-14 w-14 sm:h-16 sm:w-16 lg:h-20 lg:w-20 items-center justify-center rounded-2xl lg:rounded-3xl bg-white/20 backdrop-blur-sm shadow-lg flex-shrink-0"
          >
            <svg
              class="w-7 h-7 sm:w-8 sm:h-8 lg:w-10 lg:h-10"
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

          <div class="flex-1 min-w-0">
            <p
              class="text-white/80 text-sm sm:text-base font-medium mb-1"
            >
              {{ t("home.welcome") }}
            </p>

            <h2
              class="text-2xl sm:text-3xl lg:text-4xl font-bold break-words"
            >
              {{ auth.displayName.value }}
            </h2>

            <p
              class="text-white/90 text-sm sm:text-base lg:text-lg mt-2 max-w-3xl"
            >
              {{ welcomeMessage }}
            </p>
          </div>
        </div>

        <!-- Summary cards -->
        <div
          class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 lg:gap-5"
        >
          <div
            class="rounded-xl lg:rounded-2xl bg-white/10 backdrop-blur-sm p-4 sm:p-5 lg:p-6 border border-white/20"
          >
            <p
              class="text-white/80 text-xs sm:text-sm lg:text-base font-medium mb-1 sm:mb-2"
            >
              {{ t("home.stats.activeLoans") }}
            </p>

            <div
              v-if="loading"
              class="h-9 w-20 rounded-lg bg-white/20 animate-pulse"
            />

            <p
              v-else
              class="text-2xl sm:text-3xl lg:text-4xl font-bold"
            >
              {{ stats.activeLoans }}
            </p>
          </div>

          <div
            class="rounded-xl lg:rounded-2xl bg-white/10 backdrop-blur-sm p-4 sm:p-5 lg:p-6 border border-white/20"
          >
            <p
              class="text-white/80 text-xs sm:text-sm lg:text-base font-medium mb-1 sm:mb-2"
            >
              {{ t("home.stats.totalAmount") }}
            </p>

            <div
              v-if="loading"
              class="h-9 w-36 rounded-lg bg-white/20 animate-pulse"
            />

            <p
              v-else
              class="text-2xl sm:text-3xl lg:text-4xl font-bold break-words"
            >
              {{ formatCurrency(stats.totalAmount) }}
            </p>
          </div>
        </div>
      </section>

      <!-- Error notice -->
      <div
        v-if="loadError"
        class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
      >
        <p
          class="text-sm text-amber-800"
        >
          {{ t("home.messages.summaryLoadError") }}
        </p>

        <button
          type="button"
          class="self-start sm:self-auto text-sm font-semibold text-amber-900 hover:underline"
          @click="loadSummary"
        >
          {{ t("common.retry") }}
        </button>
      </div>

      <!-- Primary actions -->
      <section
        class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5 lg:gap-6"
      >
        <button
          v-if="auth.isAdmin.value"
          type="button"
          class="group relative overflow-hidden rounded-2xl lg:rounded-3xl border-2 border-brand bg-gradient-to-br from-brand to-brand-deep p-6 sm:p-8 lg:p-10 text-white transition-all duration-300 hover:shadow-2xl hover:shadow-brand/30 hover:scale-[1.01] active:scale-[0.99]"
          @click="router.push('/loans/new')"
        >
          <div
            class="absolute top-0 end-0 w-32 h-32 bg-white/10 rounded-full -me-16 -mt-16 group-hover:scale-150 transition-transform duration-500"
          />

          <div class="relative z-10">
            <div
              class="flex items-center justify-between mb-5 sm:mb-6"
            >
              <div
                class="flex h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16 items-center justify-center rounded-xl lg:rounded-2xl bg-white/20 backdrop-blur-sm group-hover:scale-110 transition-transform"
              >
                <svg
                  class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>

              <span
                class="rounded-full bg-white/20 px-3 sm:px-4 py-1 sm:py-1.5 text-xs sm:text-sm font-semibold border border-white/30"
              >
                {{ t("home.actions.createLoan.badge") }}
              </span>
            </div>

            <div
              :class="
                isRTL
                  ? 'text-right'
                  : 'text-left'
              "
            >
              <h3
                class="text-xl sm:text-2xl lg:text-3xl font-bold mb-2 sm:mb-3"
              >
                {{ t("home.actions.createLoan.title") }}
              </h3>

              <p
                class="text-white/90 text-sm sm:text-base lg:text-lg"
              >
                {{ t("home.actions.createLoan.description") }}
              </p>
            </div>
          </div>
        </button>

        <button
          v-if="canViewLoans"
          type="button"
          class="group relative overflow-hidden rounded-2xl lg:rounded-3xl border-2 border-line bg-white p-6 sm:p-8 lg:p-10 transition-all duration-300 hover:border-brand hover:shadow-2xl hover:scale-[1.01] active:scale-[0.99]"
          @click="router.push('/loans')"
        >
          <div
            class="absolute top-0 end-0 w-32 h-32 bg-brand/5 rounded-full -me-16 -mt-16 group-hover:scale-150 transition-transform duration-500"
          />

          <div class="relative z-10">
            <div
              class="flex items-center justify-between mb-5 sm:mb-6"
            >
              <div
                class="flex h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16 items-center justify-center rounded-xl lg:rounded-2xl bg-brand/10 group-hover:bg-brand/20 group-hover:scale-110 transition-all"
              >
                <svg
                  class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-brand"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
                  />
                </svg>
              </div>
            </div>

            <div
              :class="
                isRTL
                  ? 'text-right'
                  : 'text-left'
              "
            >
              <h3
                class="text-xl sm:text-2xl lg:text-3xl font-bold text-ink mb-2 sm:mb-3"
              >
                {{ loansCardTitle }}
              </h3>

              <p
                class="text-muted text-sm sm:text-base lg:text-lg"
              >
                {{ loansCardDescription }}
              </p>
            </div>
          </div>
        </button>

        <button
          v-if="auth.isDonor.value"
          type="button"
          class="group relative overflow-hidden rounded-2xl lg:rounded-3xl border-2 border-line bg-white p-6 sm:p-8 lg:p-10 transition-all duration-300 hover:border-success hover:shadow-2xl hover:scale-[1.01] active:scale-[0.99]"
          @click="router.push('/donations')"
        >
          <div class="relative z-10">
            <div
              class="flex h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16 items-center justify-center rounded-xl lg:rounded-2xl bg-success/10 mb-5"
            >
              <svg
                class="w-7 h-7 text-success"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1"
                />
              </svg>
            </div>

            <div
              :class="
                isRTL
                  ? 'text-right'
                  : 'text-left'
              "
            >
              <h3
                class="text-xl sm:text-2xl lg:text-3xl font-bold text-ink mb-2 sm:mb-3"
              >
                {{ t("home.actions.viewDonations.title") }}
              </h3>

              <p
                class="text-muted text-sm sm:text-base lg:text-lg"
              >
                {{ t("home.actions.viewDonations.description") }}
              </p>
            </div>
          </div>
        </button>
      </section>

      <!-- Secondary actions -->
      <section
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-5"
      >
        <button
          type="button"
          class="home-secondary-card"
          @click="router.push('/dashboard')"
        >
          <div
            class="home-secondary-icon bg-warning/10 text-warning"
          >
            <svg
              class="w-6 h-6 sm:w-7 sm:h-7"
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
          </div>

          <div
            class="flex-1 min-w-0"
            :class="
              isRTL
                ? 'text-right'
                : 'text-left'
            "
          >
            <p
              class="text-sm sm:text-base font-semibold text-ink"
            >
              {{ t("home.quickActions.dashboard") }}
            </p>

            <p
              class="text-xs sm:text-sm text-muted mt-1"
            >
              {{ t("home.quickActions.dashboardDesc") }}
            </p>
          </div>
        </button>

        <button
          v-if="auth.isAdmin.value"
          type="button"
          class="home-secondary-card"
          @click="router.push('/reports')"
        >
          <div
            class="home-secondary-icon bg-success/10 text-success"
          >
            <svg
              class="w-6 h-6 sm:w-7 sm:h-7"
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
          </div>

          <div
            class="flex-1 min-w-0"
            :class="
              isRTL
                ? 'text-right'
                : 'text-left'
            "
          >
            <p
              class="text-sm sm:text-base font-semibold text-ink"
            >
              {{ t("home.quickActions.reports") }}
            </p>

            <p
              class="text-xs sm:text-sm text-muted mt-1"
            >
              {{ t("home.quickActions.reportsDesc") }}
            </p>
          </div>
        </button>

        <button
          v-if="auth.isAdmin.value"
          type="button"
          class="home-secondary-card"
          @click="router.push('/reminders')"
        >
          <div
            class="home-secondary-icon bg-violet/10 text-violet"
          >
            <svg
              class="w-6 h-6 sm:w-7 sm:h-7"
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
          </div>

          <div
            class="flex-1 min-w-0"
            :class="
              isRTL
                ? 'text-right'
                : 'text-left'
            "
          >
            <p
              class="text-sm sm:text-base font-semibold text-ink"
            >
              {{ t("home.quickActions.reminders") }}
            </p>

            <p
              class="text-xs sm:text-sm text-muted mt-1"
            >
              {{ t("home.quickActions.remindersDesc") }}
            </p>
          </div>
        </button>
      </section>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue";

import {
  useRouter,
} from "vue-router";

import AppLayout from "../components/AppLayout.vue";

import {
  useLocale,
} from "../composables/useLocale";

import {
  useAuth,
} from "../composables/useAuth";

import api from "../services/api";


const router = useRouter();

const {
  t,
  isRTL,
  locale,
} = useLocale();

const auth = useAuth();

const loading = ref(false);
const loadError = ref(false);

const stats = reactive({
  activeLoans: 0,
  totalAmount: 0,
});


const canViewLoans = computed(
  () =>
    auth.isAdmin.value ||
    auth.isTrustee.value ||
    auth.isBorrower.value
);


const welcomeMessage = computed(
  () => {
    if (auth.isAdmin.value) {
      return t(
        "home.roleMessages.admin"
      );
    }

    if (auth.isTrustee.value) {
      return t(
        "home.roleMessages.trustee"
      );
    }

    if (auth.isBorrower.value) {
      return t(
        "home.roleMessages.borrower"
      );
    }

    return t(
      "home.roleMessages.donor"
    );
  }
);


const loansCardTitle = computed(
  () => {
    if (auth.isBorrower.value) {
      return t(
        "home.actions.myLoan.title"
      );
    }

    if (auth.isTrustee.value) {
      return t(
        "home.actions.communityLoans.title"
      );
    }

    return t(
      "home.actions.viewLoans.title"
    );
  }
);


const loansCardDescription =
  computed(() => {
    if (auth.isBorrower.value) {
      return t(
        "home.actions.myLoan.description"
      );
    }

    if (auth.isTrustee.value) {
      return t(
        "home.actions.communityLoans.description"
      );
    }

    return t(
      "home.actions.viewLoans.description"
    );
  });


function formatCurrency(
  value: number
): string {
  return new Intl.NumberFormat(
    locale.value === "he"
      ? "he-IL"
      : "en-US",
    {
      style: "currency",
      currency: "ILS",
      maximumFractionDigits: 2,
    }
  ).format(
    Number(value || 0)
  );
}


async function loadSummary() {
  loading.value = true;
  loadError.value = false;

  try {
    const response =
      await api.get(
        "/dashboard/loan-summary/"
      );

    stats.activeLoans =
      Number(
        response.data
          ?.active_loans_count ||
          0
      );

    stats.totalAmount =
      Number(
        response.data
          ?.total_active_loans_amount ||
          0
      );
  } catch {
    stats.activeLoans = 0;
    stats.totalAmount = 0;
    loadError.value = true;
  } finally {
    loading.value = false;
  }
}


onMounted(() => {
  loadSummary();
});
</script>

<style scoped>
.home-secondary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 2px solid var(--color-line);
  border-radius: 0.75rem;
  background: white;
  padding: 1.25rem;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.home-secondary-card:hover {
  border-color: rgba(0, 122, 255, 0.4);
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -4px rgba(0, 0, 0, 0.1);
  transform: scale(1.01);
}

.home-secondary-card:active {
  transform: scale(0.99);
}

.home-secondary-icon {
  display: flex;
  width: 3rem;
  height: 3rem;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  transition: transform 0.2s ease;
}

.home-secondary-card:hover
.home-secondary-icon {
  transform: scale(1.1);
}

@media (min-width: 640px) {
  .home-secondary-card {
    padding: 1.5rem;
  }

  .home-secondary-icon {
    width: 3.5rem;
    height: 3.5rem;
  }
}

@media (min-width: 1024px) {
  .home-secondary-card,
  .home-secondary-icon {
    border-radius: 1rem;
  }
}
</style>