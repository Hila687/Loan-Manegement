<template>
  <div
    class="space-y-6 rounded-xl border border-line bg-white p-4 shadow-sm sm:p-5 lg:p-6"
  >
    <TabsSection
      @tab-change="
        handleTabChange
      "
    >
      <template #details>
        <!-- Borrower information -->
        <section>
          <BorrowerInfoSection
            :borrower="
              loan.borrower
            "
          />
        </section>

        <div
          class="my-6 border-t border-line"
        ></div>

        <!-- Loan information -->
        <section>
          <div class="mb-4">
            <h2 class="text-lg font-semibold text-ink">
              {{ t("loanDetails.loanInfo") }}
            </h2>
          </div>

          <div
            class="grid grid-cols-1 gap-3 text-sm text-ink-soft sm:grid-cols-2"
          >
            <div
              class="detail-item"
            >
              <span
                class="detail-label"
              >
                {{
                  t(
                    "loanDetails.type"
                  )
                }}
              </span>

              <span>
                {{
                  loanTypeLabel
                }}
              </span>
            </div>

            <div
              class="detail-item"
            >
              <span
                class="detail-label"
              >
                {{
                  t(
                    "loanDetails.amount"
                  )
                }}
              </span>

              <span>
                {{
                  formatCurrency(
                    loan.amount
                  )
                }}
              </span>
            </div>

            <div
              class="detail-item"
            >
              <span
                class="detail-label"
              >
                {{
                  t(
                    "loanDetails.startDate"
                  )
                }}
              </span>

              <span>
                {{
                  formatDate(
                    loan.startDate
                  )
                }}
              </span>
            </div>

            <div
              class="detail-item"
            >
              <span
                class="detail-label"
              >
                {{
                  t(
                    "loanDetails.createdAt"
                  )
                }}
              </span>

              <span>
                {{
                  formatDate(
                    loan.createdAt
                  )
                }}
              </span>
            </div>

            <!-- Checks -->
            <template
              v-if="
                loan.type ===
                  'checks' &&
                checksDetails
              "
            >
              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.numPayments"
                    )
                  }}
                </span>

                <span>
                  {{
                    checksDetails.numPayments
                  }}
                </span>
              </div>

              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.predefinedSchedule"
                    )
                  }}
                </span>

                <span>
                  {{
                    checksDetails
                      .predefinedSchedule
                      ? t(
                          "loanDetails.yes"
                        )
                      : t(
                          "loanDetails.no"
                        )
                  }}
                </span>
              </div>

              <div
                class="detail-item sm:col-span-2"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.checkDetails"
                    )
                  }}
                </span>

                <span>
                  {{
                    checksDetails
                      .checkDetails ||
                    "—"
                  }}
                </span>
              </div>
            </template>

            <!-- Standing order -->
            <template
              v-if="
                loan.type ===
                  'standing_order' &&
                standingDetails
              "
            >
              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.numPayments"
                    )
                  }}
                </span>

                <span>
                  {{
                    standingDetails
                      .numPayments
                  }}
                </span>
              </div>

              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.monthlyAmount"
                    )
                  }}
                </span>

                <span>
                  {{
                    formatCurrency(
                      standingDetails
                        .monthlyAmount
                    )
                  }}
                </span>
              </div>

              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.chargeDay"
                    )
                  }}
                </span>

                <span>
                  {{
                    standingDetails
                      .chargeDay
                  }}
                </span>
              </div>

              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.stopDate"
                    )
                  }}
                </span>

                <span>
                  {{
                    standingDetails
                      .stopDate
                      ? formatDate(
                          standingDetails
                            .stopDate
                        )
                      : "—"
                  }}
                </span>
              </div>
            </template>
          </div>
        </section>

        <div
          class="my-6 border-t border-line"
        ></div>

        <!-- Signed form -->
        <section>
          <h2
            class="text-lg font-semibold text-ink"
          >
            {{
              signedFormTitle
            }}
          </h2>

          <div
            v-if="
              loan.formFileUrl
            "
            class="mt-3 flex flex-col gap-3 rounded-xl border border-brand/20 bg-brand/5 p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div
              class="flex items-start gap-3"
            >
              <div
                class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-white text-brand shadow-sm"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M7 3h7l5 5v13H7a2 2 0 01-2-2V5a2 2 0 012-2zm7 0v6h6"
                  />
                </svg>
              </div>

              <div>
                <p
                  class="text-sm font-semibold text-ink"
                >
                  {{
                    signedFormAvailableLabel
                  }}
                </p>

              </div>
            </div>

            <a
              :href="
                loan.formFileUrl
              "
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex h-10 items-center justify-center rounded-lg bg-brand px-4 text-sm font-semibold text-white transition hover:bg-brand-deep"
            >
              {{
                signedFormOpenLabel
              }}
            </a>
          </div>

          <p
            v-else
            class="mt-3 rounded-xl border border-line bg-canvas p-4 text-sm text-muted"
          >
            {{
              signedFormMissingLabel
            }}
          </p>
        </section>

        <section
          v-if="loan.type === 'standing_order'"
          class="mt-4"
        >
          <h2 class="text-lg font-semibold text-ink">
            {{ standingOrderFormTitle }}
          </h2>

          <div
            v-if="loan.standingOrderFormFileUrl"
            class="mt-3 flex flex-col gap-3 rounded-xl border border-violet/20 bg-violet/5 p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div class="flex items-start gap-3">
              <div
                class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-white text-violet shadow-sm"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M7 3h7l5 5v13H7a2 2 0 01-2-2V5a2 2 0 012-2zm7 0v6h6"
                  />
                </svg>
              </div>

              <div>
                <p class="text-sm font-semibold text-ink">
                  {{ standingOrderFormAvailableLabel }}
                </p>

              </div>
            </div>

            <a
              :href="loan.standingOrderFormFileUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex h-10 items-center justify-center rounded-lg bg-violet px-4 text-sm font-semibold text-white transition hover:opacity-90"
            >
              {{ signedFormOpenLabel }}
            </a>
          </div>

          <p
            v-else
            class="mt-3 rounded-xl border border-line bg-canvas p-4 text-sm text-muted"
          >
            {{ standingOrderFormMissingLabel }}
          </p>
        </section>

        <template
          v-if="
            loan.trustee
          "
        >
          <div
            class="my-6 border-t border-line"
          ></div>

          <!-- Trustee information -->
          <section>
            <h2
              class="text-lg font-semibold text-ink"
            >
              {{
                t(
                  "loanDetails.trustee"
                )
              }}
            </h2>

            <div
              class="mt-3 grid grid-cols-1 gap-3 text-sm text-ink-soft sm:grid-cols-2"
            >
              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.name"
                    )
                  }}
                </span>

                <span>
                  {{
                    loan.trustee
                      .name ||
                    "—"
                  }}
                </span>
              </div>

              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.phone"
                    )
                  }}
                </span>

                <a
                  v-if="loan.trustee.phone"
                  :href="phoneHref(loan.trustee.phone)"
                  dir="ltr"
                  class="w-fit font-semibold text-brand hover:underline"
                >
                  {{ loan.trustee.phone }}
                </a>

                <span v-else>—</span>
              </div>

              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.community"
                    )
                  }}
                </span>

                <span>
                  {{
                    loan.trustee
                      .community ||
                    "—"
                  }}
                </span>
              </div>

              <div
                class="detail-item"
              >
                <span
                  class="detail-label"
                >
                  {{
                    t(
                      "loanDetails.notes"
                    )
                  }}
                </span>

                <span>
                  {{
                    loan.trustee
                      .notes ||
                    "—"
                  }}
                </span>
              </div>
            </div>
          </section>
        </template>
      </template>

      <template #schedule>
        <PaymentScheduleTab
          :loan-id="
            loan.id
          "
          :active="
            activeTab ===
            'schedule'
          "
        />
      </template>
    </TabsSection>

    <div
      v-if="
        auth.isAdmin.value
      "
      class="border-t border-line pt-4"
    >
      <EditLoanButton
        :loan-id="
          loan.id
        "
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  ref,
} from "vue";

