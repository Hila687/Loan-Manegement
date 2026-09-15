<script setup>
defineProps({
  title: String,
  badge: String,
});
</script>

<template>
  <div
    class="flex flex-col gap-6 rounded-xl bg-white p-6 shadow-sm border border-line"
  >
    <div v-if="title" class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-black">
        {{ title }}
      </h2>
      <span v-if="badge" class="text-xs font-medium text-muted">
        {{ badge }}
      </span>
    </div>

    <div class="space-y-6">
      <slot />
    </div>
  </div>
</template>
