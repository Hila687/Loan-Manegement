<!-- src/components/loan-details/TabsSection.vue -->
<template>
  <div>
    <!-- Tabs Header -->
    <div class="flex border-b mb-4">
      <button
        class="px-4 py-2 -mb-px border-b-2 font-medium transition-colors"
        :class="selectedTab === 'details'
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="selectedTab = 'details'"
      >
        {{ t("loanDetails.tabDetails") }}
      </button>

      <button
        class="px-4 py-2 -mb-px border-b-2 font-medium transition-colors"
        :class="selectedTab === 'schedule'
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="selectedTab = 'schedule'"
      >
        {{ t("loanDetails.tabSchedule") }}
      </button>
    </div>

    <!-- Tabs Content -->
    <div>
      <!-- Details Tab -->
      <div v-if="selectedTab === 'details'" class="space-y-6">
        <slot name="details"></slot>
      </div>

      <!-- Schedule Tab -->
      <div v-if="selectedTab === 'schedule'" class="p-3 text-gray-500 italic">
        {{ t("loanDetails.schedulePlaceholder") }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const selectedTab = ref<"details" | "schedule">("details");
</script>
