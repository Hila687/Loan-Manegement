<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useLocale } from "../composables/useLocale";
import { useFormValidation } from "../composables/useFormValidation";
import { useFormFields } from "../composables/useFormFields";
import AppLayout from "../components/AppLayout.vue";
import FormCard from "../components/FormCard.vue";
import FormInput from "../components/FormInput.vue";
import FormDatePicker from "../components/FormDatePicker.vue";
import api from "../services/api";

// Localization: text function, current locale ref, RTL flag
const { t, locale, isRTL } = useLocale();

// Narrowed locale for FormDatePicker (only "he" or "en")
const formLocale = computed<"he" | "en">(() =>
  locale.value === "he" ? "he" : "en"
);

// Form validation composable
const {
  validationErrors,
  fieldErrorMessages,
  clearFieldError,
  setFieldError,
  clearAllErrors,
} = useFormValidation();

// Form fields focus / navigation composable
const { registerField, focusNextField, focusPreviousField } =
  useFormFields();

// Borrower data
const borrower = ref({
  first_name: "",
  last_name: "",
  id_number: "",
  phone: "",
  email: "",       // nullable
  address: "",
  trustee_id: "",
  trustee_name: "",
});

// Loan data
const loan = ref({
  loan_type: "checks" as "checks" | "standing_order",
  amount: "",
  start_date: "",
  num_payments: "",
});


// Trustee option type
type TrusteeOption = {
  id: string; // trustee_id from backend
  name: string; // "first_name last_name" or username
  community: string; // community name
  label: string; // full display label for UI (name + community)
};

// File upload and generic UI state
const formFile = ref<File | null>(null);
const fileError = ref(false);
const loading = ref(false);
const error = ref<string | null>(null);
const errorTimeout = ref<ReturnType<typeof setTimeout> | null>(null);
const success = ref<string | null>(null);

// Trustees list and selection state
const trustees = ref<TrusteeOption[]>([]);
const trusteesLoading = ref(false);
const trusteeSearchQuery = ref("");
const showTrusteeDropdown = ref(false);
const highlightedTrusteeIndex = ref(-1);
const trusteesErrorMessage = ref("");

// timeout ref for blur handling
const trusteeBlurTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

// Field refs (for keyboard navigation)
const borrowerFirstNameRef = ref<HTMLInputElement | null>(null);
const borrowerLastNameRef = ref<HTMLInputElement | null>(null);
const borrowerIdNumberRef = ref<HTMLInputElement | null>(null);
const borrowerEmailRef = ref<HTMLInputElement | null>(null);
const borrowerPhoneRef = ref<HTMLInputElement | null>(null);
const borrowerAddressRef = ref<HTMLInputElement | null>(null);
const trusteeInputRef = ref<HTMLInputElement | null>(null);
const amountRef = ref<HTMLInputElement | null>(null);
const numPaymentsRef = ref<HTMLInputElement | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const datePickerRef = ref<HTMLInputElement | null>(null);

// Fields configuration for ordered navigation
const fields = [
  { name: "borrowerFirstName", ref: borrowerFirstNameRef, order: 0 },
  { name: "borrowerLastName", ref: borrowerLastNameRef, order: 1 },
  { name: "borrowerIdNumber", ref: borrowerIdNumberRef, order: 2 },
  { name: "borrowerPhone", ref: borrowerPhoneRef, order: 3 },
  { name: "borrowerEmail", ref: borrowerEmailRef, order: 4 },
  { name: "borrowerAddress", ref: borrowerAddressRef, order: 5 },
  { name: "trustee", ref: trusteeInputRef, order: 6 },
  { name: "amount", ref: amountRef, order: 7 },
  { name: "startDate", ref: datePickerRef, order: 8 },
  { name: "numPayments", ref: numPaymentsRef, order: 9 },
  { name: "file", ref: fileInputRef, order: 10 },
];

// Register fields and fetch trustees on mount
onMounted(() => {
  fields.forEach((f) => registerField(f.name, f.ref, f.order));
  fetchTrustees();
});

