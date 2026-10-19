<template>
  <AppLayout
    :title="t('dashboard.title')"
    :show-language-toggle="true"
    max-width="full"
  >
    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="index in 4"
        :key="index"
        class="h-32 animate-pulse rounded-2xl border border-line bg-white"
      ></div>
    </div>

    <div
      v-else-if="errorMessage"
      class="rounded-2xl border border-red-200 bg-white p-6 text-center"
      role="alert"
    >
      <p class="text-sm text-red-700">{{ errorMessage }}</p>
      <button
        type="button"
        class="mt-4 cursor-pointer rounded-xl bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-deep"
        @click="loadDashboard"
      >
        {{ text("נסו שוב", "Try again", "Reintentar") }}
      </button>
    </div>

    <div v-else class="space-y-5 sm:space-y-6">
      <!-- 1. Headline numbers -->
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <component
          :is="tile.to ? 'button' : 'div'"
          v-for="tile in tiles"
          :key="tile.key"
          type="button"
          class="rounded-2xl border bg-white p-5 text-start shadow-sm transition"
          :class="[
            tile.tone === 'problem' && tile.value !== '0'
              ? 'border-red-200'
              : 'border-line',
            tile.to ? 'cursor-pointer hover:-translate-y-0.5 hover:shadow-md focus-visible:ring-2 focus-visible:ring-brand/40' : '',
          ]"
          @click="tile.to && router.push(tile.to)"
        >
          <div class="flex items-center gap-2">
            <span
              class="flex h-8 w-8 items-center justify-center rounded-lg"
              :class="toneClass(tile.tone)"
              aria-hidden="true"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons[tile.icon]" />
              </svg>
            </span>
            <p class="text-sm font-medium text-muted">{{ tile.label }}</p>
          </div>
          <p dir="ltr" class="mt-3 text-[1.75rem] font-bold leading-tight text-ink" :class="isRTL ? 'text-right' : 'text-left'">
            {{ tile.value }}
          </p>
          <p v-if="tile.hint" class="mt-1 text-xs" :class="tile.tone === 'problem' && tile.value !== '0' ? 'font-medium text-red-700' : 'text-muted'">
            {{ tile.hint }}
          </p>
        </component>
      </section>

      <!-- 2. Status split + how much was repaid -->
      <section class="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <article v-if="!auth.isBorrower.value" class="chart-card">
          <header class="chart-header">
            <h2 class="chart-title">{{ text("מצב ההלוואות", "Loan status", "Estado de los préstamos") }}</h2>
            <p class="chart-subtitle">
              {{ text("לחיצה על חלק פותחת את רשימת ההלוואות שלו", "Click a slice to open those loans", "Haz clic en una parte para ver esos préstamos") }}
            </p>
          </header>
          <DonutChart
            :segments="statusSegments"
            :center-label="text('הלוואות', 'loans', 'préstamos')"
            :aria-label="text('מצב ההלוואות', 'Loan status', 'Estado de los préstamos')"
            @select="openStatus"
          />
        </article>

        <article class="chart-card" :class="auth.isBorrower.value ? 'lg:col-span-2' : ''">
          <header class="chart-header">
            <h2 class="chart-title">
              {{ auth.isBorrower.value
                ? text("ההחזר שלי", "My repayment", "Mi devolución")
                : text("כמה כבר הוחזר", "How much has been repaid", "Cuánto se ha devuelto") }}
            </h2>
            <p class="chart-subtitle">
              {{ text("בהלוואות הפתוחות", "Across open loans", "En los préstamos abiertos") }}
            </p>
          </header>

          <div class="flex items-baseline justify-between gap-3">
            <p dir="ltr" class="text-4xl font-bold text-ink">{{ repaidPercent }}%</p>
            <p class="text-sm text-muted">{{ text("הוחזר", "repaid", "devuelto") }}</p>
          </div>

          <div
            class="mt-4 flex h-4 w-full overflow-hidden rounded-full bg-canvas-deep"
            role="img"
            :aria-label="`${text('הוחזר', 'Repaid', 'Devuelto')} ${money(data.repayment.paid)}, ${text('נותר', 'remaining', 'pendiente')} ${money(data.repayment.remaining)}`"
          >
            <div
              class="h-full rounded-full"
              :style="{ width: `${repaidPercent}%`, backgroundColor: COLORS.paid }"
            ></div>
          </div>

          <dl class="mt-5 grid grid-cols-2 gap-3">
            <div class="rounded-xl bg-canvas p-3">
              <dt class="flex items-center gap-2 text-xs text-muted">
                <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: COLORS.paid }"></span>
                {{ text("הוחזר", "Repaid", "Devuelto") }}
              </dt>
              <dd dir="ltr" class="mt-1 text-lg font-bold text-ink" :class="isRTL ? 'text-right' : 'text-left'">{{ money(data.repayment.paid) }}</dd>
            </div>
            <div class="rounded-xl bg-canvas p-3">
              <dt class="flex items-center gap-2 text-xs text-muted">
                <span class="h-2.5 w-2.5 rounded-full bg-canvas-deep ring-1 ring-line-strong"></span>
                {{ text("יתרה לתשלום", "Still owed", "Pendiente") }}
              </dt>
              <dd dir="ltr" class="mt-1 text-lg font-bold text-ink" :class="isRTL ? 'text-right' : 'text-left'">{{ money(data.repayment.remaining) }}</dd>
            </div>
          </dl>

          <p
            v-if="data.repayment.missing > 0"
            class="mt-3 flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800"
          >
            <svg class="mt-0.5 h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icons.alert" />
            </svg>
            <span>
              {{ text("תשלומים שלא נפרעו (צ'ק חזר / הוראת קבע שנכשלה):", "Unpaid payments (bounced check / failed standing order):", "Pagos no cobrados:") }}
              <strong dir="ltr">{{ money(data.repayment.missing) }}</strong>
            </span>
          </p>
        </article>
      </section>

      <!-- 3. What comes in next + where the money is -->
      <section class="grid grid-cols-1 gap-5" :class="showCommunities ? 'lg:grid-cols-2' : ''">
        <article class="chart-card">
          <header class="chart-header">
            <h2 class="chart-title">
              {{ auth.isBorrower.value
                ? text("התשלומים הקרובים שלי", "My upcoming payments", "Mis próximos pagos")
                : text("גבייה צפויה בחודשים הקרובים", "Expected collections, next months", "Cobros previstos") }}
            </h2>
            <p class="chart-subtitle">{{ text("סכום התשלומים לפי חודש", "Total payments due per month", "Total de pagos por mes") }}</p>
          </header>
          <BarChart
            :items="upcomingBars"
            :color="COLORS.money"
            :format-value="money"
            :format-short="moneyShort"
            :aria-label="text('גבייה צפויה לפי חודש', 'Expected collections per month', 'Cobros previstos por mes')"
          />
        </article>

        <article v-if="showCommunities" class="chart-card">
          <header class="chart-header">
            <h2 class="chart-title">{{ text("יתרה פתוחה לפי קהילה", "Open balance by community", "Saldo abierto por comunidad") }}</h2>
            <p class="chart-subtitle">{{ text("כמה עוד צריך לחזור מכל קהילה", "What is still owed in each community", "Lo que falta devolver en cada comunidad") }}</p>
          </header>
          <BarChart
            orientation="horizontal"
            :items="communityBars"
            :color="COLORS.money"
            :format-value="money"
            :aria-label="text('יתרה פתוחה לפי קהילה', 'Open balance by community', 'Saldo abierto por comunidad')"
          />
        </article>
      </section>

      <!-- 4. Donations (admin) -->
      <section v-if="auth.isAdmin.value && donationBars.length">
        <article class="chart-card">
          <header class="chart-header flex flex-wrap items-end justify-between gap-2">
            <div>
              <h2 class="chart-title">{{ text("תרומות ב-12 החודשים האחרונים", "Donations, last 12 months", "Donaciones, últimos 12 meses") }}</h2>
              <p class="chart-subtitle">{{ text("סכום התרומות שנרשמו בכל חודש", "Total donations recorded each month", "Total de donaciones por mes") }}</p>
            </div>
            <button
              type="button"
              class="cursor-pointer text-sm font-semibold text-brand hover:underline"
              @click="router.push('/donations')"
            >
              {{ text("לכל התרומות", "All donations", "Todas las donaciones") }}
            </button>
          </header>
          <BarChart
            :items="donationBars"
            :color="COLORS.donations"
            :format-value="dollars"
            :format-short="dollarsShort"
            :aria-label="text('תרומות לפי חודש', 'Donations per month', 'Donaciones por mes')"
          />
        </article>
      </section>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import AppLayout from "../components/AppLayout.vue";
