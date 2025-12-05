<!-- src/components/NavigationCard.vue -->
<template>
  <div
    class="border rounded-lg shadow p-6 cursor-pointer hover:bg-gray-50 transition"
    @click="goToTarget"
  >
    <h3 class="text-lg font-semibold mb-2">{{ title }}</h3>
    <p class="text-gray-600 text-sm">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const props = defineProps<{
  title: string;
  description: string;
  to: string;
}>();

const router = useRouter();

const goToTarget = () => {
  router.push(props.to);
};
</script>
