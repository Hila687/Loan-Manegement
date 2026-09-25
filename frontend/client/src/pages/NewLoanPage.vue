<script setup lang="ts">
import {
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { useRouter } from "vue-router";

import { useLocale } from "../composables/useLocale";
import { useFormValidation } from "../composables/useFormValidation";
import { useFormFields } from "../composables/useFormFields";

import AppLayout from "../components/AppLayout.vue";
import FormCard from "../components/FormCard.vue";
import FormInput from "../components/FormInput.vue";
import FormDatePicker from "../components/FormDatePicker.vue";
import LoanDocumentUpload from "../components/LoanDocumentUpload.vue";
import TrusteePicker from "../components/TrusteePicker.vue";

import api from "../services/api";


const { t, locale, isRTL } = useLocale();

const router = useRouter();

const formLocale = computed<"he" | "en" | "es">(() =>
  locale.value === "he" ? "he" : locale.value === "es" ? "es" : "en"
);

const {
  validationErrors,
  fieldErrorMessages,
  clearFieldError,
  setFieldError,
  clearAllErrors,
} = useFormValidation();

const {
  registerField,
  focusNextField,
  focusPreviousField,
} = useFormFields();


const borrower = ref({
  first_name: "",
  last_name: "",
  id_number: "",
  phone: "",
  email: "",
  address: "",
  trustee_id: "",
  trustee_name: "",
});


const loan = ref({
  loan_type: "checks" as
    | "checks"
    | "standing_order",
  amount: "",
  start_date: "",
  num_payments: "",
});


type TrusteeOption = {
  id: string;
  name: string;
  community?: string;
};


type BorrowerCredentials = {
  username: string;
  temporary_password: string;
};


const MAX_FILE_SIZE =
  10 * 1024 * 1024;

const ALLOWED_FILE_TYPES =
  new Set([
    "application/pdf",
    "image/jpeg",
    "image/png",
  ]);

const ALLOWED_FILE_EXTENSIONS =
  new Set([
    "pdf",
    "jpg",
    "jpeg",
    "png",
  ]);


const formFile =
  ref<File | null>(null);

const fileError =
  ref(false);

const standingOrderFormFile =
  ref<File | null>(null);

const standingOrderFileError =
  ref(false);


const loading =
  ref(false);

const error =
  ref<string | null>(null);

const errorTimeout =
  ref<ReturnType<
    typeof setTimeout
  > | null>(null);


const trustees =
  ref<TrusteeOption[]>([]);

const trusteesLoading =
  ref(false);

const trusteesErrorMessage =
  ref("");


const showSuccessModal =
  ref(false);

const createdLoanId =
  ref("");

const borrowerCredentials =
  ref<BorrowerCredentials | null>(
    null
  );

const credentialsCopied =
  ref(false);


// Component refs use any because these components expose a focus method.
const borrowerFirstNameRef =
  ref<any>(null);

const borrowerLastNameRef =
  ref<any>(null);

const borrowerIdNumberRef =
  ref<any>(null);

const borrowerEmailRef =
  ref<any>(null);

const borrowerPhoneRef =
  ref<any>(null);

const borrowerAddressRef =
  ref<any>(null);

const amountRef =
  ref<any>(null);

const numPaymentsRef =
  ref<any>(null);

const datePickerRef =
  ref<any>(null);


// TrusteePicker exposes a focus method.
const trusteeInputRef =
  ref<any>(null);


const fields = [
  {
    name: "borrowerFirstName",
    ref: borrowerFirstNameRef,
    order: 0,
  },
  {
    name: "borrowerLastName",
    ref: borrowerLastNameRef,
    order: 1,
  },
  {
    name: "borrowerIdNumber",
    ref: borrowerIdNumberRef,
    order: 2,
  },
  {
    name: "borrowerPhone",
    ref: borrowerPhoneRef,
    order: 3,
  },
  {
    name: "borrowerEmail",
    ref: borrowerEmailRef,
    order: 4,
  },
  {
    name: "borrowerAddress",
    ref: borrowerAddressRef,
    order: 5,
  },
  {
    name: "trustee",
    ref: trusteeInputRef,
    order: 6,
  },
  {
    name: "amount",
    ref: amountRef,
    order: 7,
  },
  {
    name: "startDate",
    ref: datePickerRef,
    order: 8,
  },
  {
    name: "numPayments",
    ref: numPaymentsRef,
    order: 9,
  },
];


onMounted(() => {
  fields.forEach((field) => {
    registerField(
      field.name,
      field.ref,
      field.order
    );
  });

  fetchTrustees();
});


onBeforeUnmount(() => {
  if (errorTimeout.value) {
    clearTimeout(
      errorTimeout.value
    );
  }
});


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

  const username =
    String(
      user.username ||
      raw?.username ||
      ""
    ).trim();

  const community =
    String(
      raw?.community || ""
    ).trim();

  const displayName =
    fullName ||
    username ||
    "Unknown trustee";

  return {
    id: String(
      raw?.trustee_id ||
      raw?.id ||
      ""
    ),
    name: displayName,
    community,
  };
}


