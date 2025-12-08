<script setup lang="ts">
import { computed, ref } from "vue";

interface Props {
  modelValue: string | number;
  label: string;
  placeholder: string;
  icon?: "user" | "phone" | "building" | "dollar";
  hasError?: boolean;
  errorMessage?: string;
  type?: "text" | "tel" | "number" | "email";
  isRTL?: boolean;
  required?: boolean;
  min?: string | number;
  step?: string | number;
  inputMode?:
    | "none"
    | "text"
    | "tel"
    | "url"
    | "email"
    | "numeric"
    | "decimal"
    | "search";
}

const props = withDefaults(defineProps<Props>(), {
  type: "text",
  isRTL: false,
  required: false,
  min: undefined,
  step: undefined,
});

const emit = defineEmits<{
  "update:modelValue": [value: string | number];
  focus: [];
  blur: [];
  keydown: [event: KeyboardEvent];
  input: [event: Event];
}>();

// Reference to the inner input element
const inputRef = ref<HTMLInputElement | null>(null);

// Padding depends on icon position and currency icon
const paddingClass = computed(() => {
  if (props.icon === "dollar" && props.isRTL) {
    return "pr-8 pl-4";
  }
  if (props.icon === "dollar" && !props.isRTL) {
    return "pl-8 pr-4";
  }
  if (props.icon && props.isRTL) {
    return "pr-10 pl-4";
  }
  return props.icon ? "pl-10 pr-4" : "px-4";
});

// Label direction and alignment
const labelDir = computed(() => (props.isRTL ? "rtl" : "ltr"));
const labelAlign = computed(() => (props.isRTL ? "text-right" : "text-left"));

// Icon position
const iconDir = computed(() =>
  props.isRTL ? "right-0 pr-4" : "left-0 pl-4"
);

// Input text alignment
const inputTextDir = computed(() =>
  props.isRTL ? "text-right" : "text-left"
);

// Handle native input: update v-model and forward the event
function handleInput(event: Event) {
  const target = event.target as HTMLInputElement;
  emit("update:modelValue", target.value);
  emit("input", event);
}

// Expose a focus method so parent can call ref.value.focus()
function focus() {
  if (inputRef.value) {
    inputRef.value.focus();
  }
}

defineExpose({ focus });
</script>

<template>
  <label class="flex flex-col">
    <!-- Field label -->
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
      <!-- Icon -->
      <span
        v-if="icon"
        :class="[
          'pointer-events-none absolute inset-y-0 flex items-center text-[#6B7280]',
          iconDir,
        ]"
      >
        <span v-if="icon === 'dollar'">₪</span>
        <template v-else>
          <!-- User icon -->
          <svg
            v-if="icon === 'user'"
            class="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>

          <!-- Phone icon -->
          <svg
            v-else-if="icon === 'phone'"
            class="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
            />
          </svg>

          <!-- Building icon -->
          <svg
            v-else-if="icon === 'building'"
            class="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
            />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
        </template>
      </span>

      <!-- Input -->
      <input
        ref="inputRef"
        :value="modelValue"
        :type="type"
        :dir="isRTL ? 'rtl' : 'ltr'"
        :placeholder="placeholder"
        :inputmode="inputMode"
        :min="min"
        :step="step"
        :class="[
          'form-input flex h-11 xl:h-12 w-full min-w-0 resize-none overflow-hidden rounded-lg border',
          'bg-white text-base font-normal leading-normal text-black placeholder:text-[#6B7280]',
          'focus:outline-0 focus:ring-2',
          paddingClass,
          inputTextDir,
          hasError
            ? 'border-[#FF3B30] focus:border-[#FF3B30] focus:ring-[#FF3B30]/20'
            : 'border-[#E5E5EA] focus:border-[#007AFF] focus:ring-[#007AFF]/20',
        ]"
        @input="handleInput"
        @focus="emit('focus')"
        @blur="emit('blur')"
        @keydown="emit('keydown', $event)"
      />
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
