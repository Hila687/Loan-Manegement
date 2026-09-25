<script setup lang="ts">
import {
  computed,
  ref,
} from "vue";


interface Props {
  modelValue: string;
  label: string;
  placeholder?: string;
  isRTL?: boolean;
  hasError?: boolean;
  errorMessage?: string;
  required?: boolean;
  locale?: "he" | "en" | "es";
}


const props = withDefaults(
  defineProps<Props>(),
  {
    placeholder: "",
    isRTL: false,
    hasError: false,
    errorMessage: "",
    required: false,
    locale: "he",
  }
);


const emit = defineEmits<{
  "update:modelValue": [value: string];
  keydown: [event: KeyboardEvent];
}>();


const dateInputRef =
  ref<HTMLInputElement | null>(
    null
  );


const labelDir =
  computed(() =>
    props.isRTL
      ? "rtl"
      : "ltr"
  );


const labelAlign =
  computed(() =>
    props.isRTL
      ? "text-right"
      : "text-left"
  );


function onInput(
  event: Event
): void {
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

  emit(
    "update:modelValue",
    target.value
  );
}


function focus(): void {
  dateInputRef.value
    ?.focus();
}


defineExpose({
  focus,
});
</script>


<template>
  <label
    class="flex flex-col"
  >
    <p
      :dir="labelDir"
      :class="labelAlign"
      class="pb-1.5 text-sm font-medium leading-normal text-muted xl:pb-2"
    >
      <span
        v-if="required"
        :class="hasError ? 'text-danger' : 'text-muted'"
      >
        *
      </span>

      {{ label }}
    </p>

    <div
      class="relative"
    >
      <input
        ref="dateInputRef"
        :value="modelValue"
        type="date"
        :lang="locale"
        dir="ltr"
        :class="[
          'h-12 w-full rounded-xl border bg-white px-4 text-base font-medium text-ink outline-none transition',
          'focus:ring-2',
          hasError
            ? 'border-danger focus:border-danger focus:ring-danger/20'
            : 'border-line focus:border-brand focus:ring-brand/20',
        ]"
        @input="onInput"
        @keydown="emit('keydown', $event)"
      />
    </div>

    <p
      v-if="hasError && errorMessage"
      class="mt-1 text-xs text-danger"
      :dir="labelDir"
      :class="labelAlign"
    >
      {{ errorMessage }}
    </p>
  </label>
</template>


<style scoped>
input[type="date"] {
  min-width: 0;
  color-scheme: light;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.7;
}
</style>