import {
  useI18n,
} from "vue-i18n";

import {
  useAuth,
} from "../../composables/useAuth";

import type {
  Loan,
  LoanChecksDetails,
  LoanStandingOrderDetails,
} from "../../types/loan";

import BorrowerInfoSection
  from "./BorrowerInfoSection.vue";

import TabsSection
  from "./TabsSection.vue";

import EditLoanButton
  from "./EditLoanButton.vue";

import PaymentScheduleTab
  from "./PaymentScheduleTab.vue";

const props =
  withDefaults(
    defineProps<{
      loan: Loan;
      showStatus?: boolean;
    }>(),
    {
      showStatus: true,
    }
  );

const showStatus =
  computed(() =>
    props.showStatus
  );

const {
  t,
  locale,
} = useI18n();

const auth =
  useAuth();


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

const activeTab =
  ref<
    | "details"
    | "schedule"
  >(
    "details"
  );

const isHebrew =
  computed(
    () =>
      locale.value ===
      "he"
  );

const loanTypeLabel =
  computed(() =>
    props.loan.type === "checks"
      ? text("צ'קים", "Checks", "Cheques")
      : text("הוראת קבע", "Standing order", "Domiciliación")
  );

const loanStatusLabel =
  computed(() => {
    if (
      props.loan.status ===
      "OVERDUE"
    ) {
      return isHebrew.value
        ? "בעייתית"
        : "Needs attention";
    }

    if (
      props.loan.status ===
      "CLOSED"
    ) {
      return isHebrew.value
        ? "הסתיימה"
        : "Completed";
    }

    return isHebrew.value
      ? "פעילה"
      : "Active";
  });

