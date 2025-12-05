<!-- src/components/LoanTypeFilter.vue -->
<template>
  <div class="flex items-center gap-3">
    <label class="text-sm font-medium text-gray-700">{{ t("loan.filterByType") }}</label>

    <select
      v-model="selected"
      @change="emit('update:modelValue', selected)"
      class="border rounded px-3 py-1 text-sm"
    >
      <option value="all">{{ t("loan.all") }}</option>
      <option value="checks">{{ t("loan.checks") }}</option>
      <option value="standing">{{ t("loan.standingOrders") }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{ modelValue: string }>();
const emit = defineEmits(["update:modelValue"]);

const { t } = useI18n();

const selected = ref(props.modelValue);
</script>
