<template>
  <button
    v-if="auth.isAdmin.value"
    type="button"
    class="w-full rounded-lg bg-brand px-4 py-2.5 font-semibold text-white transition-all hover:bg-brand-deep active:scale-95"
    @click="goToEdit"
  >
    {{ t("loanDetails.editButton") }}
  </button>
</template>

<script setup lang="ts">
import {
  useRouter,
} from "vue-router";

import {
  useI18n,
} from "vue-i18n";

import {
  useAuth,
} from "../../composables/useAuth";

const props =
  defineProps<{
    loanId: string;
  }>();

const router =
  useRouter();

const { t } =
  useI18n();

const auth =
  useAuth();

function goToEdit() {
  router.push(
    `/loans/${encodeURIComponent(
      props.loanId
    )}/edit`
  );
}
</script>