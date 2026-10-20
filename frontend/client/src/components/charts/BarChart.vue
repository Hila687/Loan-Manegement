<template>
  <figure>
    <p
      v-if="maxValue <= 0"
      class="rounded-xl bg-canvas px-4 py-8 text-center text-sm text-muted"
    >
      {{ emptyText }}
    </p>

    <!-- Vertical columns (e.g. months) -->
    <div v-else-if="orientation === 'vertical'" class="relative">
      <!-- Y scale: one recessive gridline at the top value -->
      <div class="mb-2 flex items-center gap-2 text-xs text-faint">
        <span dir="ltr">{{ format(scaleMax) }}</span>
        <span class="h-px flex-1 bg-line"></span>
      </div>

      <div
        class="flex h-48 items-end gap-2 border-b border-line-strong sm:gap-3"
        role="img"
        :aria-label="ariaLabel"
      >
        <div
          v-for="(item, index) in items"
          :key="item.key"
          class="group relative flex h-full flex-1 cursor-default flex-col justify-end"
          tabindex="0"
          @mouseenter="hovered = index"
          @mouseleave="hovered = null"
          @focus="hovered = index"
          @blur="hovered = null"
        >
          <!-- Tooltip -->
          <div
            v-if="hovered === index"
            class="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-ink px-3 py-2 text-xs text-white shadow-lg"
          >
            <p class="font-semibold">{{ item.label }}</p>
            <p dir="ltr" class="mt-0.5 text-sm font-bold">{{ format(item.value) }}</p>
            <p v-if="item.detail" class="mt-0.5 text-white/75">{{ item.detail }}</p>
          </div>

          <!-- Direct label only on the highest bar and the hovered one -->
          <span
            v-if="item.value > 0 && (index === maxIndex || hovered === index)"
            dir="ltr"
            class="mb-1 text-center text-[11px] font-semibold text-ink-soft"
          >
            {{ formatShort(item.value) }}
          </span>

          <div
            class="mx-auto w-full max-w-[3rem] rounded-t transition-opacity"
            :style="{
              height: `${barHeight(item.value)}%`,
              backgroundColor: color,
              opacity: hovered !== null && hovered !== index ? 0.45 : 1,
              minHeight: item.value > 0 ? '3px' : '0',
            }"
          ></div>
        </div>
      </div>

      <div class="mt-2 flex gap-2 sm:gap-3">
        <span
          v-for="item in items"
          :key="item.key"
          class="flex-1 truncate text-center text-xs text-muted"
        >
          {{ item.label }}
        </span>
      </div>
    </div>

    <!-- Horizontal ranking (e.g. communities) -->
    <ul v-else class="space-y-3" :aria-label="ariaLabel">
      <li
        v-for="(item, index) in items"
        :key="item.key"
        class="group"
        @mouseenter="hovered = index"
        @mouseleave="hovered = null"
      >
        <div class="mb-1 flex items-baseline justify-between gap-3 text-sm">
          <span class="min-w-0 truncate font-medium text-ink-soft">{{ item.label }}</span>
          <span dir="ltr" class="whitespace-nowrap font-bold text-ink">{{ format(item.value) }}</span>
        </div>
        <div class="h-2.5 w-full rounded-full bg-canvas-deep">
          <div
            class="h-full rounded-full transition-opacity"
            :style="{
              width: `${barHeight(item.value)}%`,
              backgroundColor: color,
              opacity: hovered !== null && hovered !== index ? 0.5 : 1,
              minWidth: item.value > 0 ? '4px' : '0',
            }"
          ></div>
        </div>
        <p v-if="item.detail" class="mt-1 text-xs text-muted">{{ item.detail }}</p>
      </li>
    </ul>

    <!-- Same numbers as a table, for screen readers -->
    <table class="sr-only">
      <caption>{{ ariaLabel }}</caption>
      <tbody>
        <tr v-for="item in items" :key="item.key">
          <th scope="row">{{ item.label }}</th>
          <td>{{ format(item.value) }}</td>
          <td v-if="item.detail">{{ item.detail }}</td>
        </tr>
      </tbody>
    </table>
  </figure>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

export type BarItem = {
  key: string;
  label: string;
  value: number;
  detail?: string;
};

const props = withDefaults(
  defineProps<{
    items: BarItem[];
    ariaLabel: string;
    color?: string;
    orientation?: "vertical" | "horizontal";
    formatValue?: (value: number) => string;
    formatShort?: (value: number) => string;
    emptyText?: string;
  }>(),
  {
    emptyText: "—",
    color: "#2a78d6",
    orientation: "vertical",
    formatValue: undefined,
    formatShort: undefined,
  }
);

const hovered = ref<number | null>(null);

const maxValue = computed(() =>
  Math.max(0, ...props.items.map((item) => item.value))
);

// Round the scale up to a "nice" number so the gridline label is clean.
const scaleMax = computed(() => {
  const max = maxValue.value;
  if (max <= 0) return 0;
  const magnitude = 10 ** Math.floor(Math.log10(max));
  const steps = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10];
  const step = steps.find((s) => s * magnitude >= max) || 10;
  return step * magnitude;
});

const maxIndex = computed(() =>
  props.items.findIndex((item) => item.value === maxValue.value && item.value > 0)
);

function barHeight(value: number): number {
  const top = props.orientation === "vertical" ? scaleMax.value : maxValue.value;
  return top > 0 ? (value / top) * 100 : 0;
}

function format(value: number): string {
  return props.formatValue ? props.formatValue(value) : String(value);
}

function formatShort(value: number): string {
  return props.formatShort ? props.formatShort(value) : format(value);
}
</script>
