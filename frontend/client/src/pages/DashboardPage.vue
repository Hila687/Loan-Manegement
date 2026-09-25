<template>
  <AppLayout
    :title="t('dashboard.title')"
    :show-language-toggle="true"
    max-width="full"
  >
    <div
      v-if="loading"
      class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
    >
      <div
        v-for="index in 4"
        :key="index"
        class="h-36 animate-pulse rounded-2xl border border-line bg-white"
      ></div>
    </div>

    <div
      v-else-if="errorMessage"
      class="rounded-2xl border border-red-200 bg-white p-6 text-center"
    >
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-500"
      >
        <svg
          class="h-6 w-6"
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

      <p class="mt-4 font-semibold text-ink">
        {{ errorMessage }}
      </p>

      <button
        type="button"
        class="mt-4 rounded-xl bg-brand px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-deep"
        @click="loadDashboard"
      >
        {{ t("common.retry") }}
      </button>
    </div>

    <div v-else class="space-y-5 sm:space-y-6">
      <!-- Main status shortcuts -->
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <button
          type="button"
          class="dashboard-card dashboard-card-button text-start"
          @click="openLoans('ACTIVE')"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="dashboard-icon bg-brand/10 text-brand">
              <svg
                class="h-6 w-6"
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

          </div>

          <p class="dashboard-label">{{ activeLoansLabel }}</p>
          <p class="dashboard-value">{{ dashboard.loan_status.active }}</p>
          <p class="dashboard-hint">{{ openLoansLabel }}</p>
        </button>

        <button
          type="button"
          class="dashboard-card dashboard-card-button text-start"
          @click="openLoans('OVERDUE')"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="dashboard-icon bg-danger/10 text-danger">
              <svg
                class="h-6 w-6"
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

          </div>

          <p class="dashboard-label">{{ problematicLoansLabel }}</p>
          <p class="dashboard-value text-danger">{{ dashboard.loan_status.overdue }}</p>
          <p class="dashboard-hint">{{ problematicHint }}</p>
        </button>

        <button
          type="button"
          class="dashboard-card text-start"
          :class="auth.isAdmin.value ? 'dashboard-card-button' : ''"
          :disabled="!auth.isAdmin.value"
          @click="openArchive"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="dashboard-icon bg-success/10 text-success">
              <svg
                class="h-6 w-6"
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

          </div>

          <p class="dashboard-label">{{ completedLoansLabel }}</p>
          <p class="dashboard-value">{{ dashboard.loan_status.closed }}</p>
          <p class="dashboard-hint">
            {{ auth.isAdmin.value ? archiveHint : completedReadOnlyHint }}
          </p>
        </button>

        <button
          type="button"
          class="dashboard-card text-start"
          :class="canOpenDonations ? 'dashboard-card-button' : ''"
          :disabled="!canOpenDonations"
          @click="openDonations"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="dashboard-icon bg-violet/10 text-violet">
              <svg
                class="h-6 w-6"
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

          </div>

          <p class="dashboard-label">{{ donationCardLabel }}</p>
          <p dir="ltr" class="dashboard-value dashboard-value-money">
            {{ formatCurrency(donationCardValue) }}
          </p>
          <p class="dashboard-hint">{{ donationsHint }}</p>
        </button>
      </section>

      <!-- Quick overview -->
      <section class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <article
          class="rounded-2xl bg-gradient-to-br from-brand to-brand-deep p-6 text-white shadow-lg shadow-brand/15 sm:p-7"
        >
          <div class="flex items-start justify-between gap-3">
            <p class="text-sm font-medium text-white/80">
              {{ openAmountLabel }}
            </p>

            <span class="flex-shrink-0 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold text-white">
              {{ openLoansCount }}
            </span>
          </div>

          <p
            dir="ltr"
            class="mt-2 whitespace-nowrap text-[clamp(1.45rem,6vw,2.25rem)] font-bold leading-tight"
          >
            {{ formatCurrency(openLoansAmount) }}
          </p>

          <div class="mt-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <p class="max-w-md text-sm leading-6 text-white/75">
              {{ openAmountDescription }}
            </p>

            <button
              type="button"
              class="inline-flex cursor-pointer flex-shrink-0 items-center justify-center gap-2 rounded-xl bg-white/15 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/25"
              @click="router.push('/loans')"
            >
              {{ openLoansLabel }}
            </button>
          </div>
        </article>

        <article
          v-if="auth.isAdmin.value"
          class="rounded-2xl border border-line bg-white p-6 shadow-sm sm:p-7"
        >
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-brand/10 text-brand">
            <svg
              class="h-6 w-6"
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

          <h2 class="mt-4 text-lg font-bold text-ink">
            {{ reportsShortcutTitle }}
          </h2>

          <p class="mt-2 text-sm leading-6 text-muted">
            {{ reportsShortcutDescription }}
          </p>

          <button
            type="button"
            class="mt-5 inline-flex items-center gap-2 rounded-xl border border-brand/20 bg-brand/5 px-4 py-2.5 text-sm font-semibold text-brand transition hover:bg-brand/10"
            @click="router.push('/reports')"
          >
            {{ reportsShortcutAction }}
          </button>
        </article>

        <article
          v-else-if="auth.isTrustee.value"
          class="rounded-2xl border border-line bg-white p-6 shadow-sm sm:p-7"
        >
          <p class="text-sm text-muted">{{ t("dashboard.trustee.community") }}</p>
          <p class="mt-1 text-xl font-bold text-ink">{{ dashboard.community || "—" }}</p>

          <div class="mt-5 rounded-xl bg-canvas p-4">
            <p class="text-sm text-muted">{{ t("dashboard.trustee.borrowers") }}</p>
            <p class="mt-1 text-2xl font-bold text-ink">{{ dashboard.borrowers_count }}</p>
          </div>
        </article>

        <article
          v-else-if="auth.isDonor.value"
          class="rounded-2xl border border-line bg-white p-6 shadow-sm sm:p-7"
        >
          <p class="text-sm text-muted">{{ t("dashboard.donor.title") }}</p>
          <p class="mt-2 text-sm leading-6 text-muted">{{ t("dashboard.donor.subtitle") }}</p>
          <p class="mt-5 text-3xl font-bold text-success">
            {{ formatCurrency(dashboard.my_donations_amount) }}
          </p>
        </article>
      </section>

      <!-- People shortcuts -->
      <section
        v-if="auth.isAdmin.value && dashboard.people"
        class="grid grid-cols-1 gap-4 sm:grid-cols-3"
      >
        <button
          v-for="person in peopleShortcuts"
          :key="person.key"
          type="button"
          class="cursor-pointer rounded-2xl border border-line bg-white p-5 text-start shadow-sm transition hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-md"
          @click="router.push(person.to)"
        >
          <div class="flex items-center justify-between gap-3">
            <p class="text-sm font-medium text-muted">{{ person.label }}</p>
          </div>

          <p class="mt-2 text-3xl font-bold text-ink">{{ person.value }}</p>
        </button>
      </section>

      <!-- Status overview -->
      <section
        class="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6 lg:rounded-3xl lg:p-7"
      >
        <div class="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-lg font-bold text-ink sm:text-xl">
              {{ statusOverviewTitle }}
            </h2>

            <p
              v-if="statusOverviewSubtitle"
              class="mt-1 text-sm text-muted"
            >
              {{ statusOverviewSubtitle }}
            </p>
          </div>

          <span class="text-sm font-semibold text-brand">
            {{ totalLoans }} {{ totalLoansLabel }}
          </span>
        </div>

        <div class="space-y-5">
          <button
            v-for="row in statusRows"
            :key="row.status"
            type="button"
            class="block w-full cursor-pointer rounded-xl p-2 text-start transition hover:bg-canvas"
            @click="openStatusRow(row.status)"
          >
            <div class="mb-2 flex items-center justify-between gap-3 text-sm">
              <span class="font-semibold text-ink-soft">{{ row.label }}</span>
              <span class="font-bold text-ink">{{ row.count }}</span>
            </div>

            <div class="h-3 w-full overflow-hidden rounded-full bg-surface-muted">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="row.barClass"
                :style="{ width: `${statusPercentage(row.count)}%` }"
              ></div>
            </div>
          </button>
        </div>
      </section>

      <!-- Community overview -->
      <section
        v-if="auth.isAdmin.value && dashboard.by_community.length"
        class="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6 lg:rounded-3xl lg:p-7"
      >
        <div class="mb-6">
          <h2 class="text-lg font-bold text-ink sm:text-xl">
            {{ communityTitle }}
          </h2>


        </div>

        <div class="space-y-4">
          <div
            v-for="community in dashboard.by_community"
            :key="community.community"
            class="rounded-xl border border-line/60 bg-surface-muted p-4"
          >
            <div class="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
              <p class="font-semibold text-ink">{{ community.community }}</p>

              <p class="text-sm text-muted">
                {{ community.loans_count }} {{ totalLoansLabel }}
                ·
                {{ formatCurrency(community.total_amount) }}
              </p>
            </div>

            <div class="h-2.5 w-full overflow-hidden rounded-full bg-line">
              <div
                class="h-full rounded-full bg-gradient-to-r from-brand to-sky"
                :style="{ width: `${communityPercentage(community.loans_count)}%` }"
              ></div>
            </div>
          </div>
        </div>
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
import { useLocale } from "../composables/useLocale";
import { useAuth } from "../composables/useAuth";
import api from "../services/api";


