<template>
  <div
    ref="rootElement"
    class="space-y-2"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <div class="flex items-center justify-between gap-3">
      <label class="text-start text-sm font-medium text-muted">
        <span
          v-if="required"
          :class="errorMessage ? 'text-danger' : 'text-muted'"
        >*</span>
        {{ label }}
      </label>

      <button
        v-if="selectedOption && !disabled"
        type="button"
        class="text-xs font-semibold text-brand transition hover:text-brand-deep"
        @click="clearSelection"
      >
        {{ changeLabel }}
      </button>
    </div>

    <div
      v-if="selectedOption"
      class="flex items-center justify-between gap-3 rounded-xl border border-brand/20 bg-brand/5 p-3.5"
    >
      <div class="flex min-w-0 flex-1 items-center gap-3 text-start">
        <div
          class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-brand text-sm font-bold text-white"
        >
          {{ selectedInitials }}
        </div>

        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-semibold text-ink">
            {{ selectedOption.name }}
          </p>

          <p
            v-if="selectedOption.community"
            class="mt-0.5 truncate text-xs text-muted"
          >
            {{ selectedOption.community }}
          </p>
        </div>
      </div>

      <svg
        class="h-5 w-5 flex-shrink-0 text-success"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M5 13l4 4L19 7"
        />
      </svg>
    </div>

    <div v-else class="relative">
      <span
        :class="[
          'pointer-events-none absolute inset-y-0 z-10 flex items-center text-muted',
          isRTL ? 'right-0 pr-4' : 'left-0 pl-4',
        ]"
      >
        <svg
          class="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="8" stroke-width="2" />
          <path
            d="m21 21-4.35-4.35"
            stroke-width="2"
            stroke-linecap="round"
          />
        </svg>
      </span>

      <input
        ref="searchInput"
        v-model="query"
        type="search"
        autocomplete="off"
        :disabled="disabled || loading"
        :dir="isRTL ? 'rtl' : 'ltr'"
        :placeholder="placeholder"
        :class="[
          'h-11 w-full rounded-xl border bg-white text-sm text-ink outline-none transition placeholder:text-muted disabled:cursor-not-allowed disabled:bg-surface-muted xl:h-12',
          isRTL ? 'pr-10 pl-4 text-right' : 'pl-10 pr-4 text-left',
          errorMessage
            ? 'border-danger focus:border-danger focus:ring-2 focus:ring-danger/20'
            : 'border-line focus:border-brand focus:ring-2 focus:ring-brand/20',
        ]"
        @focus="open = true"
        @keydown.escape.prevent="open = false"
        @keydown.down.prevent="moveHighlight(1)"
        @keydown.up.prevent="moveHighlight(-1)"
        @keydown.enter.prevent="selectHighlighted"
      />

      <div
        v-if="loading"
        :class="[
          'pointer-events-none absolute inset-y-0 flex items-center',
          isRTL ? 'left-0 pl-4' : 'right-0 pr-4',
        ]"
      >
        <div
          class="h-4 w-4 animate-spin rounded-full border-2 border-brand border-t-transparent"
        ></div>
      </div>

      <div
        v-if="open && !loading"
        class="absolute left-0 right-0 z-[80] mt-2 max-h-64 overflow-y-auto rounded-2xl border border-line bg-white p-1.5 shadow-xl"
        :dir="isRTL ? 'rtl' : 'ltr'"
      >
        <button
          v-for="(option, index) in filteredOptions"
          :key="option.id"
          type="button"
          :class="[
            'flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm transition',
            isRTL ? 'text-right' : 'text-left',
            highlightedIndex === index ? 'bg-brand/10' : 'hover:bg-surface-muted',
          ]"
          @mousedown.prevent
          @mouseenter="highlightedIndex = index"
          @click="selectOption(option)"
        >
          <div
            class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-surface-muted font-semibold text-brand"
          >
            {{ initials(option.name) }}
          </div>

          <div class="min-w-0 flex-1 text-start">
            <p class="truncate font-semibold text-ink">
              {{ option.name }}
            </p>

            <p
              v-if="option.community"
              class="mt-0.5 truncate text-xs text-muted"
            >
              {{ option.community }}
            </p>
          </div>
        </button>

        <div
          v-if="filteredOptions.length === 0"
          class="px-4 py-5 text-center text-sm text-muted"
        >
          {{ noResultsLabel }}
        </div>
      </div>
    </div>

    <p
      v-if="helperText && !errorMessage"
      class="text-start text-xs text-muted"
    >
      {{ helperText }}
    </p>

    <p
      v-if="errorMessage"
      class="text-start text-xs text-danger"
    >
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";

