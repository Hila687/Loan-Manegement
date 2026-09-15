<template>
  <AppLayout
    :title="t('dashboard.title')"
    :subtitle="t('dashboard.subtitle')"
    :show-language-toggle="true"
    max-width="full"
  >
    <!-- Loading -->
    <div
      v-if="loading"
      class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4"
    >
      <div
        v-for="index in 4"
        :key="index"
        class="h-32 rounded-2xl bg-white border border-line animate-pulse"
      />
    </div>

    <!-- Error -->
    <div
      v-else-if="errorMessage"
      class="rounded-2xl bg-white border border-red-200 p-6 text-center"
    >
      <div
        class="mx-auto w-12 h-12 rounded-xl bg-red-50 text-red-500 flex items-center justify-center mb-4"
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
            d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
          />
        </svg>
      </div>

      <p class="text-ink font-semibold">
        {{ errorMessage }}
      </p>

      <button
        type="button"
        class="mt-4 px-5 py-2.5 rounded-xl bg-brand text-white text-sm font-semibold hover:bg-brand-deep transition"
        @click="loadDashboard"
      >
        {{ t("common.retry") }}
      </button>
    </div>

    <div
      v-else
      class="space-y-5 sm:space-y-6"
    >
      <!-- KPI cards -->
      <section
        class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4"
      >
        <article
          class="dashboard-card"
        >
          <div
            class="dashboard-icon bg-brand/10 text-brand"
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
                d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
              />
            </svg>
          </div>

          <p class="dashboard-label">
            {{ t("dashboard.cards.activeLoans") }}
          </p>

          <p class="dashboard-value">
            {{ dashboard.loan_status.active }}
          </p>
        </article>

        <article
          class="dashboard-card"
        >
          <div
            class="dashboard-icon bg-danger/10 text-danger"
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
                d="M12 8v4m0 4h.01M4.93 19h14.14a2 2 0 001.73-3L13.73 4a2 2 0 00-3.46 0L3.2 16A2 2 0 004.93 19z"
              />
            </svg>
          </div>

          <p class="dashboard-label">
            {{ t("dashboard.cards.overdueLoans") }}
          </p>

          <p class="dashboard-value">
            {{ dashboard.loan_status.overdue }}
          </p>
        </article>

        <article
          class="dashboard-card"
        >
          <div
            class="dashboard-icon bg-success/10 text-success"
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
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>

          <p class="dashboard-label">
            {{ t("dashboard.cards.closedLoans") }}
          </p>

          <p class="dashboard-value">
            {{ dashboard.loan_status.closed }}
          </p>
        </article>

        <article
          class="dashboard-card"
        >
          <div
            class="dashboard-icon bg-violet/10 text-violet"
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
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8V6m0 12v-2"
              />
            </svg>
          </div>

          <p class="dashboard-label">
            {{ donationCardLabel }}
          </p>

          <p class="dashboard-value text-xl sm:text-2xl">
            {{
              formatCurrency(
                donationCardValue
              )
            }}
          </p>
        </article>
      </section>

      <!-- Financial summary -->
      <section
        class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5"
      >
        <article
          class="rounded-2xl bg-gradient-to-br from-brand to-brand-deep text-white p-6 sm:p-7 shadow-lg shadow-brand/15"
        >
          <p
            class="text-white/80 text-sm font-medium"
          >
            {{ t("dashboard.cards.activeAmount") }}
          </p>

          <p
            class="text-3xl sm:text-4xl font-bold mt-2 break-words"
          >
            {{
              formatCurrency(
                dashboard
                  .active_loans_amount
              )
            }}
          </p>

          <p
            class="text-white/75 text-sm mt-4"
          >
            {{ t("dashboard.activeAmountDescription") }}
          </p>
        </article>

        <article
          v-if="auth.isAdmin.value"
          class="rounded-2xl bg-white border border-line/70 p-6 sm:p-7 shadow-sm"
        >
          <p
            class="text-sm font-medium text-muted"
          >
            {{ t("dashboard.cards.totalDonations") }}
          </p>

          <p
            class="text-3xl sm:text-4xl font-bold text-ink mt-2 break-words"
          >
            {{
              formatCurrency(
                dashboard
                  .total_donations_amount
              )
            }}
          </p>

          <p
            class="text-sm text-muted mt-4"
          >
            {{ t("dashboard.donationsDescription") }}
          </p>
        </article>
      </section>

      <!-- People summary for admin -->
      <section
        v-if="
          auth.isAdmin.value &&
          dashboard.people
        "
        class="grid grid-cols-1 sm:grid-cols-3 gap-4"
      >
        <article
          class="rounded-2xl bg-white border border-line/70 p-5 shadow-sm"
        >
          <p class="text-sm text-muted">
            {{ t("dashboard.people.borrowers") }}
          </p>

          <p
            class="text-3xl font-bold text-ink mt-2"
          >
            {{ dashboard.people.borrowers }}
          </p>
        </article>

        <article
          class="rounded-2xl bg-white border border-line/70 p-5 shadow-sm"
        >
          <p class="text-sm text-muted">
            {{ t("dashboard.people.trustees") }}
          </p>

          <p
            class="text-3xl font-bold text-ink mt-2"
          >
            {{ dashboard.people.trustees }}
          </p>
        </article>

        <article
          class="rounded-2xl bg-white border border-line/70 p-5 shadow-sm"
        >
          <p class="text-sm text-muted">
            {{ t("dashboard.people.donors") }}
          </p>

          <p
            class="text-3xl font-bold text-ink mt-2"
          >
            {{ dashboard.people.donors }}
          </p>
        </article>
      </section>

      <!-- Operational chart: loan status -->
      <section
        class="rounded-2xl lg:rounded-3xl bg-white border border-line/70 p-5 sm:p-6 lg:p-7 shadow-sm"
      >
        <div
          class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6"
        >
          <div>
            <h2
              class="text-lg sm:text-xl font-bold text-ink"
            >
              {{ t("dashboard.statusChart.title") }}
            </h2>

            <p
              class="text-sm text-muted mt-1"
            >
              {{ t("dashboard.statusChart.subtitle") }}
            </p>
          </div>

          <span
            class="text-sm font-semibold text-brand"
          >
            {{ totalLoans }}
            {{ t("dashboard.statusChart.loans") }}
          </span>
        </div>

        <div class="space-y-5">
          <div>
            <div
              class="flex items-center justify-between text-sm mb-2"
            >
              <span
                class="font-medium text-ink-soft"
              >
                {{ t("dashboard.status.active") }}
              </span>

              <span
                class="font-semibold text-ink"
              >
                {{ dashboard.loan_status.active }}
              </span>
            </div>

            <div
              class="w-full h-3 rounded-full bg-surface-muted overflow-hidden"
            >
              <div
                class="h-full rounded-full bg-brand transition-all duration-500"
                :style="{
                  width:
                    `${statusPercentage(
                      dashboard.loan_status.active
                    )}%`,
                }"
              />
            </div>
          </div>

          <div>
            <div
              class="flex items-center justify-between text-sm mb-2"
            >
              <span
                class="font-medium text-ink-soft"
              >
                {{ t("dashboard.status.overdue") }}
              </span>

              <span
                class="font-semibold text-ink"
              >
                {{ dashboard.loan_status.overdue }}
              </span>
            </div>

            <div
              class="w-full h-3 rounded-full bg-surface-muted overflow-hidden"
            >
              <div
                class="h-full rounded-full bg-danger transition-all duration-500"
                :style="{
                  width:
                    `${statusPercentage(
                      dashboard.loan_status.overdue
                    )}%`,
                }"
              />
            </div>
          </div>

          <div>
            <div
              class="flex items-center justify-between text-sm mb-2"
            >
              <span
                class="font-medium text-ink-soft"
              >
                {{ t("dashboard.status.closed") }}
              </span>

              <span
                class="font-semibold text-ink"
              >
                {{ dashboard.loan_status.closed }}
              </span>
            </div>

            <div
              class="w-full h-3 rounded-full bg-surface-muted overflow-hidden"
            >
              <div
                class="h-full rounded-full bg-success transition-all duration-500"
                :style="{
                  width:
                    `${statusPercentage(
                      dashboard.loan_status.closed
                    )}%`,
                }"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Operational chart: community -->
      <section
        v-if="
          auth.isAdmin.value &&
          dashboard.by_community.length
        "
        class="rounded-2xl lg:rounded-3xl bg-white border border-line/70 p-5 sm:p-6 lg:p-7 shadow-sm"
      >
        <div class="mb-6">
          <h2
            class="text-lg sm:text-xl font-bold text-ink"
          >
            {{ t("dashboard.communityChart.title") }}
          </h2>

          <p
            class="text-sm text-muted mt-1"
          >
            {{ t("dashboard.communityChart.subtitle") }}
          </p>
        </div>

        <div class="space-y-4">
          <div
            v-for="community in dashboard.by_community"
            :key="community.community"
            class="rounded-xl border border-line/60 bg-surface-muted p-4"
          >
            <div
              class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 mb-3"
            >
              <p
                class="font-semibold text-ink"
              >
                {{ community.community }}
              </p>

              <p
                class="text-sm text-muted"
              >
                {{
                  community.loans_count
                }}
                {{ t("dashboard.statusChart.loans") }}
                ·
                {{
                  formatCurrency(
                    community.total_amount
                  )
                }}
              </p>
            </div>

            <div
              class="w-full h-2.5 rounded-full bg-line overflow-hidden"
            >
              <div
                class="h-full rounded-full bg-gradient-to-r from-brand to-sky"
                :style="{
                  width:
                    `${communityPercentage(
                      community.loans_count
                    )}%`,
                }"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Trustee context -->
      <section
        v-if="auth.isTrustee.value"
        class="rounded-2xl bg-white border border-line/70 p-5 sm:p-6 shadow-sm"
      >
        <h2
          class="text-lg font-bold text-ink"
        >
          {{ t("dashboard.trustee.title") }}
        </h2>

        <div
          class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-5"
        >
          <div
            class="rounded-xl bg-canvas p-4"
          >
            <p
              class="text-sm text-muted"
            >
              {{ t("dashboard.trustee.community") }}
            </p>

            <p
              class="text-lg font-semibold text-ink mt-1"
            >
              {{ dashboard.community || "—" }}
            </p>
          </div>

          <div
            class="rounded-xl bg-canvas p-4"
          >
            <p
              class="text-sm text-muted"
            >
              {{ t("dashboard.trustee.borrowers") }}
            </p>

            <p
              class="text-lg font-semibold text-ink mt-1"
            >
              {{ dashboard.borrowers_count }}
            </p>
          </div>
        </div>
      </section>

      <!-- Donor context -->
      <section
        v-if="auth.isDonor.value"
        class="rounded-2xl bg-white border border-line/70 p-5 sm:p-6 shadow-sm"
      >
        <h2
          class="text-lg font-bold text-ink"
        >
          {{ t("dashboard.donor.title") }}
        </h2>

        <p
          class="text-sm text-muted mt-1"
        >
          {{ t("dashboard.donor.subtitle") }}
        </p>

        <p
          class="text-3xl font-bold text-success mt-5"
        >
          {{
            formatCurrency(
              dashboard
                .my_donations_amount
            )
          }}
        </p>
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

