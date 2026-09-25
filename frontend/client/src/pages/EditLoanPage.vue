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
import TrusteePicker from "../components/TrusteePicker.vue";

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
  computed<"he" | "en" | "es">(
    () =>
      locale.value === "he"
        ? "he"
        : locale.value === "es"
          ? "es"
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
  name: string;
  community?: string;
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


function normalizeTrustee(
  raw: any
): TrusteeOption {
  const user =
    raw?.user_details ||
    raw?.user ||
    {};

  const firstName =
    String(
      user.first_name ||
      raw?.first_name ||
      ""
    ).trim();

  const lastName =
    String(
      user.last_name ||
      raw?.last_name ||
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
      raw?.username ||
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

    name: baseName,
    community,
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
    :title="t('editLoan.title')"
    :show-language-toggle="true"
    :show-back-button="true"
    max-width="5xl"
  >
    <div class="mx-auto w-full max-w-4xl space-y-5">
      <div
        v-if="loading"
        class="flex flex-col items-center justify-center rounded-2xl border border-line bg-white py-16"
      >
        <div
          class="h-9 w-9 animate-spin rounded-full border-4 border-brand border-t-transparent"
        ></div>

        <p class="mt-4 text-sm text-muted">
          {{ isHebrew ? "טוען פרטי הלוואה..." : "Loading loan details..." }}
        </p>
      </div>

      <div
        v-else-if="error && !loanData"
        class="rounded-2xl border border-red-200 bg-red-50 p-6 text-center"
      >
        <p class="text-sm font-medium text-red-700">
          {{ error }}
        </p>

        <button
          type="button"
          class="mt-4 rounded-xl bg-brand px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-deep"
          @click="loadLoan"
        >
          {{ retryLabel }}
        </button>
      </div>

      <template v-else-if="loanData">
        <div
          v-if="successMessage"
          class="rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-sm font-medium text-success-deep"
        >
          {{ successMessage }}
        </div>

        <div
          v-if="error"
          class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
        >
          {{ error }}
        </div>

        <!-- Loan context -->
        <section class="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div class="min-w-0">
              <h2 class="mt-1 truncate text-xl font-bold text-ink">
                {{ loanData.borrower?.name || "—" }}
              </h2>

            </div>

            <span
              class="inline-flex rounded-full bg-brand/10 px-3 py-1.5 text-xs font-semibold text-brand"
            >
              {{ loanTypeLabel }}
            </span>
          </div>
        </section>

        <!-- Trustee -->
        <FormCard
          :title="t('editLoan.sections.trustee')"
        >
          <TrusteePicker
            v-model="form.trustee_id"
            :options="trustees"
            :label="t('editLoan.fields.trustee')"
            :placeholder="isHebrew ? 'חיפוש נאמן לפי שם' : 'Search trustee by name'"
            :error-message="fieldErrors.trustee_id || trusteesError"
            :loading="trusteesLoading"
            :required="true"
            :isRTL="isRTL"
            :locale="formLocale"
            @update:model-value="delete fieldErrors.trustee_id"
          />
        </FormCard>

        <!-- Editable loan fields -->
        <FormCard
          :title="isHebrew ? 'פרטי ההלוואה' : 'Loan details'"
        >
          <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
            <FormInput
              v-model="form.amount"
              :label="t('editLoan.fields.amount')"
              :placeholder="t('editLoan.placeholders.amount')"
              icon="dollar"
              type="number"
              inputMode="decimal"
              :isRTL="isRTL"
              :required="true"
              min="0.01"
              step="0.01"
              :hasError="Boolean(fieldErrors.amount)"
              :errorMessage="fieldErrors.amount"
              @input="delete fieldErrors.amount"
            />

            <FormDatePicker
              v-model="form.start_date"
              :label="t('editLoan.fields.startDate')"
              :placeholder="t('editLoan.placeholders.startDate')"
              :locale="formLocale"
              :isRTL="isRTL"
              :required="true"
              :hasError="Boolean(fieldErrors.start_date)"
              :errorMessage="fieldErrors.start_date"
            />

            <FormInput
              v-model="form.number_of_payments"
              :label="t('editLoan.fields.numPayments')"
              :placeholder="t('editLoan.placeholders.numPayments')"
              type="number"
              inputMode="numeric"
              :isRTL="isRTL"
              :required="true"
              min="1"
              step="1"
              :hasError="Boolean(fieldErrors.number_of_payments)"
              :errorMessage="fieldErrors.number_of_payments"
              @input="delete fieldErrors.number_of_payments"
            />
          </div>
        </FormCard>

        <!-- Actions -->
        <section
          class="flex flex-col-reverse gap-3 rounded-2xl border border-line bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
        >
          <p class="text-xs text-muted">
            {{
              isHebrew
                ? "השינויים ייכנסו לתוקף לאחר לחיצה על שמירה."
                : "Changes take effect after you select Save."
            }}
          </p>

          <div class="flex flex-col-reverse gap-2 sm:flex-row">
            <button
              type="button"
              :disabled="saving"
              class="h-11 rounded-xl border border-line bg-white px-5 text-sm font-semibold text-ink-soft transition hover:bg-surface-muted disabled:cursor-not-allowed disabled:opacity-50"
              @click="onCancel"
            >
              {{ t("editLoan.actions.cancel") }}
            </button>

            <button
              type="button"
              :disabled="saving || trusteesLoading"
              class="h-11 rounded-xl bg-brand px-6 text-sm font-semibold text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep disabled:cursor-not-allowed disabled:bg-faint disabled:shadow-none"
              @click="onSave"
            >
              {{ saving ? savingLabel : t("editLoan.actions.save") }}
            </button>
          </div>
        </section>
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