export type TrusteePickerOption = {
  id: string;
  name: string;
  community?: string;
};

const props = withDefaults(
  defineProps<{
    modelValue: string;
    options: TrusteePickerOption[];
    label: string;
    placeholder: string;
    helperText?: string;
    errorMessage?: string | null;
    loading?: boolean;
    disabled?: boolean;
    required?: boolean;
    isRTL?: boolean;
    locale?: "he" | "en";
  }>(),
  {
    helperText: "",
    errorMessage: null,
    loading: false,
    disabled: false,
    required: false,
    isRTL: false,
    locale: "he",
  }
);

const emit = defineEmits<{
  (event: "update:modelValue", value: string): void;
  (event: "selected", option: TrusteePickerOption | null): void;
}>();

const query = ref("");
const open = ref(false);
const highlightedIndex = ref(-1);
const searchInput = ref<HTMLInputElement | null>(null);
const rootElement = ref<HTMLElement | null>(null);

const selectedOption = computed(() =>
  props.options.find((option) => option.id === props.modelValue) || null
);

const filteredOptions = computed(() => {
  const normalizedQuery = query.value.trim().toLowerCase();

  if (!normalizedQuery) {
    return props.options;
  }

  return props.options.filter((option) =>
    option.name.toLowerCase().includes(normalizedQuery)
  );
});

const changeLabel = computed(() =>
  props.locale === "he" ? "החלפת נאמן" : "Change trustee"
);

const noResultsLabel = computed(() =>
  props.locale === "he"
    ? "לא נמצאו נאמנים בשם הזה"
    : "No trustees found with this name"
);

const selectedInitials = computed(() => initials(selectedOption.value?.name || ""));

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);

  if (parts.length === 0) {
    return "?";
  }

  return parts
    .slice(0, 2)
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase();
}

function selectOption(option: TrusteePickerOption): void {
  emit("update:modelValue", option.id);
  emit("selected", option);
  query.value = "";
  open.value = false;
  highlightedIndex.value = -1;
}

function clearSelection(): void {
  emit("update:modelValue", "");
  emit("selected", null);
  query.value = "";
  open.value = true;

  nextTick(() => {
    searchInput.value?.focus();
  });
}

function moveHighlight(direction: number): void {
  if (!open.value) {
    open.value = true;
  }

  if (filteredOptions.value.length === 0) {
    highlightedIndex.value = -1;
    return;
  }

  const next = highlightedIndex.value + direction;

  if (next < 0) {
    highlightedIndex.value = filteredOptions.value.length - 1;
    return;
  }

  if (next >= filteredOptions.value.length) {
    highlightedIndex.value = 0;
    return;
  }

  highlightedIndex.value = next;
}

function selectHighlighted(): void {
  if (!open.value) {
    open.value = true;
    return;
  }

  if (highlightedIndex.value < 0) {
    return;
  }

  const option = filteredOptions.value[highlightedIndex.value];

  if (option) {
    selectOption(option);
  }
}

function handleOutsideClick(event: MouseEvent): void {
  const target = event.target as Node;

  if (rootElement.value?.contains(target)) {
    return;
  }

  open.value = false;
}

function focus(): void {
  if (selectedOption.value) {
    clearSelection();
    return;
  }

  open.value = true;

  nextTick(() => {
    searchInput.value?.focus();
  });
}

watch(
  () => props.options,
  () => {
    if (props.modelValue && !selectedOption.value) {
      emit("selected", null);
    }
  }
);

watch(filteredOptions, () => {
  highlightedIndex.value = filteredOptions.value.length > 0 ? 0 : -1;
});

onMounted(() => {
  document.addEventListener("click", handleOutsideClick);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleOutsideClick);
});

defineExpose({
  focus,
});
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
