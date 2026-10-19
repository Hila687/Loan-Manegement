<!-- src/components/loan-details/TabsSection.vue -->
<template>
  <div>
    <!-- Tabs Header -->
    <div class="flex border-b mb-4">
      <button
        class="px-4 py-2 -mb-px border-b-2 font-medium transition-colors"
        :class="selectedTab === 'schedule'
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-muted hover:text-ink-soft'"
        @click="setTab('schedule')"
      >
        {{ t("loanDetails.tabSchedule") }}
      </button>

      <button
        class="px-4 py-2 -mb-px border-b-2 font-medium transition-colors"
        :class="selectedTab === 'details'
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-muted hover:text-ink-soft'"
        @click="setTab('details')"
      >
        {{ t("loanDetails.tabDetails") }}
      </button>
    </div>

    <!-- Tabs Content -->
    <div>
      <!-- Details Tab -->
      <div v-if="selectedTab === 'details'" class="space-y-6">
        <slot name="details"></slot>
      </div>

      <!-- Schedule Tab -->
    <div v-if="selectedTab === 'schedule'" class="space-y-6">
      <slot name="schedule"></slot>
    </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const emit = defineEmits<{
  (e: "tab-change", tab: "details" | "schedule"): void;
}>();

// The payment schedule is what people look for first.
const selectedTab = ref<"details" | "schedule">("schedule");

function setTab(tab: "details" | "schedule") {
  selectedTab.value = tab;
  emit("tab-change", tab);
}

</script>

