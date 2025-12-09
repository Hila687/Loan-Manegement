<template>
  <div
    :dir="locale === 'he' ? 'rtl' : 'ltr'"
    :class="[
      'min-h-screen bg-gray-50',
      locale === 'he' ? 'text-right' : 'text-left'
    ]"
  >
    <router-view />
  </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";

const { locale } = useI18n();
</script>