function isValidPhone(
  phone: string
): boolean {
  const cleanPhone =
    phone
      .replace(
        /[\s-]/g,
        ""
      )
      .trim();

  return /^\+?\d{7,15}$/.test(
    cleanPhone
  );
}


function isValidEmail(
  email: string
): boolean {
  if (!email.trim()) {
    return true;
  }

  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    email.trim()
  );
}


function onPhoneInput(
  event: Event
) {
  const target =
    event.target;

  if (
    !(
      target instanceof
      HTMLInputElement
    )
  ) {
    return;
  }

  const sanitized =
    target.value.replace(
      /[^\d+\-\s]/g,
      ""
    );

  target.value =
    sanitized;

  borrower.value.phone =
    sanitized;

  clearFieldError(
    "phone"
  );
}


function handleFieldKeydown(
  fieldName: string,
  event: KeyboardEvent
) {
  const key =
    event.key;

  if (
    key !== "Enter" &&
    key !== "ArrowDown" &&
    key !== "ArrowUp"
  ) {
    return;
  }

  if (
    key === "Enter" ||
    key === "ArrowDown"
  ) {
    event.preventDefault();

    focusNextField(
      fieldName
    );

    return;
  }

  event.preventDefault();

  focusPreviousField(
    fieldName
  );
}


async function fetchTrustees() {
  trusteesLoading.value =
    true;

  trusteesErrorMessage.value =
    "";

  try {
    const response =
      await api.get(
        "/trustees/"
      );

    const rawList =
      Array.isArray(
        response.data
      )
        ? response.data
        : [];

    trustees.value =
      rawList
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
            trustee:
              TrusteeOption
          ) =>
            Boolean(
              trustee.id
            )
        );
  } catch {
    trustees.value = [];

    trusteesErrorMessage.value =
      t(
        "loanForm.messages.trusteesLoadError"
      );
  } finally {
    trusteesLoading.value =
      false;
  }
}


function onTrusteePickerSelected(
  trustee: TrusteeOption | null
): void {
  borrower.value.trustee_id =
    trustee?.id || "";

  borrower.value.trustee_name =
    trustee?.name || "";

  clearFieldError(
    "trustee"
  );
}


function getFileExtension(
  fileName: string
): string {
  const parts =
    fileName
      .toLowerCase()
      .split(".");

  return parts.length > 1
    ? parts.pop() || ""
    : "";
}


function validateSelectedFile(
  file: File
): string | null {
  if (
    file.size <= 0
  ) {
    return t(
      "loanForm.messages.uploadFailed"
    );
  }

  if (
    file.size >
    MAX_FILE_SIZE
  ) {
    return locale.value ===
      "he"
      ? "גודל הקובץ המקסימלי הוא 10MB"
      : "The maximum file size is 10MB";
  }

  const extension =
    getFileExtension(
      file.name
    );

  if (
    !ALLOWED_FILE_EXTENSIONS.has(
      extension
    )
  ) {
    return locale.value ===
      "he"
      ? "ניתן להעלות רק קובצי PDF, JPG או PNG"
      : "Only PDF, JPG or PNG files are allowed";
  }

  if (
    file.type &&
    !ALLOWED_FILE_TYPES.has(
      file.type
    )
  ) {
    return locale.value ===
      "he"
      ? "סוג הקובץ אינו נתמך"
      : "Unsupported file type";
  }

  return null;
}


