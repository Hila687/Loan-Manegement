<script setup lang="ts">
const props = defineProps<{
  label: string;
  block?: boolean;
}>();

const emit = defineEmits<{
  (e: "click"): void;
}>();

function onClick() {
  emit("click");
}
</script>

<template>
  <button
    type="button"
    @click="onClick"
    :class="[
      'cursor-pointer overflow-hidden rounded-lg h-12 px-5 bg-[#007AFF] text-white text-sm font-semibold tracking-wide hover:bg-[#0067E0] active:bg-[#0052BA] transition-colors',
      block !== false ? 'w-full flex items-center justify-center' : 'inline-flex items-center justify-center'
    ]"
  >
    <span class="truncate">
      {{ label }}
    </span>
  </button>
</template>
