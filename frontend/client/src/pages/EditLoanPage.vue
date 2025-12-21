<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useLocale } from "../composables/useLocale";

import AppLayout from "../components/AppLayout.vue";
import FormCard from "../components/FormCard.vue";
import FormInput from "../components/FormInput.vue";
import FormDatePicker from "../components/FormDatePicker.vue";
import PrimaryButton from "../components/PrimaryButton.vue";

const { t, locale, isRTL } = useLocale();
const router = useRouter();
const route = useRoute();

const loanId = computed(() => String(route.params.id || ""));

// Date picker expects only "he" | "en"
const formLocale = computed<"he" | "en">(() =>
  locale.value === "he" ? "he" : "en"
);

const form = ref({
  amount: "",
  start_date: "",
  number_of_payments: "",
  trustee_id: "",
  status: "ACTIVE",
});

function onCancel() {
  router.back();
}

function onSave() {
  // FE3 will implement PUT. For now: do nothing / show console
  console.log("[EditLoan] Save clicked", loanId.value, form.value);
}
</script>

<template>
  <AppLayout :title="t('editLoan.title')" :isRTL="isRTL" :t="t">
    <div class="max-w-3xl mx-auto px-4 py-6">
      <FormCard :title="t('editLoan.cardTitle')" :badge="loanId">
        <FormInput
          v-model="form.amount"
          :label="t('editLoan.fields.amount')"
          :placeholder="t('editLoan.placeholders.amount')"
          icon="dollar"
          type="number"
          :isRTL="isRTL"
          required
          min="1"
          step="1"
        />

        <FormDatePicker
          v-model="form.start_date"
          :label="t('editLoan.fields.startDate')"
          :placeholder="t('editLoan.placeholders.startDate')"
          :locale="formLocale"
          :isRTL="isRTL"
          required
        />

        <FormInput
          v-model="form.number_of_payments"
          :label="t('editLoan.fields.numPayments')"
          :placeholder="t('editLoan.placeholders.numPayments')"
          type="number"
          :isRTL="isRTL"
          required
          min="1"
          step="1"
        />

        <!-- Trustee (static placeholder for FE1) -->
        <div class="flex flex-col">
          <p
            :dir="isRTL ? 'rtl' : 'ltr'"
            :class="isRTL ? 'text-right' : 'text-left'"
            class="pb-1.5 text-sm font-medium leading-normal text-[#6B7280]"
          >
            * {{ t("editLoan.fields.trustee") }}
          </p>

          <select
            v-model="form.trustee_id"
            :dir="isRTL ? 'rtl' : 'ltr'"
            class="h-11 w-full rounded-lg border border-[#E5E5EA] bg-white px-4 text-base focus:outline-0 focus:ring-2 focus:border-[#007AFF] focus:ring-[#007AFF]/20"
          >
            <option value="" disabled>{{ t("editLoan.placeholders.trustee") }}</option>
            <option value="demo-trustee-1">Demo Trustee 1</option>
            <option value="demo-trustee-2">Demo Trustee 2</option>
          </select>
        </div>

        <!-- Status -->
        <div class="flex flex-col">
          <p
            :dir="isRTL ? 'rtl' : 'ltr'"
            :class="isRTL ? 'text-right' : 'text-left'"
            class="pb-1.5 text-sm font-medium leading-normal text-[#6B7280]"
          >
            * {{ t("editLoan.fields.status") }}
          </p>

          <select
            v-model="form.status"
            :dir="isRTL ? 'rtl' : 'ltr'"
            class="h-11 w-full rounded-lg border border-[#E5E5EA] bg-white px-4 text-base focus:outline-0 focus:ring-2 focus:border-[#007AFF] focus:ring-[#007AFF]/20"
          >
            <option value="ACTIVE">ACTIVE</option>
            <option value="CLOSED">CLOSED</option>
            <option value="OVERDUE">OVERDUE</option>
          </select>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 justify-end pt-2">
          <button
            type="button"
            class="h-12 px-5 rounded-lg border border-[#E5E5EA] text-sm font-semibold hover:bg-gray-50"
            @click="onCancel"
          >
            {{ t("editLoan.actions.cancel") }}
          </button>

          <PrimaryButton :label="t('editLoan.actions.save')" :block="false" @click="onSave" />
        </div>
      </FormCard>
    </div>
  </AppLayout>
</template>