import AppLayout from "../components/AppLayout.vue";

import {
  useLocale,
} from "../composables/useLocale";

import {
  useAuth,
} from "../composables/useAuth";

import api from "../services/api";


type CommunitySummary = {
  community: string;
  loans_count: number;
  total_amount: number;
};


type DashboardData = {
  loan_status: {
    active: number;
    overdue: number;
    closed: number;
  };

  active_loans_amount: number;
  total_donations_amount: number;

  people: {
    borrowers: number;
    trustees: number;
    donors: number;
  } | null;

  by_community:
    CommunitySummary[];

  community: string;
  borrowers_count: number;

  my_donations_amount: number;
};


const {
  t,
  locale,
} = useLocale();

const auth = useAuth();

const loading = ref(true);
const errorMessage =
  ref<string | null>(null);


const dashboard =
  reactive<DashboardData>({
    loan_status: {
      active: 0,
      overdue: 0,
      closed: 0,
    },

    active_loans_amount: 0,
    total_donations_amount: 0,

    people: null,

    by_community: [],

    community: "",
    borrowers_count: 0,

    my_donations_amount: 0,
  });


const totalLoans = computed(
  () =>
    dashboard.loan_status.active +
    dashboard.loan_status.overdue +
    dashboard.loan_status.closed
);