// Normalize raw trustee from backend into UI-friendly shape
function normalizeTrustee(raw: any): TrusteeOption {
  const user = raw.user_details || {};

  const first = (user.first_name || "").trim();
  const last = (user.last_name || "").trim();
  const fullName = (first + " " + last).trim();

  const community = (raw.community || "").trim();
  const username = (user.username || "").trim();

  // This is what we show to the user (no id, no username)
  let label = "";
  if (fullName && community) {
    label = `${fullName} – ${community}`;
  } else if (fullName) {
    label = fullName;
  } else if (community) {
    label = community;
  } else {
    label = "Unknown trustee";
  }

  // Internal "name" used only for searching
  const nameForSearch = fullName || username || "Unknown trustee";

  return {
    id: String(raw.trustee_id || raw.id || ""), // stays for submit
    name: nameForSearch,
    community,
    label,
  };
}

// Filtered trustees list for search
const filteredTrustees = computed(() => {
  if (!trusteeSearchQuery.value) return trustees.value;
  const q = trusteeSearchQuery.value.toLowerCase();

  return trustees.value.filter((t) => {
    return (
      t.name.toLowerCase().includes(q) ||
      t.community.toLowerCase().includes(q) ||
      t.label.toLowerCase().includes(q) ||
      t.id.toLowerCase().includes(q)
    );
  });
});

// Phone validation helper
function isValidPhone(phone: string) {
  if (!phone) return false;
  const cleanPhone = phone.replace(/[\s-]/g, "");
  const phoneRegex = /^\d{7,15}$/;
  return phoneRegex.test(cleanPhone);
}

// Phone input sanitization and update
function onPhoneInput(event: Event) {
  const target = event.target as HTMLInputElement;
  const raw = target.value || "";
  const sanitized = raw.replace(/[^\d-]/g, "");
  target.value = sanitized;
  borrower.value.phone = sanitized;
  clearFieldError("phone");
}

// Keyboard navigation between fields
function handleFieldKeydown(fieldName: string, event: KeyboardEvent) {
  const key = event.key;
  if (key !== "Enter" && key !== "ArrowDown" && key !== "ArrowUp") return;

  if (key === "Enter" || key === "ArrowDown") {
    event.preventDefault();
    focusNextField(fieldName);
  } else if (key === "ArrowUp") {
    event.preventDefault();
    focusPreviousField(fieldName);
  }
}

// Fetch trustees list from API
async function fetchTrustees() {
  trusteesLoading.value = true;
  trusteesErrorMessage.value = "";
  try {
    const response = await api.get("/trustees/");
    const rawList = (response.data || []) as any[];

    console.log("Trustees API response:", rawList);

    trustees.value = rawList.map((item) => normalizeTrustee(item));
  } catch (e) {
    console.error("Failed to fetch trustees:", e);
    trusteesErrorMessage.value = t("loanForm.messages.trusteesLoadError");
  } finally {
    trusteesLoading.value = false;
  }
}

// Select trustee from dropdown
function selectTrustee(trustee: TrusteeOption) {
  borrower.value.trustee_id = trustee.id; // this is what we send to backend
  borrower.value.trustee_name = trustee.label;
  trusteeSearchQuery.value = trustee.label;
  showTrusteeDropdown.value = false;
  highlightedTrusteeIndex.value = -1;
  clearFieldError("trustee");
}

// Trustee input focus handler
function onTrusteeInputFocus() {
  if (trusteeBlurTimeout.value) {
    clearTimeout(trusteeBlurTimeout.value);
    trusteeBlurTimeout.value = null;
  }

  showTrusteeDropdown.value = true;
  if (trustees.value.length === 0) {
    fetchTrustees();
  }
  highlightedTrusteeIndex.value =
    filteredTrustees.value.length > 0 ? 0 : -1;
}

// Trustee input value change handler
function onTrusteeInputChange(value: string) {
  trusteeSearchQuery.value = value;
  showTrusteeDropdown.value = true;
  clearFieldError("trustee");

  if (!value) {
    borrower.value.trustee_id = "";
    borrower.value.trustee_name = "";
  }

  highlightedTrusteeIndex.value =
    filteredTrustees.value.length > 0 ? 0 : -1;
}

