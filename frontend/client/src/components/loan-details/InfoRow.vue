<template>
  <div
    :class="[
      'flex items-center gap-4 pb-3',
      highlight
        ? 'justify-between bg-brand/5 rounded-lg px-3 py-2.5 border border-brand/20'
        : 'justify-between border-b border-surface-muted',
      isRtl ? 'flex-row-reverse' : 'flex-row',
    ]"
  >
    <!-- Label -->
    <span
      class="text-sm text-muted font-medium flex-shrink-0"
      :class="isRtl ? 'text-right' : 'text-left'"
    >
      {{ label }}
    </span>

    <!-- Value -->
    <p
      :class="[
        'text-sm font-semibold text-ink break-words',
        isRtl ? 'text-left' : 'text-right',
        highlight ? 'text-brand text-base' : '',
      ]"
      :dir="isRtl ? 'rtl' : 'ltr'"
    >
      {{ value || "—" }}
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string;
  value: string;
  isRtl: boolean;
  highlight?: boolean;
}

withDefaults(defineProps<Props>(), {
  highlight: false,
});
</script>

<style scoped>
</style>
