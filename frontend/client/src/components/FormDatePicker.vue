<script setup lang="ts">
import { ref, computed, onMounted, watch, defineExpose, onBeforeUnmount } from "vue";
import flatpickr from "flatpickr";
import { Hebrew } from "flatpickr/dist/l10n/he";

interface Props {
  modelValue: string;
  label: string;
  placeholder: string;
  isRTL?: boolean;
  hasError?: boolean;
  errorMessage?: string;
  required?: boolean;
  locale?: "he" | "en";
}

const props = withDefaults(defineProps<Props>(), {
  isRTL: false,
  required: false,
  locale: "he",
});

const emit = defineEmits<{
  "update:modelValue": [value: string];
  keydown: [event: KeyboardEvent];
}>();

// Reference to the visible input
const dateInputRef = ref<HTMLInputElement | null>(null);

// Flatpickr instance
let datePickerInstance: any = null;

// Label helpers
const labelDir = computed(() => (props.isRTL ? "rtl" : "ltr"));
const labelAlign = computed(() => (props.isRTL ? "text-right" : "text-left"));
const iconDir = computed(() =>
  props.isRTL ? "left-0 pl-3" : "right-0 pr-3"
);

// Initialize flatpickr on mount
onMounted(() => {
  if (!dateInputRef.value) return;

  // Localize Hebrew strings
  flatpickr.localize(Hebrew);

  datePickerInstance = flatpickr(dateInputRef.value, {
    mode: "single",
    dateFormat: "Y-m-d",
    minDate: "today",
    locale: props.locale === "he" ? "he" : "en",
    onChange: (selectedDates: Date[]) => {
      if (selectedDates.length > 0) {
        const date = selectedDates[0];
        emit("update:modelValue", date.toISOString().split("T")[0]);
      }
    },
    onOpen: () => {
      const picker = document.querySelector(".flatpickr-calendar") as HTMLElement | null;
      if (picker && props.isRTL) {
        picker.style.left = "auto";
        picker.style.right = "0";
      }
    },
  });

  // If there is already a value, sync it into the picker
  if (props.modelValue && datePickerInstance) {
    datePickerInstance.setDate(props.modelValue, false);
  }
});

// Clean up instance
onBeforeUnmount(() => {
  if (datePickerInstance) {
    datePickerInstance.destroy();
    datePickerInstance = null;
  }
});

// Watch for external modelValue changes (for example resetForm)
watch(
  () => props.modelValue,
  (newValue) => {
    if (!datePickerInstance) return;
    if (!newValue) {
      datePickerInstance.clear();
    } else {
      datePickerInstance.setDate(newValue, false);
    }
  }
);

// Watch for locale change from parent
watch(
  () => props.locale,
  (newLocale) => {
    if (!datePickerInstance) return;
    datePickerInstance.set("locale", newLocale === "he" ? "he" : "en");
  }
);

// Expose focus so parent can focus this field via ref
function focus() {
  if (dateInputRef.value) {
    dateInputRef.value.focus();
  }
}

defineExpose({ focus });
</script>

<template>
  <label class="flex flex-col">
    <!-- Label -->
    <p
      :dir="labelDir"
      :class="labelAlign"
      class="pb-1.5 xl:pb-2 text-sm font-medium leading-normal text-[#6B7280]"
    >
      <span
        v-if="required"
        :class="hasError ? 'text-[#FF3B30]' : 'text-[#6B7280]'"
        >*</span
      >
      {{ label }}
    </p>

    <div class="relative">
      <!-- Date input -->
      <input
        ref="dateInputRef"
        type="text"
        :dir="isRTL ? 'rtl' : 'ltr'"
        :class="[
          'form-input flex h-11 xl:h-12 w-full min-w-0 resize-none overflow-hidden rounded-lg border',
          'bg-white px-3.5 text-base font-normal leading-normal text-black placeholder:text-[#6B7280]',
          'focus:outline-0 focus:ring-2 cursor-pointer',
          isRTL ? 'pr-10 pl-4' : 'pl-4 pr-10',
          hasError
            ? 'border-[#FF3B30] focus:border-[#FF3B30] focus:ring-[#FF3B30]/20'
            : 'border-[#E5E5EA] focus:border-[#007AFF] focus:ring-[#007AFF]/20',
        ]"
        :placeholder="placeholder"
        readonly
        @keydown="emit('keydown', $event)"
      />

      <!-- Calendar Icon -->
      <span
        :class="[
          'pointer-events-none absolute inset-y-0 flex items-center text-[#6B7280]',
          iconDir,
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
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
        </svg>
      </span>
    </div>

    <!-- Error Message -->
    <p
      v-if="hasError && errorMessage"
      class="mt-1 text-xs text-[#FF3B30]"
    >
      {{ errorMessage }}
    </p>
  </label>
</template>