import BarChart, { type BarItem } from "../components/charts/BarChart.vue";
import DonutChart, { type DonutSegment } from "../components/charts/DonutChart.vue";
import { useAuth } from "../composables/useAuth";
import { useLocale } from "../composables/useLocale";
import api from "../services/api";

type MonthRow = { month: string; amount: number; count: number };

const router = useRouter();
const auth = useAuth();
const { t, locale, isRTL } = useLocale();

// Validated chart colors (status colors carry a text label beside them).
const COLORS = {
  active: "#2a78d6",
  problem: "#d03b3b",
  closed: "#0ca30c",
  paid: "#2a78d6",
  money: "#2a78d6",
  donations: "#4a3aa7",
};

const icons: Record<string, string> = {
  loans: "M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8",
  alert: "M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z",
  wallet: "M3 7h18v12H3zM16 13h2M3 7l2-3h12l2 3",
  donation: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8V6m0 12v-2",
  calendar: "M8 3v3m8-3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z",
  people: "M17 20v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M10 10a4 4 0 1 0 0-8 4 4 0 0 0 0 8M21 20v-2a4 4 0 0 0-3-3.87M16 2.13a4 4 0 0 1 0 7.75",
};

const loading = ref(true);
const errorMessage = ref<string | null>(null);

const data = reactive({
  loan_status: { active: 0, overdue: 0, closed: 0 },
  repayment: { paid: 0, remaining: 0, missing: 0 },
  upcoming_by_month: [] as MonthRow[],
  balance_by_community: [] as { community: string; remaining_amount: number; loans_count: number }[],
  donations_by_month: [] as MonthRow[],
  total_donations_amount: 0,
  borrowers_count: 0,
  people: null as null | { borrowers: number; trustees: number; donors: number },
  next_payment: null as null | { due_date: string; amount: number },
});

