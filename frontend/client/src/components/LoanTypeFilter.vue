<!-- src/components/LoanTypeFilter.vue -->
<template>
  <!-- Root container: full width -->
  <div
    class="w-full relative z-40"
    @click.stop
    @keydown.escape.prevent="closeDropdown"
  >
    <!-- Top label ("Filter by loan type") -->
    <p
      class="text-xs sm:text-sm font-medium text-[#6B7280] mb-2 flex items-center gap-2"
      :class="isRtlComputed ? 'justify-end' : 'justify-start'"
    >
      <span>{{ t("loan.filterByType") }}</span>
    </p>

    <!-- Trigger pill -->
    <button
      type="button"
      class="flex items-center w-full rounded-full border-2 border-[#FF9500] bg-white px-4 py-2.5 shadow-sm transition-all hover:shadow-md"
      :class="isRtlComputed ? 'flex-row-reverse' : 'flex-row'"
      @click="toggleDropdown"
    >
      <!-- Icon -->
      <div class="flex items-center justify-center flex-shrink-0">
        <svg
          class="w-5 h-5 text-[#FF9500]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
      </div>

      <!-- Selected label -->
      <div
        class="flex-1 text-sm sm:text-base font-medium text-[#111827] px-3 truncate"
        :class="isRtlComputed ? 'text-right' : 'text-left'"
      >
        {{ selectedLabel }}
      </div>

      <!-- Chevron -->
      <div class="flex items-center justify-center flex-shrink-0">
        <svg
          class="w-4 h-4 text-[#6B7280] transition-transform"
          :class="isOpen ? 'rotate-180' : 'rotate-0'"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </button>

    <!-- Dropdown menu -->
    <transition name="fade-scale">
      <div
        v-if="isOpen"
        class="absolute left-0 right-0 w-full mt-2 rounded-2xl bg-white shadow-xl 
               border border-[#E5E5EA] z-50 overflow-hidden"
      >
        <button
          v-for="option in options"
          :key="option.value"
          type="button"
          class="w-full flex items-center gap-2 px-4 py-2.5 text-sm sm:text-base transition-colors"
          :class="[
            isRtlComputed ? 'flex-row-reverse text-right' : 'flex-row text-left',
            option.value === localValue
              ? 'bg-[#FFF7E6] text-[#FF9500] font-semibold'
              : 'text-[#111827] hover:bg-[#F3F4F6]'
          ]"
          @click="selectOption(option.value)"
        >
          <!-- Checkmark for selected option -->
          <svg
            v-if="option.value === localValue"
            class="w-4 h-4 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>

          <span class="truncate">
            {{ t(option.labelKey) }}
          </span>
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
/**
 * LoanTypeFilter
 * - Custom styled dropdown (no native <select>)
 * - Uses i18n labels from "loan.*"
 * - v-model for the selected type: "all" | "checks" | "standing"
 * - Supports RTL via isRtl prop
 */

import { ref, watch, computed, onMounted, onBeforeUnmount } from "vue";
import { useI18n } from "vue-i18n";

interface Props {
  modelValue: string;
  /** When true, align for RTL layout */
  isRtl?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
}>();

const { t } = useI18n();

// Options definitions with i18n keys
const options = [
  { value: "all", labelKey: "loan.all" },
  { value: "checks", labelKey: "loan.checks" },
  { value: "standing", labelKey: "loan.standingOrders" }
];

// Local state
const localValue = ref(props.modelValue ?? "all");
const isOpen = ref(false);

// Sync with external v-model
watch(
  () => props.modelValue,
  (val) => {
    if (val && val !== localValue.value) {
      localValue.value = val;
    }
  }
);

// RTL helper
const isRtlComputed = computed(() => props.isRtl ?? false);

// Human-readable label for current value
const selectedLabel = computed(() => {
  const opt = options.find((o) => o.value === localValue.value) ?? options[0];
  return t(opt.labelKey);
});

// Dropdown actions
const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const closeDropdown = () => {
  isOpen.value = false;
};

const selectOption = (value: string) => {
  localValue.value = value;
  emit("update:modelValue", value);
  isOpen.value = false;
};

// Close when clicking outside the component
const handleClickOutside = () => {
  if (isOpen.value) {
    isOpen.value = false;
  }
};

onMounted(() => {
  window.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
  window.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
/* Small entrance animation for dropdown */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.15s ease-out;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
</style>
