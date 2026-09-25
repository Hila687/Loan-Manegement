<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
} from "vue";

import {
  type AppLocale,
  useLocale,
} from "../composables/useLocale";


const {
  locale,
  setLanguage,
} = useLocale();

const root =
  ref<HTMLElement | null>(null);

const open =
  ref(false);

const languages: Array<{
  value: AppLocale;
  code: string;
  label: string;
}> = [
  {
    value: "he",
    code: "HE",
    label: "עברית",
  },
  {
    value: "en",
    code: "EN",
    label: "English",
  },
  {
    value: "es",
    code: "ES",
    label: "Español",
  },
];

const currentCode =
  computed(() => {
    const current =
      languages.find(
        (item) =>
          item.value ===
          locale.value
      );

    return current?.code ||
      "HE";
  });


function chooseLanguage(
  language: AppLocale
): void {
  setLanguage(
    language
  );

  open.value =
    false;
}


function handleOutsideClick(
  event: MouseEvent
): void {
  if (
    root.value &&
    !root.value.contains(
      event.target as Node
    )
  ) {
    open.value =
      false;
  }
}


onMounted(() => {
  document.addEventListener(
    "click",
    handleOutsideClick
  );
});


onBeforeUnmount(() => {
  document.removeEventListener(
    "click",
    handleOutsideClick
  );
});
</script>


<template>
  <div
    ref="root"
    class="relative"
  >
    <button
      type="button"
      class="inline-flex h-10 min-w-16 cursor-pointer items-center justify-center gap-1.5 rounded-xl border border-line bg-white px-3 text-sm font-semibold text-ink-soft shadow-sm transition hover:border-brand/40 hover:bg-canvas"
      :aria-expanded="open"
      aria-haspopup="menu"
      aria-label="Language"
      @click.stop="open = !open"
    >
      <span>
        {{ currentCode }}
      </span>

      <svg
        class="h-3.5 w-3.5 text-muted transition-transform"
        :class="open ? 'rotate-180' : ''"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        />
      </svg>
    </button>

    <div
      v-if="open"
      class="absolute top-full z-[80] mt-2 w-36 overflow-hidden rounded-xl border border-line bg-white p-1.5 shadow-xl"
      :class="locale === 'he' ? 'left-0' : 'right-0'"
      role="menu"
    >
      <button
        v-for="language in languages"
        :key="language.value"
        type="button"
        class="flex w-full cursor-pointer items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-start text-sm transition hover:bg-canvas"
        :class="
          locale === language.value
            ? 'bg-brand/5 font-semibold text-brand'
            : 'text-ink-soft'
        "
        role="menuitem"
        @click="chooseLanguage(language.value)"
      >
        <span>
          {{ language.label }}
        </span>

        <span
          class="text-xs font-semibold"
          :class="
            locale === language.value
              ? 'text-brand'
              : 'text-muted'
          "
        >
          {{ language.code }}
        </span>
      </button>
    </div>
  </div>
</template>