// Trustee input keyboard support (dropdown navigation)
function onTrusteeKeydown(event: KeyboardEvent) {
  const list = filteredTrustees.value;
  const hasOptions = list.length > 0;

  if (event.key === "ArrowDown" || event.key === "ArrowUp") {
    if (hasOptions) {
      event.preventDefault();
      if (!showTrusteeDropdown.value) {
        showTrusteeDropdown.value = true;
        highlightedTrusteeIndex.value = 0;
        return;
      }

      if (event.key === "ArrowDown") {
        highlightedTrusteeIndex.value =
          highlightedTrusteeIndex.value < list.length - 1
            ? highlightedTrusteeIndex.value + 1
            : 0;
      } else if (event.key === "ArrowUp") {
        highlightedTrusteeIndex.value =
          highlightedTrusteeIndex.value > 0
            ? highlightedTrusteeIndex.value - 1
            : list.length - 1;
      }
      return;
    }
    handleFieldKeydown("trustee", event);
    return;
  }

  if (event.key === "Enter") {
    if (
      showTrusteeDropdown.value &&
      hasOptions &&
      highlightedTrusteeIndex.value >= 0
    ) {
      event.preventDefault();
      selectTrustee(list[highlightedTrusteeIndex.value]);
      return;
    }
    handleFieldKeydown("trustee", event);
    return;
  }

  if (event.key === "Escape") {
    if (showTrusteeDropdown.value) {
      event.preventDefault();
      showTrusteeDropdown.value = false;
    }
  }
}

// Close trustee dropdown with small delay (so click selection works)
function closeTrusteeDropdown() {
  showTrusteeDropdown.value = false;
  highlightedTrusteeIndex.value = -1;
}

function onTrusteeInputBlur() {
  trusteeBlurTimeout.value = setTimeout(() => {
    closeTrusteeDropdown();
    trusteeBlurTimeout.value = null;
  }, 200);
}

// File input change handler
function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0] || null;
  formFile.value = file;
  fileError.value = false;
  clearFieldError("file");
}

// Reset all form data and state
function resetForm() {
  borrower.value = {
    first_name: "",
    last_name: "",
    id_number: "",
    phone: "",
    email: "",
    address: "",
    trustee_id: "",
    trustee_name: "",
  };
  loan.value = { loan_type: "checks", amount: "", start_date: "", num_payments: "" };
  formFile.value = null;
  fileError.value = false;
  error.value = null;
  success.value = null;
  clearAllErrors();
  trusteeSearchQuery.value = "";
  showTrusteeDropdown.value = false;
  highlightedTrusteeIndex.value = -1;
  trusteesErrorMessage.value = "";
}

// Show error banner for a short duration
function showErrorMessage() {
  if (errorTimeout.value) {
    clearTimeout(errorTimeout.value);
  }
  errorTimeout.value = setTimeout(() => {
    error.value = null;
  }, 2000);
}

