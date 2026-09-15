<template>
  <AppLayout
    :title="
      t(
        'loanDetails.title'
      )
    "
    :subtitle="
      loan?.borrower?.name ||
      ''
    "
    :show-back-button="true"
    :show-language-toggle="true"
    max-width="5xl"
  >
    <!-- Loading -->
    <div
      v-if="loading"
      class="flex flex-col items-center justify-center py-16"
    >
      <div
        class="h-10 w-10 animate-spin rounded-full border-4 border-brand border-t-transparent"
      ></div>

      <p
        class="mt-4 text-sm font-medium text-muted"
      >
        {{
          t(
            "loanList.messages.loading"
          )
        }}
      </p>
    </div>

    <!-- Error -->
    <div
      v-else-if="
        errorMessage
      "
      class="rounded-2xl border border-red-200 bg-red-50 p-6 text-center"
    >
      <p
        class="text-sm font-medium text-red-700"
      >
        {{ errorMessage }}
      </p>

      <button
        type="button"
        class="mt-4 rounded-xl bg-brand px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-deep"
        @click="
          loadLoan
        "
      >
        {{ retryLabel }}
      </button>
    </div>

    <!-- Loan details -->
    <div
      v-else-if="loan"
      class="space-y-6"
    >
      <LoanDetailsPanel
        :loan="loan"
      />
    </div>

    <!-- Not found -->
    <div
      v-else
      class="py-16 text-center"
    >
      <p
        class="text-lg text-muted"
      >
        {{
          t(
            "loanDetails.notFound"
          )
        }}
      </p>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
  watch,
} from "vue";

import {
  useRoute,
} from "vue-router";

import {
  useI18n,
} from "vue-i18n";

import AppLayout
  from "../components/AppLayout.vue";

import LoanDetailsPanel
  from "../components/loan-details/LoanDetailsPanel.vue";

import loanService
  from "../services/loanService";

import type {
  Loan,
} from "../types/loan";

const route =
  useRoute();

const {
  t,
  locale,
} = useI18n();

const loan =
  ref<Loan | null>(
    null
  );

const loading =
  ref(false);

const errorMessage =
  ref("");

const loanId =
  computed(() =>
    typeof route.params.id ===
    "string"
      ? route.params.id
      : ""
  );

const retryLabel =
  computed(() =>
    locale.value ===
    "he"
      ? "נסה שוב"
      : "Retry"
  );

async function loadLoan() {
  if (!loanId.value) {
    loan.value =
      null;

    errorMessage.value =
      t(
        "loanDetails.notFound"
      );

    return;
  }

  loading.value =
    true;

  errorMessage.value =
    "";

  try {
    loan.value =
      await loanService
        .getLoanDetails(
          loanId.value
        );
  } catch (
    requestError: any
  ) {
    loan.value =
      null;

    const status =
      requestError
        ?.response
        ?.status;

    if (
      status === 403
    ) {
      errorMessage.value =
        locale.value ===
        "he"
          ? "אין לך הרשאה לצפות בהלוואה זו."
          : "You do not have permission to view this loan.";
    } else if (
      status === 404
    ) {
      errorMessage.value =
        t(
          "loanDetails.notFound"
        );
    } else {
      errorMessage.value =
        requestError
          ?.response
          ?.data
          ?.detail ||
        (
          locale.value ===
          "he"
            ? "טעינת פרטי ההלוואה נכשלה."
            : "Failed to load loan details."
        );
    }
  } finally {
    loading.value =
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