function selectLoanAgreementFile(
  file: File
) {
  const message =
    validateSelectedFile(
      file
    );

  if (message) {
    formFile.value =
      null;

    fileError.value =
      true;

    setFieldError(
      "file",
      message
    );

    return;
  }

  formFile.value =
    file;

  fileError.value =
    false;

  clearFieldError(
    "file"
  );
}


function selectStandingOrderFile(
  file: File
) {
  const message =
    validateSelectedFile(
      file
    );

  if (message) {
    standingOrderFormFile.value =
      null;

    standingOrderFileError.value =
      true;

    setFieldError(
      "standing_order_form_file",
      message
    );

    return;
  }

  standingOrderFormFile.value =
    file;

  standingOrderFileError.value =
    false;

  clearFieldError(
    "standing_order_form_file"
  );
}


function removeLoanAgreementFile() {
  formFile.value =
    null;

  fileError.value =
    false;

  clearFieldError(
    "file"
  );
}


function removeStandingOrderFile() {
  standingOrderFormFile.value =
    null;

  standingOrderFileError.value =
    false;

  clearFieldError(
    "standing_order_form_file"
  );
}


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

  loan.value = {
    loan_type: "checks",
    amount: "",
    start_date: "",
    num_payments: "",
  };

  formFile.value =
    null;

  fileError.value =
    false;

  standingOrderFormFile.value =
    null;

  standingOrderFileError.value =
    false;

  error.value =
    null;

  clearAllErrors();
}


function showErrorMessage() {
  if (
    errorTimeout.value
  ) {
    clearTimeout(
      errorTimeout.value
    );
  }

  errorTimeout.value =
    setTimeout(() => {
      error.value =
        null;
    }, 3000);
}


function normalizeBackendMessage(
  value: unknown
): string | null {
  if (
    typeof value ===
    "string"
  ) {
    return value;
  }

  if (
    Array.isArray(value) &&
    value.length > 0
  ) {
    return normalizeBackendMessage(
      value[0]
    );
  }

  return null;
}


function setErrorsFromBackend(
  data: unknown
) {
  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data)
  ) {
    return;
  }

  const root =
    data as Record<
      string,
      unknown
    >;

  const borrowerErrors =
    root.borrower;

  if (
    borrowerErrors &&
    typeof borrowerErrors ===
      "object" &&
    !Array.isArray(
      borrowerErrors
    )
  ) {
    for (
      const [
        field,
        value,
      ] of Object.entries(
        borrowerErrors as Record<
          string,
          unknown
        >
      )
    ) {
      const message =
        normalizeBackendMessage(
          value
        );

      if (message) {
        setFieldError(
          field,
          message
        );
      }
    }
  }

  const loanErrors =
    root.loan;

  if (
    loanErrors &&
    typeof loanErrors ===
      "object" &&
    !Array.isArray(
      loanErrors
    )
  ) {
    for (
      const [
        field,
        value,
      ] of Object.entries(
        loanErrors as Record<
          string,
          unknown
        >
      )
    ) {
      const message =
        normalizeBackendMessage(
          value
        );

      if (message) {
        setFieldError(
          field,
          message
        );
      }
    }
  }

  const trusteeMessage =
    normalizeBackendMessage(
      root.trustee_id
    );

  if (
    trusteeMessage
  ) {
    setFieldError(
      "trustee",
      trusteeMessage
    );
  }

  const fileMessage =
    normalizeBackendMessage(
      root.form_file
    );

  if (
    fileMessage
  ) {
    fileError.value =
      true;

    setFieldError(
      "file",
      fileMessage
    );
  }

  const standingOrderFileMessage =
    normalizeBackendMessage(
      root.standing_order_form_file
    );

  if (
    standingOrderFileMessage
  ) {
    standingOrderFileError.value =
      true;

    setFieldError(
      "standing_order_form_file",
      standingOrderFileMessage
    );
  }
}