const loanStatusClass =
  computed(() => {
    if (
      props.loan.status ===
      "OVERDUE"
    ) {
      return (
        "bg-danger/10 " +
        "text-danger"
      );
    }

    if (
      props.loan.status ===
      "CLOSED"
    ) {
      return (
        "bg-success/10 " +
        "text-success-deep"
      );
    }

    return (
      "bg-brand/10 " +
      "text-brand"
    );
  });

const checksDetails =
  computed<LoanChecksDetails | null>(() => {
    if (
      props.loan.type !==
      "checks"
    ) {
      return null;
    }

    const details =
      props.loan.details;

    if (
      !(
        "predefinedSchedule"
        in details
      )
    ) {
      return null;
    }

    return details;
  });


const standingDetails =
  computed<LoanStandingOrderDetails | null>(() => {
    if (
      props.loan.type !==
      "standing_order"
    ) {
      return null;
    }

    const details =
      props.loan.details;

    if (
      !(
        "monthlyAmount"
        in details
      )
    ) {
      return null;
    }

    return details;
  });

const signedFormTitle =
  computed(() =>
    text(
      "טופס הלוואה חתום",
      "Signed loan form",
      "Formulario de préstamo firmado"
    )
  );

const signedFormAvailableLabel =
  computed(() =>
    text(
      "המסמך החתום שמור במערכת",
      "Signed document is stored",
      "El documento firmado está guardado"
    )
  );

const signedFormOpenLabel =
  computed(() =>
    text("פתיחת המסמך", "Open document", "Abrir documento")
  );

const signedFormMissingLabel =
  computed(() =>
    text(
      "לא נמצא מסמך חתום עבור הלוואה זו.",
      "No signed document is stored for this loan.",
      "No hay un documento firmado guardado para este préstamo."
    )
  );

const standingOrderFormTitle =
  computed(() =>
    text(
      "אישור הוראת קבע",
      "Standing order authorization",
      "Autorización de domiciliación"
    )
  );

const standingOrderFormAvailableLabel =
  computed(() =>
    text(
      "אישור הוראת הקבע שמור במערכת",
      "Standing order authorization is stored",
      "La autorización está guardada"
    )
  );

const standingOrderFormMissingLabel =
  computed(() =>
    text(
      "לא נמצא אישור הוראת קבע עבור הלוואה זו.",
      "No standing order authorization is stored for this loan.",
      "No hay una autorización de domiciliación guardada para este préstamo."
    )
  );

function formatCurrency(
  amount: number
) {
  return new Intl.NumberFormat(
    locale.value === "he"
      ? "he-IL"
      : locale.value === "es"
        ? "es-ES"
        : "en-US",
    {
      style: "currency",
      currency: "ILS",
      maximumFractionDigits: 2,
    }
  ).format(
    Number(
      amount || 0
    )
  );
}

function formatDate(
  date?: string
) {
  if (!date) {
    return "—";
  }

  const normalized =
    date.length === 10
      ? `${date}T00:00:00`
      : date;

  const value =
    new Date(
      normalized
    );

  if (
    Number.isNaN(
      value.getTime()
    )
  ) {
    return date;
  }

  return value.toLocaleDateString(
    isHebrew.value
      ? "he-IL"
      : "en-US"
  );
}

function phoneHref(
  phone: string
): string {
  const cleaned =
    String(phone || "")
      .replace(
        /[^\d+]/g,
        ""
      );

  return `tel:${cleaned}`;
}


function handleTabChange(
  tab:
    | "details"
    | "schedule"
) {
  activeTab.value =
    tab;
}
</script>

<style scoped>
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-radius: 0.5rem;
  background: var(--color-canvas);
  padding: 0.75rem;
}

.detail-label {
  color: var(--color-muted);
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 500;
}
</style>