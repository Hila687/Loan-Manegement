<script setup lang="ts">
import {
  computed,
  onMounted,
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

import AppLayout from "../components/AppLayout.vue";
import FormCard from "../components/FormCard.vue";
import FormInput from "../components/FormInput.vue";
import FormDatePicker from "../components/FormDatePicker.vue";

import api from "../services/api";

import {
  fetchLoanDetails,
  updateLoan,
} from "../services/api-loan";

import type {
  ApiLoanDetails,
} from "../types/api-loan";


const {
  t,
  locale,
  isRTL,
} = useLocale();

const route =
  useRoute();

const router =
  useRouter();


const loanId =
  computed(() =>
    typeof route.params.id ===
    "string"
      ? route.params.id
      : ""
  );


const formLocale =
  computed<"he" | "en">(
    () =>
      locale.value === "he"
        ? "he"
        : "en"
  );


const form =
  ref({
    amount: "",
    start_date: "",
    number_of_payments: "",
    trustee_id: "",
  });


const loanData =
  ref<ApiLoanDetails | null>(
    null
  );

const loading =
  ref(true);

const saving =
  ref(false);

const error =
  ref<string | null>(
    null
  );

const successMessage =
  ref<string | null>(
    null
  );

const fieldErrors =
  ref<
    Record<
      string,
      string
    >
  >({});


type TrusteeOption = {
  id: string;
  label: string;
};


const trustees =
  ref<TrusteeOption[]>([]);

const trusteesLoading =
  ref(false);

const trusteesError =
  ref<string | null>(
    null
  );


const isHebrew =
  computed(
    () =>
      locale.value ===
      "he"
  );


const loanTypeLabel =
  computed(() => {
    if (!loanData.value) {
      return "—";
    }

    return (
      loanData.value.loan_type ===
      "checks"
        ? t(
            "loan.types.checks"
          )
        : t(
            "loan.types.standingOrder"
          )
    );
  });


const statusLabel =
  computed(() => {
    const status =
      loanData.value?.status;

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
  });


const statusClass =
  computed(() => {
    const status =
      loanData.value?.status;

    if (
      status ===
      "OVERDUE"
    ) {
      return (
        "bg-danger/10 " +
        "text-danger"
      );
    }

    if (
      status ===
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


const automaticStatusNote =
  computed(() =>
    isHebrew.value
      ? "סטטוס ההלוואה מחושב אוטומטית לפי מצב התשלומים ולכן אינו נערך ידנית כאן."
      : "Loan status is calculated automatically from payment status and is not edited manually here."
  );


const loadErrorLabel =
  computed(() =>
    isHebrew.value
      ? "טעינת פרטי ההלוואה נכשלה."
      : "Failed to load loan details."
  );


const saveErrorLabel =
  computed(() =>
    isHebrew.value
      ? "שמירת השינויים נכשלה."
      : "Failed to save changes."
  );


const savedLabel =
  computed(() =>
    isHebrew.value
      ? "השינויים נשמרו בהצלחה."
      : "Changes saved successfully."
  );


const retryLabel =
  computed(() =>
    isHebrew.value
      ? "נסה שוב"
      : "Retry"
  );


const savingLabel =
  computed(() =>
    isHebrew.value
      ? "שומר..."
      : "Saving..."
  );


const readOnlyLabel =
  computed(() =>
    isHebrew.value
      ? "לקריאה בלבד"
      : "Read only"
  );


function normalizeTrustee(
  raw: any
): TrusteeOption {
  const user =
    raw?.user_details ||
    {};

  const firstName =
    String(
      user.first_name ||
      ""
    ).trim();

  const lastName =
    String(
      user.last_name ||
      ""
    ).trim();

  const fullName =
    `${firstName} ${lastName}`.trim();

  const community =
    String(
      raw?.community ||
      ""
    ).trim();

  const username =
    String(
      user.username ||
      ""
    ).trim();

  const baseName =
    fullName ||
    username ||
    (
      isHebrew.value
        ? "נאמן"
        : "Trustee"
    );

  return {
    id:
      String(
        raw?.trustee_id ||
        raw?.id ||
        ""
      ),

    label:
      community
        ? `${baseName} – ${community}`
        : baseName,
  };
}


async function fetchTrustees():
  Promise<void> {
  trusteesLoading.value =
    true;

  trusteesError.value =
    null;

  try {
    const response =
      await api.get(
        "/trustees/"
      );

    const data =
      Array.isArray(
        response.data
      )
        ? response.data
        : [];

    trustees.value =
      data
        .filter(
          (item: any) =>
            item?.is_active !==
            false
        )
        .map(
          (item: any) =>
            normalizeTrustee(
              item
            )
        )
        .filter(
          (
            item:
              TrusteeOption
          ) =>
            Boolean(
              item.id
            )
        );
  } catch {
    trustees.value =
      [];

    trusteesError.value =
      isHebrew.value
        ? "טעינת רשימת הנאמנים נכשלה."
        : "Failed to load trustees.";
  } finally {
    trusteesLoading.value =
      false;
  }
}


function mapLoanToForm(
  currentLoan:
    ApiLoanDetails
): void {
  form.value.amount =
    String(
      currentLoan.amount ??
      ""
    );

  form.value.start_date =
    String(
      currentLoan.start_date ||
      ""
    );

  form.value.number_of_payments =
    String(
      currentLoan.details
        ?.num_payments ??
      ""
    );

  form.value.trustee_id =
    String(
      currentLoan.trustee_id ||
      ""
    );
}


function clearErrors():
  void {
  fieldErrors.value =
    {};

  error.value =
    null;

  successMessage.value =
    null;
}


function firstErrorMessage(
  value: unknown
): string | null {
  if (
    typeof value ===
    "string"
  ) {
    return value;
  }

  if (
    Array.isArray(
      value
    ) &&
    value.length > 0
  ) {
    return firstErrorMessage(
      value[0]
    );
  }

  return null;
}


function setErrorsFromBackend(
  data: unknown
): void {
  if (
    !data ||
    typeof data !==
      "object" ||
    Array.isArray(
      data
    )
  ) {
    return;
  }

  const result:
    Record<
      string,
      string
    > = {};

  for (
    const [
      key,
      value,
    ]
    of Object.entries(
      data as Record<
        string,
        unknown
      >
    )
  ) {
    const message =
      firstErrorMessage(
        value
      );

    if (message) {
      result[key] =
        message;
    }
  }

  fieldErrors.value =
    result;
}


function validateForm():
  boolean {
  fieldErrors.value =
    {};

  const amount =
    Number(
      form.value.amount
    );

  const numberOfPayments =
    Number(
      form.value
        .number_of_payments
    );

  if (
    !Number.isFinite(
      amount
    ) ||
    amount <= 0
  ) {
    fieldErrors.value.amount =
      isHebrew.value
        ? "יש להזין סכום גדול מאפס."
        : "Amount must be greater than zero.";
  }

  if (
    !form.value.start_date
  ) {
    fieldErrors.value.start_date =
      isHebrew.value
        ? "יש לבחור תאריך התחלה."
        : "Start date is required.";
  }

  if (
    !Number.isInteger(
      numberOfPayments
    ) ||
    numberOfPayments < 1
  ) {
    fieldErrors.value
      .number_of_payments =
        isHebrew.value
          ? "מספר התשלומים חייב להיות לפחות 1."
          : "Number of payments must be at least 1.";
  }

  if (
    !form.value
      .trustee_id
  ) {
    fieldErrors.value.trustee_id =
      isHebrew.value
        ? "יש לבחור נאמן."
        : "Trustee is required.";
  }

  return (
    Object.keys(
      fieldErrors.value
    ).length === 0
  );
}


async function loadLoan():
  Promise<void> {
  if (!loanId.value) {
    error.value =
      isHebrew.value
        ? "מזהה ההלוואה חסר."
        : "Loan ID is missing.";

    loading.value =
      false;

    return;
  }

  loading.value =
    true;

  error.value =
    null;

  successMessage.value =
    null;

  try {
    const [
      currentLoan,
    ] =
      await Promise.all([
        fetchLoanDetails(
          loanId.value
        ),

        fetchTrustees(),
      ]);

    loanData.value =
      currentLoan;

    mapLoanToForm(
      currentLoan
    );
  } catch (
    requestError: any
  ) {
    loanData.value =
      null;

    const status =
      requestError
        ?.response
        ?.status;

    if (
      status === 403
    ) {
      error.value =
        isHebrew.value
          ? "אין לך הרשאה לערוך הלוואה זו."
          : "You do not have permission to edit this loan.";
    } else if (
      status === 404
    ) {
      error.value =
        isHebrew.value
          ? "ההלוואה לא נמצאה."
          : "Loan not found.";
    } else {
      error.value =
        requestError
          ?.response
          ?.data
          ?.detail ||
        loadErrorLabel.value;
    }
  } finally {
    loading.value =
      false;
  }
}


function onCancel():
  void {
  if (
    window.history.length >
    1
  ) {
    router.back();

    return;
  }

  router.push(
    "/loans"
  );
}


async function onSave():
  Promise<void> {
  if (
    saving.value ||
    !loanData.value
  ) {
    return;
  }

  clearErrors();

  if (
    !validateForm()
  ) {
    error.value =
      isHebrew.value
        ? "יש לתקן את השדות המסומנים."
        : "Please correct the highlighted fields.";

    return;
  }

  saving.value =
    true;

  try {
    const updatedLoan =
      await updateLoan(
        loanId.value,
        {
          amount:
            Number(
              form.value
                .amount
            ),

          start_date:
            form.value
              .start_date,

          number_of_payments:
            Number(
              form.value
                .number_of_payments
            ),

          trustee_id:
            form.value
              .trustee_id,

          status:
            loanData.value
              .status,
        }
      );

    loanData.value =
      updatedLoan;

    mapLoanToForm(
      updatedLoan
    );

    successMessage.value =
      savedLabel.value;

    window.setTimeout(
      () => {
        router.push(
          `/loans/${encodeURIComponent(
            loanId.value
          )}/details`
        );
      },
      500
    );
  } catch (
    requestError: any
  ) {
    const status =
      requestError
        ?.response
        ?.status;

    const data =
      requestError
        ?.response
        ?.data;

    if (
      status === 400 &&
      data
    ) {
      setErrorsFromBackend(
        data
      );

      error.value =
        isHebrew.value
          ? "יש לתקן את השדות המסומנים."
          : "Please correct the highlighted fields.";
    } else if (
      status === 403
    ) {
      error.value =
        isHebrew.value
          ? "אין לך הרשאה לערוך הלוואה זו."
          : "You do not have permission to edit this loan.";
    } else if (
      status === 404
    ) {
      error.value =
        isHebrew.value
          ? "ההלוואה לא נמצאה."
          : "Loan not found.";
    } else {
      error.value =
        data?.detail ||
        saveErrorLabel.value;
    }
  } finally {
    saving.value =
      false;
  }
}


onMounted(() => {
  loadLoan();
});


watch(
  loanId,
  () => {
    loadLoan();
  }
);
</script>


<template>
  <AppLayout
    :title="
      t(
        'editLoan.title'
      )
    "
    :subtitle="
      loanData
        ?.borrower
        ?.name ||
      ''
    "
    :show-language-toggle="true"
    :show-back-button="true"
    max-width="4xl"
  >
    <div
      class="mx-auto w-full max-w-3xl"
    >
      <!-- Loading -->
      <div
        v-if="
          loading
        "
        class="flex flex-col items-center justify-center py-16"
      >
        <div
          class="h-9 w-9 animate-spin rounded-full border-4 border-brand border-t-transparent"
        ></div>

        <p
          class="mt-4 text-sm text-muted"
        >
          {{
            isHebrew
              ? "טוען פרטי הלוואה..."
              : "Loading loan details..."
          }}
        </p>
      </div>

      <!-- Load error -->
      <div
        v-else-if="
          error &&
          !loanData
        "
        class="rounded-2xl border border-red-200 bg-red-50 p-6 text-center"
      >
        <p
          class="text-sm font-medium text-red-700"
        >
          {{ error }}
        </p>

        <button
          type="button"
          class="mt-4 rounded-xl bg-brand px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-deep"
          @click="
            loadLoan
          "
        >
          {{
            retryLabel
          }}
        </button>
      </div>

      <template
        v-else-if="
          loanData
        "
      >
        <!-- Save success -->
        <div
          v-if="
            successMessage
          "
          class="mb-4 rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-sm font-medium text-success-deep"
        >
          {{
            successMessage
          }}
        </div>

        <!-- Save error -->
        <div
          v-if="
            error
          "
          class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
        >
          {{ error }}
        </div>

        <FormCard
          :title="
            t(
              'editLoan.cardTitle'
            )
          "
          :badge="
            loanId
          "
        >
          <!-- Read-only loan context -->
          <div
            class="grid grid-cols-1 gap-3 rounded-xl border border-line bg-canvas p-4 sm:grid-cols-2"
          >
            <div>
              <p
                class="text-xs font-medium text-muted"
              >
                {{
                  isHebrew
                    ? "סוג הלוואה"
                    : "Loan type"
                }}
              </p>

              <p
                class="mt-1 text-sm font-semibold text-ink"
              >
                {{
                  loanTypeLabel
                }}
              </p>
            </div>

            <div>
              <div
                class="flex items-center gap-2"
              >
                <p
                  class="text-xs font-medium text-muted"
                >
                  {{
                    t(
                      "editLoan.fields.status"
                    )
                  }}
                </p>

                <span
                  class="rounded-full bg-white px-2 py-0.5 text-[10px] font-medium text-muted"
                >
                  {{
                    readOnlyLabel
                  }}
                </span>
              </div>

              <span
                class="mt-1 inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="
                  statusClass
                "
              >
                {{
                  statusLabel
                }}
              </span>
            </div>
          </div>

          <p
            class="rounded-lg border border-brand/15 bg-brand/5 px-3 py-2 text-xs leading-5 text-ink-soft"
          >
            {{
              automaticStatusNote
            }}
          </p>

          <!-- Amount -->
          <FormInput
            v-model="
              form.amount
            "
            :label="
              t(
                'editLoan.fields.amount'
              )
            "
            :placeholder="
              t(
                'editLoan.placeholders.amount'
              )
            "
            icon="dollar"
            type="number"
            inputMode="decimal"
            :isRTL="
              isRTL
            "
            :required="
              true
            "
            min="0.01"
            step="0.01"
            :hasError="
              Boolean(
                fieldErrors.amount
              )
            "
            :errorMessage="
              fieldErrors.amount
            "
            @input="
              delete fieldErrors.amount
            "
          />

          <!-- Start date -->
          <FormDatePicker
            v-model="
              form.start_date
            "
            :label="
              t(
                'editLoan.fields.startDate'
              )
            "
            :placeholder="
              t(
                'editLoan.placeholders.startDate'
              )
            "
            :locale="
              formLocale
            "
            :isRTL="
              isRTL
            "
            :required="
              true
            "
            :hasError="
              Boolean(
                fieldErrors.start_date
              )
            "
            :errorMessage="
              fieldErrors.start_date
            "
          />

          <!-- Number of payments -->
          <FormInput
            v-model="
              form.number_of_payments
            "
            :label="
              t(
                'editLoan.fields.numPayments'
              )
            "
            :placeholder="
              t(
                'editLoan.placeholders.numPayments'
              )
            "
            type="number"
            inputMode="numeric"
            :isRTL="
              isRTL
            "
            :required="
              true
            "
            min="1"
            step="1"
            :hasError="
              Boolean(
                fieldErrors.number_of_payments
              )
            "
            :errorMessage="
              fieldErrors.number_of_payments
            "
            @input="
              delete fieldErrors.number_of_payments
            "
          />

          <!-- Trustee -->
          <div
            class="flex flex-col gap-2"
          >
            <h2
              class="pt-2 text-lg font-semibold text-ink"
              :dir="
                isRTL
                  ? 'rtl'
                  : 'ltr'
              "
              :class="
                isRTL
                  ? 'text-right'
                  : 'text-left'
              "
            >
              {{
                t(
                  "editLoan.sections.trustee"
                )
              }}
            </h2>

            <p
              :dir="
                isRTL
                  ? 'rtl'
                  : 'ltr'
              "
              :class="
                isRTL
                  ? 'text-right'
                  : 'text-left'
              "
              class="pb-1 text-sm font-medium text-muted"
            >
              <span
                :class="
                  fieldErrors.trustee_id
                    ? 'text-danger'
                    : 'text-muted'
                "
              >
                *
              </span>

              {{
                t(
                  "editLoan.fields.trustee"
                )
              }}
            </p>

            <select
              v-model="
                form.trustee_id
              "
              :disabled="
                trusteesLoading
              "
              :dir="
                isRTL
                  ? 'rtl'
                  : 'ltr'
              "
              class="h-11 w-full rounded-lg border bg-white px-4 text-base outline-none transition focus:ring-2 disabled:cursor-wait disabled:bg-surface-muted"
              :class="
                fieldErrors.trustee_id
                  ? 'border-danger focus:border-danger focus:ring-danger/20'
                  : 'border-line focus:border-brand focus:ring-brand/20'
              "
              @change="
                delete fieldErrors.trustee_id
              "
            >
              <option
                value=""
                disabled
              >
                {{
                  trusteesLoading
                    ? (
                        isHebrew
                          ? "טוען נאמנים..."
                          : "Loading trustees..."
                      )
                    : t(
                        "editLoan.placeholders.trustee"
                      )
                }}
              </option>

              <option
                v-for="
                  trustee
                  in trustees
                "
                :key="
                  trustee.id
                "
                :value="
                  trustee.id
                "
              >
                {{
                  trustee.label
                }}
              </option>
            </select>

            <p
              v-if="
                trusteesError
              "
              class="text-xs text-danger"
            >
              {{
                trusteesError
              }}
            </p>

            <p
              v-if="
                fieldErrors.trustee_id
              "
              class="text-xs text-danger"
            >
              {{
                fieldErrors.trustee_id
              }}
            </p>
          </div>

          <!-- Actions -->
          <div
            class="flex flex-col-reverse gap-3 border-t border-line pt-5 sm:flex-row sm:justify-end"
          >
            <button
              type="button"
              :disabled="
                saving
              "
              class="h-12 rounded-xl border border-line bg-white px-5 text-sm font-semibold text-ink-soft transition hover:bg-surface-muted disabled:cursor-not-allowed disabled:opacity-50"
              @click="
                onCancel
              "
            >
              {{
                t(
                  "editLoan.actions.cancel"
                )
              }}
            </button>

            <button
              type="button"
              :disabled="
                saving ||
                trusteesLoading
              "
              class="h-12 rounded-xl bg-brand px-6 text-sm font-semibold text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep disabled:cursor-not-allowed disabled:bg-faint disabled:shadow-none"
              @click="
                onSave
              "
            >
              {{
                saving
                  ? savingLabel
                  : t(
                      "editLoan.actions.save"
                    )
              }}
            </button>
          </div>
        </FormCard>
      </template>
    </div>
  </AppLayout>
</template>


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