function text(he: string, en: string, es: string): string {
  if (locale.value === "he") return he;
  if (locale.value === "es") return es;
  return en;
}

const numberLocale = computed(() =>
  locale.value === "he" ? "he-IL" : locale.value === "es" ? "es-ES" : "en-US"
);

function money(value: number): string {
  return `₪ ${new Intl.NumberFormat(numberLocale.value, { maximumFractionDigits: 0 }).format(value || 0)}`;
}

function moneyShort(value: number): string {
  return `₪${new Intl.NumberFormat(numberLocale.value, { notation: "compact", maximumFractionDigits: 1 }).format(value || 0)}`;
}

function dollars(value: number): string {
  return `$ ${new Intl.NumberFormat(numberLocale.value, { maximumFractionDigits: 0 }).format(value || 0)}`;
}

function dollarsShort(value: number): string {
  return `$${new Intl.NumberFormat(numberLocale.value, { notation: "compact", maximumFractionDigits: 1 }).format(value || 0)}`;
}

function monthLabel(key: string): string {
  const [year, month] = key.split("-").map(Number);
  const date = new Date(year, month - 1, 1);
  const sameYear = year === new Date().getFullYear();
  return new Intl.DateTimeFormat(numberLocale.value, {
    month: "short",
    ...(sameYear ? {} : { year: "2-digit" }),
  }).format(date);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(numberLocale.value, { day: "numeric", month: "short" }).format(
    new Date(`${value}T00:00:00`)
  );
}