// Submit form to backend
async function submit() {
  clearAllErrors();
  error.value = null;
  fileError.value = false;

  let hasErrors = false;

  // Borrower first/last name validation
  if (!borrower.value.first_name || borrower.value.first_name.trim() === "") {
    setFieldError("first_name", t("loanForm.messages.nameRequired"));
    hasErrors = true;
  }

  if (!borrower.value.last_name || borrower.value.last_name.trim() === "") {
    setFieldError("last_name", t("loanForm.messages.nameRequired"));
    hasErrors = true;
  }


  // Borrower phone validation
  if (!borrower.value.phone || !isValidPhone(borrower.value.phone)) {
    setFieldError("phone", t("loanForm.messages.phoneInvalid"));
    hasErrors = true;
  }

  // Trustee validation
  if (!borrower.value.trustee_id) {
    setFieldError("trustee", t("loanForm.messages.validationError"));
    hasErrors = true;
  }

  // Amount validation
  if (!loan.value.amount || parseFloat(loan.value.amount) <= 0) {
    setFieldError("amount", t("loanForm.messages.amountInvalid"));
    hasErrors = true;
  }

  // Start date validation
  if (!loan.value.start_date) {
    setFieldError("start_date", t("loanForm.messages.startDateInvalid"));
    hasErrors = true;
  }

  // Number of payments validation
  if (!loan.value.num_payments || parseInt(loan.value.num_payments) <= 0) {
    setFieldError(
      "num_payments",
      t("loanForm.messages.numPaymentsInvalid")
    );
    hasErrors = true;
  }

  // File validation
  if (!formFile.value) {
    setFieldError("file", t("loanForm.messages.fileRequired"));
    fileError.value = true;
    hasErrors = true;
  }

  // If any validation failed, show banner and exit
  if (hasErrors) {
    error.value = t("loanForm.messages.requiredFieldsError");
    showErrorMessage();
    return;
  }

  // Send form data to backend
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append("borrower_name",
      `${borrower.value.first_name} ${borrower.value.last_name}`.trim()
    );

    formData.append("borrower_phone", borrower.value.phone);
    formData.append("borrower_address", borrower.value.address);
    formData.append("trustee_id", borrower.value.trustee_id);
    formData.append("amount", loan.value.amount);
    formData.append("start_date", loan.value.start_date);
    formData.append("num_payments", loan.value.num_payments);
    if (formFile.value) {
      formData.append("form_file", formFile.value);
    }

    await api.post("/loans/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    success.value = t("loanForm.messages.success");
    resetForm();
  } catch (e: any) {
    console.error(e);
    error.value =
      e?.response?.data?.detail ||
      t("loanForm.messages.genericError");
    showErrorMessage();
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AppLayout
    :title="t('loanForm.title')"
    :show-language-toggle="true"
    max-width="full"
  >
    <!-- Error notification banner -->
    <transition name="slide-down">
      <div
        v-if="error"
        class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-white border border-[#007AFF] px-6 py-4 rounded-lg shadow-lg"
      >
        <p class="text-sm font-medium text-[#007AFF]">
          {{ error }}
        </p>
      </div>
    </transition>

    <div class="flex flex-col gap-6 xl:gap-5 h-full">
      <div
        class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 xl:gap-5 auto-rows-max xl:auto-rows-max"
      >
        <!-- Borrower Details Card -->
        <FormCard
          :title="t('loanForm.sections.borrower')"
          :badge="t('loanForm.badges.borrower')"
        >
          <!-- Borrower First Name -->
          <FormInput
            ref="borrowerFirstNameRef"
            v-model="borrower.first_name"
            :label="t('loanForm.fields.borrowerFirstName')"
            :placeholder="t('loanForm.fields.borrowerFirstNamePlaceholder')"
            icon="user"
            :isRTL="isRTL"
            :required="true"
            :hasError="validationErrors.first_name"
            :errorMessage="fieldErrorMessages.first_name"
            @keydown="handleFieldKeydown('borrowerFirstName', $event)"
            @input="clearFieldError('first_name')"
          />

          <!-- Borrower Last Name -->
          <FormInput
            ref="borrowerLastNameRef"
            v-model="borrower.last_name"
            :label="t('loanForm.fields.borrowerLastName')"
            :placeholder="t('loanForm.fields.borrowerLastNamePlaceholder')"
            icon="user"
            :isRTL="isRTL"
            :required="true"
            :hasError="validationErrors.last_name"
            :errorMessage="fieldErrorMessages.last_name"
            @keydown="handleFieldKeydown('borrowerLastName', $event)"
            @input="clearFieldError('last_name')"
          />

          <!-- Borrower ID Number -->
          <FormInput
            ref="borrowerIdNumberRef"
            v-model="borrower.id_number"
            :label="t('loanForm.fields.borrowerIdNumber')"
            :placeholder="t('loanForm.fields.borrowerIdNumberPlaceholder')"
            type="text"
            icon="user"
            :isRTL="isRTL"
            :required="true"
            :hasError="validationErrors.id_number"
            :errorMessage="fieldErrorMessages.id_number"
            @keydown="handleFieldKeydown('borrowerIdNumber', $event)"
            @input="clearFieldError('id_number')"
          />

          <!-- Borrower Phone -->
          <FormInput
            ref="borrowerPhoneRef"
            v-model="borrower.phone"
            :label="t('loanForm.fields.borrowerPhone')"
            :placeholder="t('loanForm.fields.borrowerPhonePlaceholder')"
            type="tel"
            icon="phone"
            :isRTL="isRTL"
            :required="true"
            :hasError="validationErrors.phone"
            :errorMessage="fieldErrorMessages.phone"
            inputMode="tel"
            @input="onPhoneInput"
            @keydown="handleFieldKeydown('borrowerPhone', $event)"
          />

          <!-- Borrower Email (nullable) -->
          <FormInput
            ref="borrowerEmailRef"
            v-model="borrower.email"
            :label="t('loanForm.fields.borrowerEmail')"
            :placeholder="t('loanForm.fields.borrowerEmailPlaceholder')"
            type="email"
            :isRTL="isRTL"
            :required="false"
            :hasError="validationErrors.email"
            :errorMessage="fieldErrorMessages.email"
            @keydown="handleFieldKeydown('borrowerEmail', $event)"
            @input="clearFieldError('email')"
          />

          <!-- Borrower Address -->
          <FormInput
            ref="borrowerAddressRef"
            v-model="borrower.address"
            :label="t('loanForm.fields.borrowerAddress')"
            :placeholder="t('loanForm.fields.borrowerAddressPlaceholder')"
            icon="building"
            :isRTL="isRTL"
            @keydown="handleFieldKeydown('borrowerAddress', $event)"
          />

          <!-- Trustee Selection -->
          <label class="flex flex-col">
            <p
              :dir="isRTL ? 'rtl' : 'ltr'"
              :class="isRTL ? 'text-right' : 'text-left'"
              class="pb-1.5 xl:pb-2 text-sm font-medium leading-normal text-[#6B7280]"
            >
              <span
                :class="
                  validationErrors.trustee
                    ? 'text-[#FF3B30]'
                    : 'text-[#6B7280]'
                "
              >
                *
              </span>
              {{ t('loanForm.fields.trustee') }}
            </p>

            <div class="relative">
              <!-- Search Icon -->
              <span
                :class="[
                  'pointer-events-none absolute inset-y-0 flex items-center text-[#6B7280]',
                  isRTL ? 'right-0 pr-4' : 'left-0 pl-4',
                ]"
              >
                <svg
                  class="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.35-4.35" />
                </svg>
              </span>

              <!-- Trustee search input -->
              <input
                ref="trusteeInputRef"
                :value="trusteeSearchQuery"
                type="text"
                :dir="isRTL ? 'rtl' : 'ltr'"
                :class="[
                  'form-input flex h-11 xl:h-12 w-full min-w-0 resize-none overflow-hidden rounded-lg border',
                  'bg-white text-base font-normal leading-normal text-black placeholder:text-[#6B7280]',
                  'focus:outline-0 focus:ring-2',
                  isRTL ? 'pr-10 pl-4' : 'pl-10 pr-4',
                  validationErrors.trustee
                    ? 'border-[#FF3B30] focus:border-[#FF3B30] focus:ring-[#FF3B30]/20'
                    : 'border-[#E5E5EA] focus:border-[#007AFF] focus:ring-[#007AFF]/20',
                ]"
                :placeholder="t('loanForm.fields.trusteePlaceholder')"
                @input="onTrusteeInputChange(($event.target as HTMLInputElement).value)"
                @focus="onTrusteeInputFocus"
                @blur="onTrusteeInputBlur"
                @keydown="onTrusteeKeydown"
              />

              <!-- Trustees loading spinner -->
              <div
                v-if="trusteesLoading"
                :class="[
                  'pointer-events-none absolute inset-y-0 flex items-center',
                  isRTL ? 'left-0 pl-4' : 'right-0 pr-4',
                ]"
              >
                <div
                  class="w-4 h-4 border-2 border-[#007AFF] border-t-transparent rounded-full animate-spin"
                ></div>
              </div>

              <!-- Trustees dropdown -->
              <div
                v-if="showTrusteeDropdown && !borrower.trustee_id"
                class="absolute top-full left-0 right-0 mt-1 bg-white border border-[#E5E5EA] rounded-lg shadow-lg z-20 max-h-40 overflow-y-auto"
              >
                <div
                  v-if="trusteesLoading"
                  class="px-4 py-3 text-center text-sm text-[#6B7280]"
                >
                  {{ t('loanForm.messages.loadingTrustees') }}
                </div>

                <template v-else>
                  <button
                    v-for="(trustee, index) in filteredTrustees"
                    :key="trustee.id"
                    @click.prevent="selectTrustee(trustee)"
                    @mousedown.prevent
                    type="button"
                    :class="[
                      'w-full px-4 py-2.5 text-sm border-b border-[#E5E5EA] last:border-b-0 transition-colors',
                      index === highlightedTrusteeIndex
                        ? 'bg-[#007AFF]/10'
                        : 'hover:bg-[#007AFF]/10',
                    ]"
                    :dir="isRTL ? 'rtl' : 'ltr'"
                  >
                    <p
                      class="font-medium text-black"
                      :class="isRTL ? 'text-right' : 'text-left'"
                    >
                      {{ trustee.label }}
                    </p>
                  </button>

                  <div
                    v-if="filteredTrustees.length === 0"
                    class="px-4 py-3 text-center text-sm text-[#6B7280]"
                  >
                    {{ t('loanForm.messages.noTrustees') }}
                  </div>
                </template>
              </div>
            </div>

            <!-- Selected trustee display -->
            <div
              v-if="borrower.trustee_id"
              class="mt-2 p-3 bg-[#007AFF]/5 rounded-lg border border-[#007AFF]/20 flex items-center justify-between"
            >
              <p class="text-sm font-medium text-black">
                {{ borrower.trustee_name }}
              </p>
              <button
                @click="
                  (borrower.trustee_id = '');
                  (borrower.trustee_name = '');
                  (trusteeSearchQuery = '');
                "
                type="button"
                class="text-[#6B7280] hover:text-[#FF3B30] transition-colors"
              >
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <!-- Trustee validation error -->
            <p
              v-if="validationErrors.trustee && fieldErrorMessages.trustee"
              class="mt-1 text-xs text-[#FF3B30]"
            >
              {{ fieldErrorMessages.trustee }}
            </p>

            <!-- Trustees loading error -->
            <p
              v-if="trusteesErrorMessage"
              class="mt-1 text-xs text-[#FF3B30]"
            >
              {{ trusteesErrorMessage }}
            </p>
          </label>
        </FormCard>

        <!-- Loan Details Card -->
        <FormCard
          :title="t('loanForm.sections.loan')"
          :badge="t('loanForm.badges.loan')"
        >
          <!-- Loan Type -->
          <div class="flex flex-col">
            <p
              :dir="isRTL ? 'rtl' : 'ltr'"
              :class="isRTL ? 'text-right' : 'text-left'"
              class="pb-1.5 xl:pb-2 text-sm font-medium leading-normal text-[#6B7280]"
            >
              <span class="text-[#007AFF]">*</span>
              {{ t('loanForm.fields.loanType') }}
            </p>

            <select
              v-model="loan.loan_type"
              :dir="isRTL ? 'rtl' : 'ltr'"
              class="h-11 xl:h-12 w-full rounded-lg border border-[#E5E5EA] bg-white px-4 text-base focus:outline-0 focus:ring-2 focus:border-[#007AFF] focus:ring-[#007AFF]/20"
            >
              <option value="checks">{{ t('loanForm.loanTypes.checks') }}</option>
              <option value="standing_order">{{ t('loanForm.loanTypes.standingOrder') }}</option>
            </select>
          </div>

          <!-- Loan amount -->
          <FormInput
            ref="amountRef"
            v-model="loan.amount"
            :label="t('loanForm.fields.amount')"
            :placeholder="t('loanForm.fields.amountPlaceholder')"
            type="number"
            icon="dollar"
            :isRTL="isRTL"
            :required="true"
            :hasError="validationErrors.amount"
            :errorMessage="fieldErrorMessages.amount"
            min="0"
            step="0.01"
            @keydown="handleFieldKeydown('amount', $event)"
            @input="clearFieldError('amount')"
          />

          <div class="grid grid-cols-2 gap-3 xl:gap-4">
            <!-- Start date -->
            <FormDatePicker
              ref="datePickerRef"
              v-model="loan.start_date"
              :label="t('loanForm.fields.startDate')"
              :placeholder="t('loanForm.fields.startDatePlaceholder')"
              :isRTL="isRTL"
              :required="true"
              :hasError="validationErrors.start_date"
              :errorMessage="fieldErrorMessages.start_date"
              :locale="formLocale"
              @keydown="handleFieldKeydown('startDate', $event)"
            />

            <!-- Number of payments -->
            <FormInput
              ref="numPaymentsRef"
              v-model="loan.num_payments"
              :label="t('loanForm.fields.numPayments')"
              :placeholder="t('loanForm.fields.numPaymentsPlaceholder')"
              type="number"
              :isRTL="isRTL"
              :required="true"
              :hasError="validationErrors.num_payments"
              :errorMessage="fieldErrorMessages.num_payments"
              min="1"
              @keydown="handleFieldKeydown('numPayments', $event)"
              @input="clearFieldError('num_payments')"
            />
          </div>
        </FormCard>

        <!-- File Upload Card -->
        <div class="flex flex-col lg:col-span-2 xl:col-span-1">
          <FormCard
            :title="t('loanForm.sections.file')"
            :badge="t('loanForm.badges.file')"
            class="flex-1 flex flex-col"
          >
            <div class="flex-1 flex items-center justify-center">
              <!-- Initial upload state -->
              <label
                v-if="!formFile && !fileError"
                class="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-[#007AFF]/50 bg-[#007AFF]/5 p-6 xl:p-8 text-center text-[#007AFF] transition-colors hover:border-[#007AFF] hover:bg-[#007AFF]/10 w-full"
              >
                <div
                  class="flex size-10 items-center justify-center rounded-full bg-[#007AFF]/10"
                >
                  <svg
                    class="w-5 h-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="16 16 12 12 8 16" />
                    <line x1="12" y1="12" x2="12" y2="21" />
                    <path
                      d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"
                    />
                  </svg>
                </div>
                <p class="mt-3 font-medium text-sm xl:text-base">
                  <span class="text-[#007AFF]">*</span>
                  {{ t('loanForm.fields.signedForm') }}
                </p>
                <p class="mt-1 text-xs opacity-80">
                  {{ t('loanForm.messages.fileNotSelected') }}
                </p>
                <input
                  ref="fileInputRef"
                  type="file"
                  class="sr-only"
                  @change="onFileChange"
                  @keydown="handleFieldKeydown('file', $event)"
                />
              </label>

              <!-- Error state when file is required -->
              <div v-if="!formFile && fileError" class="space-y-2 w-full">
                <label
                  class="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-[#FF3B30] bg-[#FF3B30]/5 p-6 xl:p-8 text-center text-[#FF3B30] transition-colors hover:border-[#FF3B30]/80 hover:bg-[#FF3B30]/10"
                >
                  <div
                    class="flex size-10 items-center justify-center rounded-full bg-[#FF3B30]/10"
                  >
                    <svg
                      class="w-5 h-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <polyline points="16 16 12 12 8 16" />
                      <line x1="12" y1="12" x2="12" y2="21" />
                      <path
                        d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"
                      />
                    </svg>
                  </div>
                  <p class="mt-3 font-medium text-sm xl:text-base">
                    <span class="text-[#FF3B30]">*</span>
                    {{ t('loanForm.messages.uploadFailed') }}
                  </p>
                  <p class="mt-1 text-xs opacity-80">
                    {{ t('loanForm.messages.fileNotSelected') }}
                  </p>
                  <input
                    ref="fileInputRef"
                    type="file"
                    class="sr-only"
                    @change="onFileChange"
                    @keydown="handleFieldKeydown('file', $event)"
                  />
                </label>
                <p class="px-1 text-xs text-[#FF3B30]">
                  {{ t('loanForm.messages.fileRequired') }}
                </p>
              </div>

              <!-- File uploaded state -->
              <div
                v-if="formFile"
                class="flex items-center gap-3 rounded-xl border border-[#34C759] bg-[#34C759]/5 p-4 text-[#34C759] transition-colors hover:bg-[#34C759]/10 w-full"
              >
                <svg
                  class="w-5 h-5 flex-shrink-0"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate">
                    {{ formFile.name }}
                  </p>
                  <p class="text-xs opacity-80">
                    {{ (formFile.size / 1024 / 1024).toFixed(2) }} MB
                  </p>
                </div>
                <button
                  @click="formFile = null"
                  type="button"
                  class="flex size-7 flex-shrink-0 items-center justify-center rounded-full text-[#6B7280] hover:bg:black/10 transition-colors"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </FormCard>
        </div>
      </div>
    </div>

    <!-- Footer action buttons -->
    <template #footer>
      <div class="flex items-center gap-3">
        <!-- Reset form button -->
        <button
          @click="resetForm"
          :disabled="loading"
          :title="t('loanForm.buttons.clearForm')"
          class="flex size-12 xl:size-14 items-center justify-center rounded-xl bg-white border border-[#E5E5EA] 
                 text-[#6B7280] transition-colors hover:bg-gray-50 hover:border-[#FF3B30]/30 hover:text-[#FF3B30]
                 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <svg
            class="w-5 xl:w-6 h-5 xl:h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>

        <!-- Submit form button -->
        <button
          @click="submit"
          :disabled="loading"
          class="h-12 xl:h-14 flex-1 rounded-xl bg-[#007AFF] text-base font-semibold text-white shadow-lg 
                 shadow-[#007AFF]/20 transition-colors hover:bg-[#007AFF]/90 
                 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {{
            loading
              ? t('loanForm.buttons.submitting')
              : t('loanForm.buttons.submit')
          }}
        </button>
      </div>
    </template>
  </AppLayout>
</template>


<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