async function submit() {
  clearAllErrors();

  error.value =
    null;

  fileError.value =
    false;

  standingOrderFileError.value =
    false;

  let hasErrors =
    false;


  if (
    !borrower.value
      .first_name
      .trim()
  ) {
    setFieldError(
      "first_name",
      t(
        "loanForm.messages.nameRequired"
      )
    );

    hasErrors =
      true;
  }


  if (
    !borrower.value
      .last_name
      .trim()
  ) {
    setFieldError(
      "last_name",
      t(
        "loanForm.messages.nameRequired"
      )
    );

    hasErrors =
      true;
  }


  if (
    !borrower.value
      .id_number
      .trim()
  ) {
    setFieldError(
      "id_number",
      t(
        "loanForm.messages.idNumberRequired"
      )
    );

    hasErrors =
      true;
  }


  if (
    !borrower.value.phone ||
    !isValidPhone(
      borrower.value.phone
    )
  ) {
    setFieldError(
      "phone",
      t(
        "loanForm.messages.phoneInvalid"
      )
    );

    hasErrors =
      true;
  }


  if (
    !isValidEmail(
      borrower.value.email
    )
  ) {
    setFieldError(
      "email",
      locale.value ===
        "he"
        ? "כתובת האימייל אינה תקינה"
        : "Invalid email address"
    );

    hasErrors =
      true;
  }


  if (
    !borrower.value
      .address
      .trim()
  ) {
    setFieldError(
      "address",
      locale.value ===
        "he"
        ? "כתובת היא שדה חובה"
        : "Address is required"
    );

    hasErrors =
      true;
  }


  if (
    !borrower.value
      .trustee_id
  ) {
    setFieldError(
      "trustee",
      locale.value ===
        "he"
        ? "יש לבחור נאמן"
        : "Please select a trustee"
    );

    hasErrors =
      true;
  }


  const amount =
    Number(
      loan.value.amount
    );

  if (
    !Number.isFinite(
      amount
    ) ||
    amount <= 0
  ) {
    setFieldError(
      "amount",
      t(
        "loanForm.messages.amountInvalid"
      )
    );

    hasErrors =
      true;
  }


  if (
    !loan.value
      .start_date
  ) {
    setFieldError(
      "start_date",
      t(
        "loanForm.messages.startDateInvalid"
      )
    );

    hasErrors =
      true;
  }


  const numPayments =
    Number(
      loan.value
        .num_payments
    );

  if (
    !Number.isInteger(
      numPayments
    ) ||
    numPayments < 1
  ) {
    setFieldError(
      "num_payments",
      t(
        "loanForm.messages.numPaymentsInvalid"
      )
    );

    hasErrors =
      true;
  }


  const selectedFile =
    formFile.value;

  if (
    !selectedFile
  ) {
    fileError.value =
      true;

    setFieldError(
      "file",
      t(
        "loanForm.messages.fileRequired"
      )
    );

    hasErrors =
      true;
  } else {
    const message =
      validateSelectedFile(
        selectedFile
      );

    if (message) {
      fileError.value =
        true;

      setFieldError(
        "file",
        message
      );

      hasErrors =
        true;
    }
  }


  if (
    loan.value.loan_type ===
      "standing_order"
  ) {
    const standingOrderFile =
      standingOrderFormFile.value;

    if (
      !standingOrderFile
    ) {
      standingOrderFileError.value =
        true;

      setFieldError(
        "standing_order_form_file",
        locale.value ===
          "he"
          ? "יש להעלות טופס אישור הוראת קבע"
          : "Standing order authorization form is required"
      );

      hasErrors =
        true;
    } else {
      const message =
        validateSelectedFile(
          standingOrderFile
        );

      if (message) {
        standingOrderFileError.value =
          true;

        setFieldError(
          "standing_order_form_file",
          message
        );

        hasErrors =
          true;
      }
    }
  }


  if (
    hasErrors
  ) {
    error.value =
      t(
        "loanForm.messages.requiredFieldsError"
      );

    showErrorMessage();

    return;
  }


  if (
    !selectedFile
  ) {
    return;
  }


  loading.value =
    true;

  try {
    const payload = {
      loan_type:
        loan.value.loan_type,

      borrower: {
        id_number:
          borrower.value
            .id_number
            .trim(),

        first_name:
          borrower.value
            .first_name
            .trim(),

        last_name:
          borrower.value
            .last_name
            .trim(),

        phone:
          borrower.value
            .phone
            .trim(),

        email:
          borrower.value
            .email
            .trim(),

        address:
          borrower.value
            .address
            .trim(),
      },

      loan: {
        amount,

        num_payments:
          numPayments,

        start_date:
          loan.value
            .start_date,
      },

      trustee_id:
        borrower.value
          .trustee_id,
    };


    const formData =
      new FormData();

    formData.append(
      "payload",
      JSON.stringify(
        payload
      )
    );

    formData.append(
      "form_file",
      selectedFile
    );


    if (
      loan.value.loan_type ===
        "standing_order" &&
      standingOrderFormFile.value
    ) {
      formData.append(
        "standing_order_form_file",
        standingOrderFormFile.value
      );
    }


    const response =
      await api.post(
        "/loans/",
        formData
      );


    createdLoanId.value =
      String(
        response.data
          ?.loan_id ||
          ""
      );


    const credentials =
      response.data
        ?.borrower_credentials;


    borrowerCredentials.value =
      credentials
        ? {
            username:
              String(
                credentials
                  .username ||
                  ""
              ),

            temporary_password:
              String(
                credentials
                  .temporary_password ||
                  ""
              ),
          }
        : null;


    credentialsCopied.value =
      false;

    showSuccessModal.value =
      true;
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
        t(
          "loanForm.messages.requiredFieldsError"
        );
    } else if (
      status === 413
    ) {
      error.value =
        locale.value ===
          "he"
          ? "אחד הקבצים שהועלו גדול מדי"
          : "One of the uploaded files is too large";
    } else {
      error.value =
        data?.detail ||
        t(
          "loanForm.messages.genericError"
        );
    }

    showErrorMessage();
  } finally {
    loading.value =
      false;
  }
}