function toneClass(tone: string): string {
  return {
    active: "bg-brand/10 text-brand",
    problem: "bg-red-50 text-red-600",
    money: "bg-sky/10 text-sky-700",
    donation: "bg-violet/10 text-violet",
    neutral: "bg-canvas-deep text-ink-soft",
  }[tone] || "bg-canvas-deep text-ink-soft";
}

const openLoans = computed(() => data.loan_status.active + data.loan_status.overdue);

const repaidPercent = computed(() => {
  const total = data.repayment.paid + data.repayment.remaining;
  return total > 0 ? Math.round((data.repayment.paid / total) * 100) : 0;
});

type Tile = {
  key: string;
  label: string;
  value: string;
  hint?: string;
  icon: string;
  tone: string;
  to?: string;
};

const tiles = computed<Tile[]>(() => {
  const problemTile: Tile = {
    key: "problem",
    label: text("הלוואות בעייתיות", "Problem loans", "Préstamos con problemas"),
    value: String(data.loan_status.overdue),
    hint:
      data.loan_status.overdue > 0
        ? text(`חסרים ${money(data.repayment.missing)} – לחצו לפרטים`, `${money(data.repayment.missing)} missing – click for details`, `Faltan ${money(data.repayment.missing)}`)
        : text("אין תשלומים חסרים", "No missing payments", "Sin pagos pendientes"),
    icon: "alert",
    tone: "problem",
    to: "/loans?status=OVERDUE",
  };

  const balanceTile: Tile = {
    key: "balance",
    label: text("יתרה פתוחה", "Open balance", "Saldo abierto"),
    value: money(data.repayment.remaining),
    hint: text("כמה עוד צריך לחזור", "Still to be repaid", "Pendiente de devolver"),
    icon: "wallet",
    tone: "money",
  };

  if (auth.isBorrower.value) {
    return [
      balanceTile,
      {
        key: "next",
        label: text("התשלום הבא", "Next payment", "Próximo pago"),
        value: data.next_payment ? money(data.next_payment.amount) : "—",
        hint: data.next_payment ? formatDate(data.next_payment.due_date) : text("אין תשלומים קרובים", "No upcoming payments", "Sin pagos próximos"),
        icon: "calendar",
        tone: "active",
        to: "/loans",
      },
      { ...problemTile, label: text("תשלומים שלא נפרעו", "Unpaid payments", "Pagos no cobrados"), to: "/loans" },
      {
        key: "loans",
        label: text("ההלוואות שלי", "My loans", "Mis préstamos"),
        value: String(openLoans.value),
        hint: text("לצפייה בלוח התשלומים", "View payment schedule", "Ver calendario de pagos"),
        icon: "loans",
        tone: "neutral",
        to: "/loans",
      },
    ];
  }

  const list: Tile[] = [
    {
      key: "active",
      label: text("הלוואות פעילות", "Active loans", "Préstamos activos"),
      value: String(openLoans.value),
      hint: text("לרשימת ההלוואות", "Open the loans list", "Ver préstamos"),
      icon: "loans",
      tone: "active",
      to: "/loans",
    },
    problemTile,
    balanceTile,
  ];

  if (auth.isAdmin.value) {
    list.push({
      key: "donations",
      label: text("סך התרומות", "Total donations", "Total de donaciones"),
      value: dollars(data.total_donations_amount),
      hint: text("לרשימת התרומות", "Open donations", "Ver donaciones"),
      icon: "donation",
      tone: "donation",
      to: "/donations",
    });
  } else {
    list.push({
      key: "borrowers",
      label: text("לווים בקהילה", "Borrowers in community", "Prestatarios"),
      value: String(data.borrowers_count),
      hint: text("לרשימת הלווים", "Open borrowers", "Ver prestatarios"),
      icon: "people",
      tone: "neutral",
      to: "/borrowers",
    });
  }

  return list;
});