type CommunitySummary = {
  community: string;
  loans_count: number;
  total_amount: number;
};

type LoanStatusKey =
  | "ACTIVE"
  | "OVERDUE"
  | "CLOSED";

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
  by_community: CommunitySummary[];
  community: string;
  borrowers_count: number;
  my_donations_amount: number;
};

const { t, locale } = useLocale();
const auth = useAuth();
const router = useRouter();

const loading = ref(true);
const errorMessage = ref<string | null>(null);

const dashboard = reactive<DashboardData>({
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

function text(
  he: string,
  en: string,
  es: string
): string {
  if (locale.value === "he") {
    return he;
  }

  if (locale.value === "es") {
    return es;
  }

  return en;
}

const openLoansAmount = ref(0);
const openLoansCount = ref(0);

const activeLoansLabel = computed(() =>
  text("הלוואות פעילות", "Active loans", "Préstamos activos")
);

const problematicLoansLabel = computed(() =>
  text("הלוואות בעייתיות", "Needs attention", "Préstamos problemáticos")
);

const completedLoansLabel = computed(() =>
  text("הלוואות שהסתיימו", "Completed loans", "Préstamos finalizados")
);

const openLoansLabel = computed(() =>
  text("לצפייה בהלוואות", "View loans", "Ver préstamos")
);

const openAmountLabel = computed(() =>
  text("סכום הלוואות פתוחות", "Open loan amount", "Importe de préstamos abiertos")
);

const openAmountDescription = computed(() =>
  text(
    "כולל הלוואות פעילות והלוואות בעייתיות שעדיין לא הסתיימו.",
    "Includes active and problematic loans that have not yet been completed.",
    "Incluye préstamos activos y problemáticos que aún no han finalizado."
  )
);

const problematicHint = computed(() =>
  text("דורשות תשומת לב", "Require attention", "Requieren atención")
);

const archiveHint = computed(() =>
  text("לצפייה בארכיון", "Open archive", "Abrir archivo")
);

const completedReadOnlyHint = computed(() =>
  text("הלוואות שהושלמו", "Completed loans", "Préstamos finalizados")
);

const donationsHint = computed(() =>
  text("לצפייה בתרומות", "View donations", "Ver donaciones")
);

const reportsShortcutTitle = computed(() =>
  text("דוחות וסיכומים", "Reports & summaries", "Informes y resúmenes")
);

const reportsShortcutDescription = computed(() =>
  text(
    "סינון וסיכום נתוני הלוואות לפי הצורך.",
    "Filter and summarize loan data as needed.",
    "Filtra y resume los datos de préstamos según sea necesario."
  )
);

const reportsShortcutAction = computed(() =>
  text("מעבר לדוחות", "Open reports", "Abrir informes")
);

const statusOverviewTitle = computed(() =>
  text("מצב ההלוואות", "Loan status", "Estado de préstamos")
);

const statusOverviewSubtitle = computed(() => "");

const totalLoansLabel = computed(() =>
  text("הלוואות", "loans", "préstamos")
);


const communityTitle = computed(() =>
  text(
    "הלוואות לפי קהילה",
    "Loans by community",
    "Préstamos por comunidad"
  )
);

const donationCardLabel = computed(() =>
  auth.isDonor.value
    ? text("התרומות שלי", "My donations", "Mis donaciones")
    : text("סך התרומות", "Total donations", "Total de donaciones")
);

const donationCardValue = computed(() =>
  auth.isDonor.value
    ? dashboard.my_donations_amount
    : dashboard.total_donations_amount
);

const canOpenDonations = computed(() =>
  auth.isAdmin.value || auth.isDonor.value
);

const totalLoans = computed(() =>
  dashboard.loan_status.active +
  dashboard.loan_status.overdue +
  dashboard.loan_status.closed
);

const maximumCommunityLoans = computed(() => {
  if (dashboard.by_community.length === 0) {
    return 0;
  }

  return Math.max(
    ...dashboard.by_community.map((item) => item.loans_count)
  );
});

const peopleShortcuts = computed(() => {
  if (!dashboard.people) {
    return [];
  }

  return [
    {
      key: "borrowers",
      label: text("לווים", "Borrowers", "Prestatarios"),
      value: dashboard.people.borrowers,
      to: "/borrowers",
    },
    {
      key: "trustees",
      label: text("נאמנים", "Trustees", "Responsables"),
      value: dashboard.people.trustees,
      to: "/trustees",
    },
    {
      key: "donors",
      label: text("תורמים", "Donors", "Donantes"),
      value: dashboard.people.donors,
      to: "/donors",
    },
  ];
});

const statusRows = computed(() => [
  {
    status: "ACTIVE" as LoanStatusKey,
    label: activeLoansLabel.value,
    count: dashboard.loan_status.active,
    barClass: "bg-brand",
  },
  {
    status: "OVERDUE" as LoanStatusKey,
    label: problematicLoansLabel.value,
    count: dashboard.loan_status.overdue,
    barClass: "bg-danger",
  },
  {
    status: "CLOSED" as LoanStatusKey,
    label: completedLoansLabel.value,
    count: dashboard.loan_status.closed,
    barClass: "bg-success",
  },
]);

function formatCurrency(value: number): string {
  const formatterLocale =
    locale.value === "he"
      ? "he-IL"
      : locale.value === "es"
        ? "es-ES"
        : "en-US";

  const formatted = new Intl.NumberFormat(
    formatterLocale,
    {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }
  ).format(Number(value || 0));

  return `₪\u00A0${formatted}`;
}

function statusPercentage(count: number): number {
  if (totalLoans.value === 0) {
    return 0;
  }

  return Math.min(
    100,
    Math.round((count / totalLoans.value) * 100)
  );
}

function communityPercentage(count: number): number {
  if (maximumCommunityLoans.value === 0) {
    return 0;
  }

  return Math.min(
    100,
    Math.round((count / maximumCommunityLoans.value) * 100)
  );
}

function openLoans(status: "ACTIVE" | "OVERDUE"): void {
  router.push({
    path: "/loans",
    query: {
      status,
    },
  });
}

function openArchive(): void {
  if (!auth.isAdmin.value) {
    return;
  }

  router.push("/archive");
}

function openDonations(): void {
  if (!canOpenDonations.value) {
    return;
  }

  router.push("/donations");
}

function openStatusRow(status: LoanStatusKey): void {
  if (status === "CLOSED") {
    openArchive();
    return;
  }

  openLoans(status);
}

function summarizeOpenLoans(
  rows: any[]
): void {
  const openRows = rows.filter(
    (loan) =>
      String(
        loan?.status || "ACTIVE"
      ).toUpperCase() !== "CLOSED"
  );

  openLoansCount.value = openRows.length;

  openLoansAmount.value = openRows.reduce(
    (total: number, loan: any) =>
      total + Number(loan?.amount || 0),
    0
  );
}

async function loadDashboard(): Promise<void> {
  loading.value = true;
  errorMessage.value = null;

  try {
    const requests: Promise<any>[] = [
      api.get("/dashboard/overview/"),
    ];

    if (
      auth.isAdmin.value ||
      auth.isTrustee.value ||
      auth.isBorrower.value
    ) {
      requests.push(
        api.get("/loans/", {
          params: {
            type: "all",
          },
        })
      );
    }

    const results = await Promise.all(requests);
    const data = results[0].data || {};

    dashboard.loan_status = {
      active: Number(data.loan_status?.active || 0),
      overdue: Number(data.loan_status?.overdue || 0),
      closed: Number(data.loan_status?.closed || 0),
    };

    dashboard.active_loans_amount = Number(
      data.active_loans_amount || 0
    );

    dashboard.total_donations_amount = Number(
      data.total_donations_amount || 0
    );

    dashboard.people = data.people
      ? {
          borrowers: Number(data.people.borrowers || 0),
          trustees: Number(data.people.trustees || 0),
          donors: Number(data.people.donors || 0),
        }
      : null;

    dashboard.by_community = Array.isArray(data.by_community)
      ? data.by_community.map(
          (item: any): CommunitySummary => ({
            community: String(item.community || ""),
            loans_count: Number(item.loans_count || 0),
            total_amount: Number(item.total_amount || 0),
          })
        )
      : [];

    dashboard.community = String(data.community || "");
    dashboard.borrowers_count = Number(data.borrowers_count || 0);
    dashboard.my_donations_amount = Number(
      data.my_donations_amount || 0
    );

    if (results[1]) {
      const rows = Array.isArray(results[1].data)
        ? results[1].data
        : [];

      summarizeOpenLoans(rows);
    } else {
      openLoansCount.value =
        dashboard.loan_status.active +
        dashboard.loan_status.overdue;

      openLoansAmount.value =
        dashboard.active_loans_amount;
    }
  } catch (requestError: any) {
    errorMessage.value =
      requestError?.response?.data?.detail ||
      t("dashboard.messages.loadError");
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
  border: 1px solid rgba(229, 231, 235, 0.9);
  border-radius: 1rem;
  background: white;
  padding: 1.25rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.dashboard-card-button {
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.dashboard-card-button:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 122, 255, 0.25);
  box-shadow:
    0 8px 18px -10px rgba(0, 0, 0, 0.2),
    0 2px 6px rgba(0, 0, 0, 0.05);
}

.dashboard-card:disabled {
  cursor: default;
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
  font-weight: 600;
}

.dashboard-value {
  margin-top: 0.25rem;
  color: var(--color-ink);
  font-size: 1.875rem;
  line-height: 2.25rem;
  font-weight: 700;
}

.dashboard-value-money {
  white-space: nowrap;
  direction: ltr;
  font-size: clamp(1.05rem, 4.5vw, 1.35rem);
  line-height: 1.8rem;
}

.dashboard-hint {
  margin-top: 0.75rem;
  color: var(--color-muted);
  font-size: 0.75rem;
}


@media (min-width: 640px) {
  .dashboard-card {
    padding: 1.5rem;
  }

  .dashboard-value-money {
    font-size: 1.5rem;
    line-height: 2rem;
  }
}
</style>