async function copyCredentials() {
  if (
    !borrowerCredentials.value
  ) {
    return;
  }

  const text =
    `Username: ${borrowerCredentials.value.username}\n` +
    `Temporary password: ${borrowerCredentials.value.temporary_password}`;

  try {
    await navigator
      .clipboard
      .writeText(
        text
      );

    credentialsCopied.value =
      true;
  } catch {
    credentialsCopied.value =
      false;
  }
}


async function finishSuccessFlow() {
  showSuccessModal.value =
    false;

  borrowerCredentials.value =
    null;

  const loanId =
    createdLoanId.value;

  resetForm();

  if (loanId) {
    await router.push(
      `/loans/${loanId}/details`
    );

    return;
  }

  await router.push(
    "/loans"
  );
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
        class="fixed top-4 left-1/2 z-50 -translate-x-1/2 rounded-lg border border-brand bg-white px-6 py-4 shadow-lg"
      >
        <p
          class="text-sm font-medium text-brand"
        >
          {{ error }}
        </p>
      </div>
    </transition>


    <div
      class="flex h-full flex-col gap-6 xl:gap-5"
    >
      <section
        class="rounded-2xl border border-line bg-white p-4 shadow-sm sm:p-5"
        :dir="isRTL ? 'rtl' : 'ltr'"
      >
        <div
          class="max-w-2xl"
          :class="isRTL ? 'ml-auto' : 'mr-auto'"
        >
          <TrusteePicker
            ref="trusteeInputRef"
            v-model="borrower.trustee_id"
            :options="trustees"
            :label="t('loanForm.fields.trustee')"
            :placeholder="
              locale === 'he'
                ? 'חיפוש נאמן לפי שם'
                : 'Search trustee by name'
            "
            :error-message="
              fieldErrorMessages.trustee || trusteesErrorMessage
            "
            :loading="trusteesLoading"
            :required="true"
            :isRTL="isRTL"
            :locale="formLocale"
            @selected="onTrusteePickerSelected"
          />
        </div>
      </section>

      <div
        class="grid grid-cols-1 gap-6 auto-rows-max lg:grid-cols-2 xl:grid-cols-3 xl:gap-5"
      >
        <!-- Borrower Details Card -->
        <FormCard
          :title="
            t(
              'loanForm.sections.borrower'
            )
          "
          :badge="
            t(
              'loanForm.badges.borrower'
            )
          "
        >
          <FormInput
            ref="borrowerFirstNameRef"
            v-model="
              borrower.first_name
            "
            :label="
              t(
                'loanForm.fields.borrowerFirstName'
              )
            "
            :placeholder="
              t(
                'loanForm.fields.borrowerFirstNamePlaceholder'
              )
            "
            icon="user"
            :isRTL="isRTL"
            :required="true"
            :hasError="
              validationErrors.first_name
            "
            :errorMessage="
              fieldErrorMessages.first_name
            "
            @keydown="
              handleFieldKeydown(
                'borrowerFirstName',
                $event
              )
            "
            @input="
              clearFieldError(
                'first_name'
              )
            "
          />


          <FormInput
            ref="borrowerLastNameRef"
            v-model="
              borrower.last_name
            "
            :label="
              t(
                'loanForm.fields.borrowerLastName'
              )
            "
            :placeholder="
              t(
                'loanForm.fields.borrowerLastNamePlaceholder'
              )
            "
            icon="user"
            :isRTL="isRTL"
            :required="true"
            :hasError="
              validationErrors.last_name
            "
            :errorMessage="
              fieldErrorMessages.last_name
            "
            @keydown="
              handleFieldKeydown(
                'borrowerLastName',
                $event
              )
            "
            @input="
              clearFieldError(
                'last_name'
              )
            "
          />


          <FormInput
            ref="borrowerIdNumberRef"
            v-model="
              borrower.id_number
            "
            :label="
              t(
                'loanForm.fields.borrowerIdNumber'
              )
            "
            :placeholder="
              t(
                'loanForm.fields.borrowerIdNumberPlaceholder'
              )
            "
            type="text"
            icon="user"
            :isRTL="isRTL"
            :required="true"
            :hasError="
              validationErrors.id_number
            "
            :errorMessage="
              fieldErrorMessages.id_number
            "
            @keydown="
              handleFieldKeydown(
                'borrowerIdNumber',
                $event
              )
            "
            @input="
              clearFieldError(
                'id_number'
              )
            "
          />


          <FormInput
            ref="borrowerPhoneRef"
            v-model="
              borrower.phone
            "
            :label="
              t(
                'loanForm.fields.borrowerPhone'
              )
            "
            :placeholder="
              t(
                'loanForm.fields.borrowerPhonePlaceholder'
              )
            "
            type="tel"
            icon="phone"
            :isRTL="isRTL"
            :required="true"
            :hasError="
              validationErrors.phone
            "
            :errorMessage="
              fieldErrorMessages.phone
            "
            inputMode="tel"
            @input="
              onPhoneInput
            "
            @keydown="
              handleFieldKeydown(
                'borrowerPhone',
                $event
              )
            "
          />


          <FormInput
            ref="borrowerEmailRef"
            v-model="
              borrower.email
            "
            :label="
              t(
                'loanForm.fields.borrowerEmail'
              )
            "
            :placeholder="
              t(
                'loanForm.fields.borrowerEmailPlaceholder'
              )
            "
            type="email"
            :isRTL="isRTL"
            :required="false"
            :hasError="
              validationErrors.email
            "
            :errorMessage="
              fieldErrorMessages.email
            "
            @keydown="
              handleFieldKeydown(
                'borrowerEmail',
                $event
              )
            "
            @input="
              clearFieldError(
                'email'
              )
            "
          />


          <FormInput
            ref="borrowerAddressRef"
            v-model="
              borrower.address
            "
            :label="
              t(
                'loanForm.fields.borrowerAddress'
              )
            "
            :placeholder="
              t(
                'loanForm.fields.borrowerAddressPlaceholder'
              )
            "
            icon="building"
            :isRTL="isRTL"
            :required="true"
            :hasError="
              validationErrors.address
            "
            :errorMessage="
              fieldErrorMessages.address
            "
            @keydown="
              handleFieldKeydown(
                'borrowerAddress',
                $event
              )
            "
            @input="
              clearFieldError(
                'address'
              )
            "
          />

        </FormCard>


        <!-- Loan Details Card -->
        <FormCard
          :title="
            t(
              'loanForm.sections.loan'
            )
          "
          :badge="
            t(
              'loanForm.badges.loan'
            )
          "
        >
          <div
            class="flex flex-col"
          >
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
              class="pb-1.5 text-sm font-medium leading-normal text-muted xl:pb-2"
            >
              <span
                class="text-brand"
              >
                *
              </span>

              {{
                t(
                  "loanForm.fields.loanType"
                )
              }}
            </p>


            <select
              v-model="
                loan.loan_type
              "
              :dir="
                isRTL
                  ? 'rtl'
                  : 'ltr'
              "
              class="h-11 w-full rounded-lg border border-line bg-white px-4 text-base focus:border-brand focus:ring-2 focus:ring-brand/20 focus:outline-0 xl:h-12"
            >
              <option
                value="checks"
              >
                {{
                  t(
                    "loanForm.loanTypes.checks"
                  )
                }}
              </option>

              <option
                value="standing_order"
              >
                {{
                  t(
                    "loanForm.loanTypes.standingOrder"
                  )
                }}
              </option>
            </select>
          </div>


          <FormInput
            ref="amountRef"
            v-model="
              loan.amount
            "
            :label="
              t(
                'loanForm.fields.amount'
              )
            "
            :placeholder="
              t(
                'loanForm.fields.amountPlaceholder'
              )
            "
            type="number"
            icon="dollar"
            :isRTL="isRTL"
            :required="true"
            :hasError="
              validationErrors.amount
            "
            :errorMessage="
              fieldErrorMessages.amount
            "
            inputMode="decimal"
            min="0.01"
            step="0.01"
            @keydown="
              handleFieldKeydown(
                'amount',
                $event
              )
            "
            @input="
              clearFieldError(
                'amount'
              )
            "
          />


          <div
            class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:gap-4"
          >
            <FormDatePicker
              ref="datePickerRef"
              v-model="
                loan.start_date
              "
              :label="
                t(
                  'loanForm.fields.startDate'
                )
              "
              :placeholder="
                t(
                  'loanForm.fields.startDatePlaceholder'
                )
              "
              :isRTL="isRTL"
              :required="true"
              :hasError="
                validationErrors.start_date
              "
              :errorMessage="
                fieldErrorMessages.start_date
              "
              :locale="
                formLocale
              "
              @keydown="
                handleFieldKeydown(
                  'startDate',
                  $event
                )
              "
            />


            <FormInput
              ref="numPaymentsRef"
              v-model="
                loan.num_payments
              "
              :label="
                t(
                  'loanForm.fields.numPayments'
                )
              "
              :placeholder="
                t(
                  'loanForm.fields.numPaymentsPlaceholder'
                )
              "
              type="number"
              :isRTL="isRTL"
              :required="true"
              :hasError="
                validationErrors.num_payments
              "
              :errorMessage="
                fieldErrorMessages.num_payments
              "
              inputMode="numeric"
              min="1"
              step="1"
              @keydown="
                handleFieldKeydown(
                  'numPayments',
                  $event
                )
              "
              @input="
                clearFieldError(
                  'num_payments'
                )
              "
            />
          </div>
        </FormCard>


        <!-- Loan Documents Card -->
        <div
          class="flex flex-col lg:col-span-2 xl:col-span-1"
        >
          <FormCard
            :title="
              locale === 'he'
                ? 'מסמכי הלוואה'
                : 'Loan Documents'
            "
            :badge="
              t(
                'loanForm.badges.file'
              )
            "
            class="flex flex-1 flex-col"
          >
            <div
              class="flex flex-col gap-5"
            >
              <LoanDocumentUpload
                :title="
                  locale === 'he'
                    ? 'שטר הלוואה'
                    : 'Loan Agreement'
                "
                :label="
                  locale === 'he'
                    ? 'שטר הלוואה חתום'
                    : 'Signed Loan Agreement'
                "
                :file="
                  formFile
                "
                :error-message="
                  fieldErrorMessages.file
                "
                :isRTL="
                  isRTL
                "
                @select="
                  selectLoanAgreementFile
                "
                @remove="
                  removeLoanAgreementFile
                "
              />


              <LoanDocumentUpload
                v-if="
                  loan.loan_type ===
                  'standing_order'
                "
                :title="
                  locale === 'he'
                    ? 'אישור הוראת קבע'
                    : 'Standing Order Authorization'
                "
                :label="
                  locale === 'he'
                    ? 'טופס אישור הוראת קבע'
                    : 'Standing Order Authorization Form'
                "
                :file="
                  standingOrderFormFile
                "
                :error-message="
                  fieldErrorMessages.standing_order_form_file
                "
                :isRTL="
                  isRTL
                "
                @select="
                  selectStandingOrderFile
                "
                @remove="
                  removeStandingOrderFile
                "
              />
            </div>
          </FormCard>
        </div>
      </div>
    </div>


    <!-- Footer action buttons -->
    <template #footer>
      <div
        class="flex items-center gap-3"
      >
        <button
          type="button"
          :disabled="
            loading
          "
          :title="
            t(
              'loanForm.buttons.clearForm'
            )
          "
          class="flex size-12 items-center justify-center rounded-xl border border-line bg-white text-muted transition-colors hover:border-danger/30 hover:bg-surface-muted hover:text-danger disabled:cursor-not-allowed disabled:opacity-50 xl:size-14"
          @click="
            resetForm
          "
        >
          <svg
            class="h-5 w-5 xl:h-6 xl:w-6"
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


        <button
          type="button"
          :disabled="
            loading
          "
          class="h-12 flex-1 rounded-xl bg-brand text-base font-semibold text-white shadow-lg shadow-brand/20 transition-colors hover:bg-brand/90 disabled:cursor-not-allowed disabled:bg-faint xl:h-14"
          @click="
            submit
          "
        >
          {{
            loading
              ? t(
                  "loanForm.buttons.submitting"
                )
              : t(
                  "loanForm.buttons.submit"
                )
          }}
        </button>
      </div>
    </template>


    <!-- Success modal -->
    <Teleport
      to="body"
    >
      <div
        v-if="
          showSuccessModal
        "
        class="fixed inset-0 z-[100] flex items-center justify-center bg-black/45 p-4 backdrop-blur-sm"
        :dir="
          isRTL
            ? 'rtl'
            : 'ltr'
        "
      >
        <div
          class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl"
        >
          <div
            class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-success/10 text-success"
          >
            <svg
              class="h-8 w-8"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2.5"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>


          <h2
            class="mt-4 text-center text-xl font-bold text-ink"
          >
            {{
              t(
                "loanForm.messages.success"
              )
            }}
          </h2>


          <p
            v-if="
              createdLoanId
            "
            class="mt-2 break-all text-center text-xs text-muted"
          >
            {{
              createdLoanId
            }}
          </p>


          <div
            v-if="
              borrowerCredentials
            "
            class="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4"
          >
            <p
              class="text-sm font-semibold text-amber-900"
            >
              {{
                locale === "he"
                  ? "פרטי כניסה זמניים ללווה"
                  : "Temporary borrower credentials"
              }}
            </p>


            <p
              class="mt-1 text-xs leading-5 text-amber-800"
            >
              {{
                locale === "he"
                  ? "יש למסור אותם ללווה בצורה מאובטחת. הסיסמה תוצג כאן פעם אחת בלבד."
                  : "Give these credentials to the borrower securely. The password is shown here only once."
              }}
            </p>


            <div
              class="mt-4 space-y-3"
            >
              <div>
                <p
                  class="text-xs text-muted"
                >
                  {{
                    locale === "he"
                      ? "שם משתמש"
                      : "Username"
                  }}
                </p>

                <p
                  class="mt-1 break-all rounded-lg bg-white px-3 py-2 font-mono text-sm text-ink"
                >
                  {{
                    borrowerCredentials.username
                  }}
                </p>
              </div>


              <div>
                <p
                  class="text-xs text-muted"
                >
                  {{
                    locale === "he"
                      ? "סיסמה זמנית"
                      : "Temporary password"
                  }}
                </p>

                <p
                  class="mt-1 break-all rounded-lg bg-white px-3 py-2 font-mono text-sm text-ink"
                >
                  {{
                    borrowerCredentials.temporary_password
                  }}
                </p>
              </div>
            </div>


            <button
              type="button"
              class="mt-4 w-full rounded-xl border border-amber-300 bg-white px-4 py-2.5 text-sm font-semibold text-amber-900 transition hover:bg-amber-100"
              @click="
                copyCredentials
              "
            >
              {{
                credentialsCopied
                  ? (
                      locale === "he"
                        ? "הועתק"
                        : "Copied"
                    )
                  : (
                      locale === "he"
                        ? "העתקת פרטים"
                        : "Copy credentials"
                    )
              }}
            </button>
          </div>


          <button
            type="button"
            class="mt-5 h-12 w-full rounded-xl bg-brand font-semibold text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep"
            @click="
              finishSuccessFlow
            "
          >
            {{
              locale === "he"
                ? "הצגת ההלוואה"
                : "View loan"
            }}
          </button>
        </div>
      </div>
    </Teleport>
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