const statusSegments = computed<DonutSegment[]>(() => [
  { key: "ACTIVE", label: text("פעילות", "Active", "Activos"), value: data.loan_status.active, color: COLORS.active },
  { key: "OVERDUE", label: text("בעייתיות", "Problem", "Con problemas"), value: data.loan_status.overdue, color: COLORS.problem },
  { key: "CLOSED", label: text("הסתיימו", "Completed", "Finalizados"), value: data.loan_status.closed, color: COLORS.closed },
]);

function openStatus(key: string): void {
  router.push(key === "CLOSED" ? "/archive" : `/loans?status=${key}`);
}

const upcomingBars = computed<BarItem[]>(() =>
  data.upcoming_by_month.map((row) => ({
    key: row.month,
    label: monthLabel(row.month),
    value: row.amount,
    detail: text(`${row.count} תשלומים`, `${row.count} payments`, `${row.count} pagos`),
  }))
);

const showCommunities = computed(() => auth.isAdmin.value && data.balance_by_community.length > 1);

const communityBars = computed<BarItem[]>(() =>
  data.balance_by_community.map((row) => ({
    key: row.community,
    label: row.community,
    value: row.remaining_amount,
    detail: text(`${row.loans_count} הלוואות פתוחות`, `${row.loans_count} open loans`, `${row.loans_count} préstamos abiertos`),
  }))
);

const donationBars = computed<BarItem[]>(() =>
  data.donations_by_month.map((row) => ({
    key: row.month,
    label: monthLabel(row.month),
    value: row.amount,
    detail: text(`${row.count} תרומות`, `${row.count} donations`, `${row.count} donaciones`),
  }))
);

function toMonthRows(rows: any): MonthRow[] {
  return Array.isArray(rows)
    ? rows.map((row) => ({ month: String(row.month), amount: Number(row.amount || 0), count: Number(row.count || 0) }))
    : [];
}

async function loadDashboard(): Promise<void> {
  loading.value = true;
  errorMessage.value = null;

  try {
    const response = await api.get("/dashboard/overview/");
    const d = response.data || {};

    data.loan_status = {
      active: Number(d.loan_status?.active || 0),
      overdue: Number(d.loan_status?.overdue || 0),
      closed: Number(d.loan_status?.closed || 0),
    };
    data.repayment = {
      paid: Number(d.repayment?.paid || 0),
      remaining: Number(d.repayment?.remaining || 0),
      missing: Number(d.repayment?.missing || 0),
    };
    data.upcoming_by_month = toMonthRows(d.upcoming_by_month);
    data.donations_by_month = toMonthRows(d.donations_by_month);
    data.balance_by_community = Array.isArray(d.balance_by_community)
      ? d.balance_by_community.map((row: any) => ({
          community: String(row.community || "—"),
          remaining_amount: Number(row.remaining_amount || 0),
          loans_count: Number(row.loans_count || 0),
        }))
      : [];
    data.total_donations_amount = Number(d.total_donations_amount || 0);
    data.borrowers_count = Number(d.borrowers_count || 0);
    data.people = d.people || null;
    data.next_payment = d.next_payment
      ? { due_date: String(d.next_payment.due_date), amount: Number(d.next_payment.amount || 0) }
      : null;
  } catch (error: any) {
    errorMessage.value = t("dashboard.messages.loadError");
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>

<style scoped>
.chart-card {
  border: 1px solid var(--color-line);
  border-radius: 1rem;
  background: var(--color-surface);
  padding: 1.25rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

@media (min-width: 640px) {
  .chart-card {
    padding: 1.5rem;
  }
}

.chart-header {
  margin-bottom: 1.25rem;
}

.chart-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-ink);
}

.chart-subtitle {
  margin-top: 0.125rem;
  font-size: 0.8125rem;
  color: var(--color-muted);
}
</style>
