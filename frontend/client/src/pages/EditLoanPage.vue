<script setup lang="ts">
    import { ref, computed, onMounted } from "vue";
    import { useRoute, useRouter } from "vue-router";
    import { useLocale } from "../composables/useLocale";
    
    import AppLayout from "../components/AppLayout.vue";
    import FormCard from "../components/FormCard.vue";
    import FormInput from "../components/FormInput.vue";
    import FormDatePicker from "../components/FormDatePicker.vue";
    import PrimaryButton from "../components/PrimaryButton.vue";
    
    import { fetchLoanDetails } from "../services/api-loan";
    
    const { t, locale, isRTL } = useLocale();
    const router = useRouter();
    const route = useRoute();
    
    const loanId = computed(() => String(route.params.id || ""));
    
    // Date picker expects only "he" | "en"
    const formLocale = computed<"he" | "en">(() =>
      locale.value === "he" ? "he" : "en"
    );
    
    // ---- state ----
    const form = ref({
      amount: "",
      start_date: "",
      number_of_payments: "",
      trustee_id: "",
      status: "ACTIVE",
    });
    
    const loanData = ref<any | null>(null);
    const loading = ref(true);
    const error = ref<string | null>(null);
    
    // ---- computed: trustee label ----
    const trusteeLabel = computed(() => {
      if (!loanData.value?.trustee) return "";
      const tData = loanData.value.trustee;
      return `${tData.community}${tData.name ? " – " + tData.name : ""}`;
    });

    // ---- computed: loan type label (FE2 – display only) ----
    const loanTypeLabel = computed(() => {
        if (!loanData.value?.type) return "";

        return loanData.value.type === "checks"
            ? t("loan.types.checks")
            : t("loan.types.standingOrder");
        });

    
    // ---- map backend loan -> edit form ----
    function mapLoanToForm(loan: any) {
      // amount
      form.value.amount = String(loan.amount);
    
      // start date
      if (loan.startDate) {
        form.value.start_date = new Date(loan.startDate);
      }
    
      // status
      form.value.status = loan.status;
    
      // loan type (normalized in adapter)
      const loanType = loan.type;
    
      if (loanType === "checks" && loan.details?.num_payments != null) {
        form.value.number_of_payments = String(loan.details.num_payments);
      } else if (
        loanType === "standing_order" &&
        loan.details?.monthly_amount != null
      ) {
        form.value.number_of_payments = String(
          Number(loan.amount) / loan.details.monthly_amount
        );
      } else {
        console.warn("[EditLoan] could not resolve number_of_payments", loan);
        form.value.number_of_payments = "";
      }
    
      // trustee (FE2: display only)
      form.value.trustee_id = loan.trustee_id ?? "";
    }
    
    // ---- lifecycle ----
    onMounted(async () => {
      loading.value = true;
      error.value = null;
    
      try {
        const loan = await fetchLoanDetails(loanId.value);
        loanData.value = loan;
    
        mapLoanToForm(loan);
      } catch (e) {
        console.error("[EditLoan] Failed to load loan", e);
        error.value =
          t("editLoan.errors.loadFailed") || "Failed to load loan details";
      } finally {
        loading.value = false;
      }
    });
    
    function onCancel() {
      router.back();
    }
    
    function onSave() {
      // FE3 will implement PUT
      console.log("[EditLoan] Save clicked", loanId.value, form.value);
    }
    </script>
    
    <template>
      <AppLayout :title="t('editLoan.title')" :isRTL="isRTL" :t="t">
        <div class="max-w-3xl mx-auto px-4 py-6">
          <!-- Loading -->
          <div v-if="loading" class="text-center py-10">
            Loading loan details...
          </div>
    
          <!-- Error -->
          <div v-else-if="error" class="text-center text-red-500 py-10">
            {{ error }}
          </div>
    
          <!-- Form -->
          <FormCard v-else :title="t('editLoan.cardTitle')" :badge="loanId">
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
    
            <!-- Trustee (FE2 – display only) -->
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
                disabled
                :dir="isRTL ? 'rtl' : 'ltr'"
                class="h-11 w-full rounded-lg border border-[#E5E5EA] bg-gray-100 px-4 text-base"
              >
                <option :value="form.trustee_id">
                  {{ trusteeLabel }}
                </option>
                
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
    
            <!-- Actions + Loan Type -->
            <div
            class="flex items-center justify-between pt-4"
            :dir="isRTL ? 'rtl' : 'ltr'"
            >
            <!-- Loan type label -->
            <span class="text-sm text-[#6B7280]">
                {{ loanTypeLabel }}
            </span>

            <!-- Buttons -->
            <div class="flex gap-3">
                <button
                type="button"
                class="h-12 px-5 rounded-lg border border-[#E5E5EA] text-sm font-semibold hover:bg-gray-50"
                @click="onCancel"
                >
                {{ t("editLoan.actions.cancel") }}
                </button>

                <PrimaryButton
                :label="t('editLoan.actions.save')"
                :block="false"
                @click="onSave"
                />
            </div>
            </div>

          </FormCard>
        </div>
      </AppLayout>
    </template>
    