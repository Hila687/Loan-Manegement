<template>
  <AppLayout
    :title="title"
    :subtitle="subtitle"
    :show-language-toggle="true"
    max-width="full"
  >
    <div class="space-y-5 sm:space-y-6">
      <!-- Report filters -->
      <section
        class="rounded-2xl border border-[#E5E5EA] bg-white p-4 shadow-sm sm:p-5"
      >
        <div
          class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4"
        >
          <label
            class="flex flex-col gap-1.5"
          >
            <span
              class="text-sm font-medium text-[#374151]"
            >
              {{ trusteeLabel }}
            </span>

            <select
              v-model="filters.trustee"
              class="h-11 rounded-lg border border-[#E5E5EA] bg-white px-3 text-sm outline-none transition focus:border-[#007AFF] focus:ring-2 focus:ring-[#007AFF]/20"
            >
              <option value="">
                {{ allLabel }}
              </option>

              <option
                v-for="trustee in trustees"
                :key="trustee.id"
                :value="trustee.id"
              >
                {{ trustee.label }}
              </option>
            </select>
          </label>

          <label
            class="flex flex-col gap-1.5"
          >
            <span
              class="text-sm font-medium text-[#374151]"
            >
              {{ borrowerLabel }}
            </span>

            <select
              v-model="filters.borrower"
              class="h-11 rounded-lg border border-[#E5E5EA] bg-white px-3 text-sm outline-none transition focus:border-[#007AFF] focus:ring-2 focus:ring-[#007AFF]/20"
            >
              <option value="">
                {{ allLabel }}
              </option>

              <option
                v-for="borrower in borrowers"
                :key="borrower.id"
                :value="borrower.id"
              >
                {{ borrower.label }}
              </option>
            </select>
          </label>

          <label
            class="flex flex-col gap-1.5"
          >
            <span
              class="text-sm font-medium text-[#374151]"
            >
              {{ fromDateLabel }}
            </span>

            <input
              v-model="filters.start_date"
              type="date"
              class="h-11 rounded-lg border border-[#E5E5EA] bg-white px-3 text-sm outline-none transition focus:border-[#007AFF] focus:ring-2 focus:ring-[#007AFF]/20"
            />
          </label>

          <label
            class="flex flex-col gap-1.5"
          >
            <span
              class="text-sm font-medium text-[#374151]"
            >
              {{ toDateLabel }}
            </span>

            <input
              v-model="filters.end_date"
              type="date"
              class="h-11 rounded-lg border border-[#E5E5EA] bg-white px-3 text-sm outline-none transition focus:border-[#007AFF] focus:ring-2 focus:ring-[#007AFF]/20"
            />
          </label>
        </div>

        <div
          class="mt-4 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end"
        >
          <button
            type="button"
            :disabled="loading"
            class="h-11 rounded-xl border border-[#E5E5EA] bg-white px-5 text-sm font-semibold text-[#374151] transition hover:bg-gray-50 disabled:opacity-50"
            @click="clearFilters"
          >
            {{ clearLabel }}
          </button>

          <button
            type="button"
            :disabled="loading"
            class="h-11 rounded-xl bg-[#007AFF] px-5 text-sm font-semibold text-white shadow-lg shadow-[#007AFF]/20 transition hover:bg-[#0051D5] disabled:bg-gray-400"
            @click="loadReport()"
          >
            {{
              loading
                ? loadingLabel
                : generateLabel
            }}
          </button>
        </div>
      </section>

      <!-- Error -->
      <div
        v-if="errorMessage"
        class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
      >
        {{ errorMessage }}
      </div>

      <!-- Summary -->
      <section
        v-if="summaryCards.length"
        class="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-6"
      >
        <article
          v-for="card in summaryCards"
          :key="card.key"
          class="rounded-2xl border border-[#E5E5EA] bg-white p-4 shadow-sm"
        >
          <p
            class="text-xs font-medium text-[#6B7280]"
          >
            {{ card.label }}
          </p>

          <p
            class="mt-2 break-words text-lg font-bold text-[#111827]"
          >
            {{ card.value }}
          </p>
        </article>
      </section>

      <!-- Loading -->
      <div
        v-if="loading"
        class="flex flex-col items-center justify-center rounded-2xl border border-[#E5E5EA] bg-white py-16"
      >
        <div
          class="h-9 w-9 animate-spin rounded-full border-4 border-[#007AFF] border-t-transparent"
        ></div>

        <p
          class="mt-4 text-sm text-[#6B7280]"
        >
          {{ loadingLabel }}
        </p>
      </div>

      <!-- Empty -->
      <div
        v-else-if="
          loaded &&
          rows.length === 0
        "
        class="rounded-2xl border border-[#E5E5EA] bg-white px-6 py-14 text-center"
      >
        <h2
          class="text-base font-semibold text-[#111827]"
        >
          {{ emptyTitle }}
        </h2>

        <p
          class="mt-1 text-sm text-[#6B7280]"
        >
          {{ emptyDescription }}
        </p>
      </div>

      <!-- Desktop table -->
      <section
        v-else-if="rows.length"
        class="hidden overflow-hidden rounded-2xl border border-[#E5E5EA] bg-white shadow-sm md:block"
      >
        <div
          class="overflow-x-auto"
        >
          <table
            class="min-w-full divide-y divide-[#E5E5EA] text-sm"
          >
            <thead
              class="bg-[#F7F8FC]"
            >
              <tr>
                <th
                  class="px-4 py-3 text-start font-semibold text-[#374151]"
                >
                  {{ borrowerLabel }}
                </th>

                <th
                  class="px-4 py-3 text-start font-semibold text-[#374151]"
                >
                  {{ trusteeLabel }}
                </th>

                <th
                  class="px-4 py-3 text-start font-semibold text-[#374151]"
                >
                  {{ amountLabel }}
                </th>

                <th
                  class="px-4 py-3 text-start font-semibold text-[#374151]"
                >
                  {{ statusLabelText }}
                </th>

                <th
                  class="px-4 py-3 text-start font-semibold text-[#374151]"
                >
                  {{ startDateLabel }}
                </th>
              </tr>
            </thead>

            <tbody
              class="divide-y divide-[#E5E5EA]"
            >
              <tr
                v-for="(row, index) in rows"
                :key="rowKey(row, index)"
                class="hover:bg-[#F7F8FC]/60"
              >
                <td
                  class="px-4 py-3 text-[#111827]"
                >
                  {{ rowBorrower(row) }}
                </td>

                <td
                  class="px-4 py-3 text-[#111827]"
                >
                  {{ rowTrustee(row) }}
                </td>

                <td
                  class="px-4 py-3 font-medium text-[#111827]"
                >
                  {{
                    formatCurrency(
                      rowAmount(row)
                    )
                  }}
                </td>

                <td
                  class="px-4 py-3"
                >
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                    :class="
                      statusClass(
                        rowStatus(row)
                      )
                    "
                  >
                    {{
                      statusLabel(
                        rowStatus(row)
                      )
                    }}
                  </span>
                </td>

                <td
                  class="px-4 py-3 text-[#111827]"
                >
                  {{
                    formatDate(
                      rowStartDate(row)
                    )
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Mobile cards -->
      <section
        v-if="rows.length"
        class="space-y-3 md:hidden"
      >
        <article
          v-for="(row, index) in rows"
          :key="rowKey(row, index)"
          class="rounded-2xl border border-[#E5E5EA] bg-white p-4 shadow-sm"
        >
          <div
            class="flex items-start justify-between gap-3"
          >
            <div
              class="min-w-0"
            >
              <h3
                class="truncate font-semibold text-[#111827]"
              >
                {{ rowBorrower(row) }}
              </h3>

              <p
                class="mt-1 truncate text-xs text-[#6B7280]"
              >
                {{ rowTrustee(row) }}
              </p>
            </div>

            <span
              class="flex-shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="
                statusClass(
                  rowStatus(row)
                )
              "
            >
              {{
                statusLabel(
                  rowStatus(row)
                )
              }}
            </span>
          </div>

          <div
            class="mt-4 grid grid-cols-2 gap-3"
          >
            <div>
              <p
                class="text-xs text-[#6B7280]"
              >
                {{ amountLabel }}
              </p>

              <p
                class="mt-1 text-sm font-semibold text-[#111827]"
              >
                {{
                  formatCurrency(
                    rowAmount(row)
                  )
                }}
              </p>
            </div>

            <div>
              <p
                class="text-xs text-[#6B7280]"
              >
                {{ startDateLabel }}
              </p>

              <p
                class="mt-1 text-sm text-[#111827]"
              >
                {{
                  formatDate(
                    rowStartDate(row)
                  )
                }}
              </p>
            </div>
          </div>
        </article>
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

import AppLayout
  from "../components/AppLayout.vue";

import api
  from "../services/api";

import {
  useLocale,
} from "../composables/useLocale";

type OptionItem = {
  id: string;
  label: string;
};

type ReportRow =
  Record<string, any>;

type ReportResponse =
  Record<string, any>;

const {
  locale,
} = useLocale();

const isHebrew =
  computed(
    () =>
      locale.value ===
      "he"
  );

const filters =
  reactive({
    trustee: "",
    borrower: "",
    start_date: "",
    end_date: "",
  });

const trustees =
  ref<OptionItem[]>([]);

const borrowers =
  ref<OptionItem[]>([]);

const report =
  ref<ReportResponse>({});

const loading =
  ref(false);

const loaded =
  ref(false);

const errorMessage =
  ref("");

const title =
  computed(() =>
    isHebrew.value
      ? "דוחות ניהוליים"
      : "Management Reports"
  );

const subtitle =
  computed(() =>
    isHebrew.value
      ? "סיכום הלוואות לפי לווה, נאמן וטווח תאריכים"
      : "Loan summaries by borrower, trustee, and date range"
  );

const trusteeLabel =
  computed(() =>
    isHebrew.value
      ? "נאמן"
      : "Trustee"
  );

const borrowerLabel =
  computed(() =>
    isHebrew.value
      ? "לווה"
      : "Borrower"
  );

const allLabel =
  computed(() =>
    isHebrew.value
      ? "הכל"
      : "All"
  );

const fromDateLabel =
  computed(() =>
    isHebrew.value
      ? "מתאריך"
      : "From date"
  );

const toDateLabel =
  computed(() =>
    isHebrew.value
      ? "עד תאריך"
      : "To date"
  );

const startDateLabel =
  computed(() =>
    isHebrew.value
      ? "תאריך התחלה"
      : "Start date"
  );

const amountLabel =
  computed(() =>
    isHebrew.value
      ? "סכום"
      : "Amount"
  );

const statusLabelText =
  computed(() =>
    isHebrew.value
      ? "סטטוס"
      : "Status"
  );

const clearLabel =
  computed(() =>
    isHebrew.value
      ? "ניקוי"
      : "Clear"
  );

const generateLabel =
  computed(() =>
    isHebrew.value
      ? "הפקת דוח"
      : "Generate report"
  );

const loadingLabel =
  computed(() =>
    isHebrew.value
      ? "טוען דוח..."
      : "Loading report..."
  );

const emptyTitle =
  computed(() =>
    isHebrew.value
      ? "אין נתונים להצגה"
      : "No report data"
  );

const emptyDescription =
  computed(() =>
    isHebrew.value
      ? "לא נמצאו הלוואות המתאימות למסננים שנבחרו."
      : "No loans match the selected filters."
  );

const rows =
  computed<ReportRow[]>(
    () => {
      const candidates = [
        report.value.loans,
        report.value.results,
        report.value.rows,
        report.value.data,
      ];

      for (
        const candidate
        of candidates
      ) {
        if (
          Array.isArray(
            candidate
          )
        ) {
          return candidate;
        }
      }

      return [];
    }
  );

const summarySource =
  computed<
    Record<string, any>
  >(() => {
    if (
      report.value.summary &&
      typeof report.value
        .summary ===
        "object"
    ) {
      return report.value
        .summary;
    }

    return report.value;
  });

const summaryCards =
  computed(() => {
    const source =
      summarySource.value;

    const definitions = [
      {
        key:
          "loans_count",

        aliases: [
          "loans_count",
          "total_loans",
          "count",
        ],

        label:
          isHebrew.value
            ? "מספר הלוואות"
            : "Loans",

        format:
          "number",
      },

      {
        key:
          "total_loan_amount",

        aliases: [
          "loans_amount",
          "total_loan_amount",
          "total_amount",
          "loan_amount",
        ],

        label:
          isHebrew.value
            ? "סכום הלוואות"
            : "Loan amount",

        format:
          "currency",
      },

      {
        key:
          "paid_amount",

        aliases: [
          "paid_amount",
          "total_paid",
        ],

        label:
          isHebrew.value
            ? "שולם"
            : "Paid",

        format:
          "currency",
      },

      {
        key:
          "outstanding_amount",

        aliases: [
          "outstanding_amount",
          "remaining_amount",
          "open_amount",
        ],

        label:
          isHebrew.value
            ? "יתרה פתוחה"
            : "Outstanding",

        format:
          "currency",
      },

      {
        key:
          "overdue_loans_count",

        aliases: [
          "overdue_loans_count",
          "overdue_count",
        ],

        label:
          isHebrew.value
            ? "הלוואות באיחור"
            : "Overdue loans",

        format:
          "number",
      },

      {
        key:
          "donations_total",

        aliases: [
          "donations_amount",
          "donations_total",
          "total_donations",
        ],

        label:
          isHebrew.value
            ? "סה״כ תרומות"
            : "Donations",

        format:
          "currency",
      },
    ];

    return definitions
      .map(
        (
          definition
        ) => {
          const alias =
            definition
              .aliases
              .find(
                (key) =>
                  source[key] !==
                    undefined &&
                  source[key] !==
                    null
              );

          if (!alias) {
            return null;
          }

          const rawValue =
            source[alias];

          const value =
            definition.format ===
            "currency"
              ? formatCurrency(
                  rawValue
                )
              : new Intl
                  .NumberFormat(
                    isHebrew.value
                      ? "he-IL"
                      : "en-US"
                  )
                  .format(
                    Number(
                      rawValue ||
                      0
                    )
                  );

          return {
            key:
              definition.key,

            label:
              definition.label,

            value,
          };
        }
      )
      .filter(
        (
          item
        ): item is {
          key: string;
          label: string;
          value: string;
        } =>
          item !== null
      );
  });

function normalizePersonName(
  item: any
): string {
  if (!item) {
    return "";
  }

  if (
    typeof item ===
    "string"
  ) {
    return item;
  }

  const user =
    item.user_details ||
    item.user ||
    {};

  const first =
    String(
      item.first_name ||
      user.first_name ||
      ""
    ).trim();

  const last =
    String(
      item.last_name ||
      user.last_name ||
      ""
    ).trim();

  const fullName =
    `${first} ${last}`.trim();

  return (
    fullName ||
    String(
      item.name ||
      user.username ||
      ""
    ).trim()
  );
}

function normalizeOption(
  item: any,
  type:
    | "trustee"
    | "borrower"
): OptionItem {
  const id =
    type === "trustee"
      ? item.trustee_id ||
        item.id
      : item.borrower_id ||
        item.id;

  const name =
    normalizePersonName(
      item
    );

  const fallback =
    type === "trustee"
      ? String(
          item.community ||
          ""
        ).trim()
      : String(
          item.id_number ||
          ""
        ).trim();

  return {
    id:
      String(
        id || ""
      ),

    label:
      name ||
      fallback ||
      "—",
  };
}

async function loadOptions():
  Promise<void> {
  const results =
    await Promise.allSettled(
      [
        api.get(
          "/trustees/"
        ),

        api.get(
          "/borrowers/"
        ),
      ]
    );

  const trusteeResult =
    results[0];

  const borrowerResult =
    results[1];

  if (
    trusteeResult.status ===
    "fulfilled"
  ) {
    const data =
      Array.isArray(
        trusteeResult.value
          .data
      )
        ? trusteeResult.value
            .data
        : [];

    trustees.value =
      data
        .map(
          (item: any) =>
            normalizeOption(
              item,
              "trustee"
            )
        )
        .filter(
          (
            item:
              OptionItem
          ) =>
            Boolean(
              item.id
            )
        );
  }

  if (
    borrowerResult.status ===
    "fulfilled"
  ) {
    const data =
      Array.isArray(
        borrowerResult.value
          .data
      )
        ? borrowerResult.value
            .data
        : [];

    borrowers.value =
      data
        .map(
          (item: any) =>
            normalizeOption(
              item,
              "borrower"
            )
        )
        .filter(
          (
            item:
              OptionItem
          ) =>
            Boolean(
              item.id
            )
        );
  }
}

async function loadReport():
  Promise<void> {
  if (
    loading.value
  ) {
    return;
  }

  if (
    filters.start_date &&
    filters.end_date &&
    filters.start_date >
      filters.end_date
  ) {
    errorMessage.value =
      isHebrew.value
        ? "תאריך ההתחלה לא יכול להיות מאוחר מתאריך הסיום."
        : "The start date cannot be after the end date.";

    return;
  }

  loading.value =
    true;

  errorMessage.value =
    "";

  try {
    const params:
      Record<
        string,
        string
      > = {};

    if (
      filters.trustee
    ) {
      params.trustee_id =
        filters.trustee;
    }

    if (
      filters.borrower
    ) {
      params.borrower_id =
        filters.borrower;
    }

    if (
      filters.start_date
    ) {
      params.start_date =
        filters.start_date;
    }

    if (
      filters.end_date
    ) {
      params.end_date =
        filters.end_date;
    }

    const response =
      await api.get(
        "/reports/summary/",
        {
          params,
        }
      );

    report.value =
      response.data &&
      typeof response.data ===
        "object"
        ? response.data
        : {};

    loaded.value =
      true;
  } catch (
    requestError: any
  ) {
    report.value =
      {};

    loaded.value =
      true;

    errorMessage.value =
      requestError
        ?.response
        ?.data
        ?.detail ||
      (
        isHebrew.value
          ? "טעינת הדוח נכשלה."
          : "Failed to load the report."
      );
  } finally {
    loading.value =
      false;
  }
}

function clearFilters():
  void {
  filters.trustee =
    "";

  filters.borrower =
    "";

  filters.start_date =
    "";

  filters.end_date =
    "";

  errorMessage.value =
    "";

  loadReport();
}

function rowKey(
  row: ReportRow,
  index: number
): string {
  return String(
    row.loan_id ||
    row.id ||
    `${index}`
  );
}

function rowBorrower(
  row: ReportRow
): string {
  return (
    normalizePersonName(
      row.borrower
    ) ||
    String(
      row.borrower_name ||
      "—"
    )
  );
}

function rowTrustee(
  row: ReportRow
): string {
  return (
    normalizePersonName(
      row.trustee
    ) ||
    String(
      row.trustee_name ||
      row.community ||
      "—"
    )
  );
}

function rowAmount(
  row: ReportRow
): number | string {
  return (
    row.amount ??
    row.loan_amount ??
    0
  );
}

function rowStatus(
  row: ReportRow
): string {
  return String(
    row.status ||
    "ACTIVE"
  ).toUpperCase();
}

function rowStartDate(
  row: ReportRow
): string {
  return String(
    row.start_date ||
    row.created_at ||
    ""
  );
}

function formatCurrency(
  value: any
): string {
  return new Intl
    .NumberFormat(
      isHebrew.value
        ? "he-IL"
        : "en-US",
      {
        style:
          "currency",

        currency:
          "ILS",

        maximumFractionDigits:
          2,
      }
    )
    .format(
      Number(
        value || 0
      )
    );
}

function formatDate(
  value: string
): string {
  if (!value) {
    return "—";
  }

  const normalized =
    value.length === 10
      ? `${value}T00:00:00`
      : value;

  const date =
    new Date(
      normalized
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value;
  }

  return date
    .toLocaleDateString(
      isHebrew.value
        ? "he-IL"
        : "en-US"
    );
}

function statusLabel(
  status: string
): string {
  if (
    status ===
    "OVERDUE"
  ) {
    return isHebrew.value
      ? "באיחור"
      : "Overdue";
  }

  if (
    status ===
    "CLOSED"
  ) {
    return isHebrew.value
      ? "סגורה"
      : "Closed";
  }

  return isHebrew.value
    ? "פעילה"
    : "Active";
}

function statusClass(
  status: string
): string {
  if (
    status ===
    "OVERDUE"
  ) {
    return (
      "bg-[#FF3B30]/10 " +
      "text-[#FF3B30]"
    );
  }

  if (
    status ===
    "CLOSED"
  ) {
    return (
      "bg-[#34C759]/10 " +
      "text-[#248A3D]"
    );
  }

  return (
    "bg-[#007AFF]/10 " +
    "text-[#007AFF]"
  );
}

onMounted(
  async () => {
    await loadOptions();
    await loadReport();
  }
);
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(
      360deg
    );
  }
}

.animate-spin {
  animation:
    spin
    1s
    linear
    infinite;
}
</style>