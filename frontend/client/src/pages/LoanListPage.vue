<!-- src/pages/LoanList.vue -->
<template>
  <AppLayout>

    <!-- כותרת העמוד -->
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold">{{ t("loan.activeLoans") }}</h1>

      <button
        @click="goToCreate"
        class="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition font-medium shadow"
      >
        {{ t("loan.createNewLoan") }}
      </button>
    </div>

    <!-- פילטר סוג הלוואה -->
    <div class="mb-6 flex items-center gap-3">
      <label class="text-gray-600 font-medium">
        {{ t("loan.filterByType") }}
      </label>

      <select
        v-model="loanType"
        class="border rounded-lg px-3 py-2 bg-white shadow-sm focus:ring-2 focus:ring-blue-400"
      >
        <option value="all">All</option>
        <option value="checks">Checks</option>
        <option value="standing">Standing Orders</option>
      </select>
    </div>

    <!-- כרטיס הטבלה -->
    <div class="bg-white shadow-md rounded-xl border p-4">

      <LoanTable
        :loans="loans"
        :openLoanId="openLoanId"
        @row-click="onRowClick"
        @row-close="onCloseRow"
      />

      <div v-if="loading" class="text-gray-500 mt-4 text-center">Loading...</div>
      <div v-if="error" class="text-red-600 mt-4 text-center">{{ error }}</div>

    </div>

  </AppLayout>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import AppLayout from "../components/AppLayout.vue";
import LoanTable from "../components/LoanTable.vue";

import { useLoans } from "../composables/useLoans";
import { useLoanFilters } from "../composables/useLoanFilters";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

function goToCreate() {
  router.push("/loans/new");
}

// ========== API / דמו ==========
const { loans, loadLoans, loading, error } = useLoans();
const { loanType } = useLoanFilters();

// דמו זמני — לא נוגעים בזה
loans.value = [
  {
    loan_id: "1",
    loan_type: "checks",
    amount: 1000,
    start_date: "2025-01-01",
    status: "ACTIVE",
    created_at: "2025-01-01T00:00:00Z",

    borrower: {
      id_number: "123456781",
      name: "Shira Cohen",
      phone: "050-1234567",
      email: "shira@example.com",
      address: "רח׳ הר חומה 12, ירושלים",
      created_at: "2025-01-01T00:00:00Z"
    },

    trustee: {
      name: "Moshe Levi",
      community: "רמות",
      phone: "050-2000001",
      notes: "נאמן ראשי"
    },

    details: {
      num_payments: 10,
      check_details: "Demo checks",
      predefined_schedule: true
    },

    form_file_url: null
  },

  {
    loan_id: "2",
    loan_type: "standing",
    amount: 2500,
    start_date: "2025-03-01",
    status: "OVERDUE",
    created_at: "2025-02-15T00:00:00Z",

    borrower: {
      id_number: "222222222",
      name: "Dana Levi",
      phone: "052-7654321",
      email: "dana@example.com",
      address: "שדרות הרצל 50, ירושלים",
      created_at: "2025-02-01T00:00:00Z"
    },

    trustee: {
      name: "Yossi Bar",
      community: "הר נוף",
      phone: "050-8888888",
      notes: "נאמן חדש"
    },

    details: {
      monthly_amount: "300.00",
      charge_day: 15,
      stop_date: null
    },

    form_file_url: null
  }
];


// ========== תמיכה ב־URL: /loans/:id ==========

// אם יש URL /loans/2 — נפתח את השורה של 2
const openLoanId = ref(route.params.id ? String(route.params.id) : null);

// כאשר לוחצים על שורה
function onRowClick(loanId: string) {
  openLoanId.value = loanId;
  router.replace(`/loans/${loanId}`);
}

// כאשר סוגרים שורה
function onCloseRow() {
  openLoanId.value = null;
  router.replace("/loans");
}
</script>