const maximumCommunityLoans =
  computed(() => {
    if (
      dashboard.by_community.length ===
      0
    ) {
      return 0;
    }

    return Math.max(
      ...dashboard.by_community.map(
        (item) =>
          item.loans_count
      )
    );
  });


const donationCardLabel =
  computed(() =>
    auth.isDonor.value
      ? t(
          "dashboard.cards.myDonations"
        )
      : t(
          "dashboard.cards.totalDonations"
        )
  );


const donationCardValue =
  computed(() =>
    auth.isDonor.value
      ? dashboard
          .my_donations_amount
      : dashboard
          .total_donations_amount
  );


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


function statusPercentage(
  count: number
): number {
  if (totalLoans.value === 0) {
    return 0;
  }

  return Math.min(
    100,
    Math.round(
      (count /
        totalLoans.value) *
        100
    )
  );
}


function communityPercentage(
  count: number
): number {
  if (
    maximumCommunityLoans.value ===
    0
  ) {
    return 0;
  }

  return Math.min(
    100,
    Math.round(
      (count /
        maximumCommunityLoans.value) *
        100
    )
  );
}


async function loadDashboard() {
  loading.value = true;
  errorMessage.value = null;

  try {
    const response =
      await api.get(
        "/dashboard/overview/"
      );

    const data =
      response.data || {};

    dashboard.loan_status = {
      active:
        Number(
          data.loan_status?.active ||
            0
        ),

      overdue:
        Number(
          data.loan_status
            ?.overdue ||
            0
        ),

      closed:
        Number(
          data.loan_status?.closed ||
            0
        ),
    };

    dashboard.active_loans_amount =
      Number(
        data.active_loans_amount ||
          0
      );

    dashboard.total_donations_amount =
      Number(
        data.total_donations_amount ||
          0
      );

    dashboard.people =
      data.people
        ? {
            borrowers:
              Number(
                data.people
                  .borrowers ||
                  0
              ),

            trustees:
              Number(
                data.people
                  .trustees ||
                  0
              ),

            donors:
              Number(
                data.people
                  .donors ||
                  0
              ),
          }
        : null;

    dashboard.by_community =
      Array.isArray(
        data.by_community
      )
        ? data.by_community.map(
            (
              item: any
            ): CommunitySummary => ({
              community:
                String(
                  item.community ||
                    ""
                ),

              loans_count:
                Number(
                  item.loans_count ||
                    0
                ),

              total_amount:
                Number(
                  item.total_amount ||
                    0
                ),
            })
          )
        : [];

    dashboard.community =
      String(
        data.community || ""
      );

    dashboard.borrowers_count =
      Number(
        data.borrowers_count || 0
      );

    dashboard.my_donations_amount =
      Number(
        data.my_donations_amount ||
          0
      );
  } catch (error: any) {
    errorMessage.value =
      error?.response?.data
        ?.detail ||
      t(
        "dashboard.messages.loadError"
      );
  } finally {
    loading.value = false;
  }
}


onMounted(() => {
  loadDashboard();
});
</script>

<style scoped>
.dashboard-card {
  border: 1px solid rgba(229, 231, 235, 0.7);
  border-radius: 1rem;
  background: white;
  padding: 1.25rem;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.05);
  transition:
    box-shadow 0.2s ease;
}

.dashboard-card:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.dashboard-icon {
  display: flex;
  width: 2.75rem;
  height: 2.75rem;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  border-radius: 0.75rem;
}

.dashboard-label {
  color: var(--color-muted);
  font-size: 0.875rem;
  font-weight: 500;
}

.dashboard-value {
  margin-top: 0.25rem;
  color: var(--color-ink);
  font-size: 1.875rem;
  line-height: 2.25rem;
  font-weight: 700;
}

@media (min-width: 640px) {
  .dashboard-card {
    padding: 1.5rem;
  }
}
</style>