<template>
  <figure class="donut">
    <div class="flex flex-col items-center gap-6 sm:flex-row sm:items-center">
      <!-- Ring -->
      <div class="relative h-44 w-44 flex-shrink-0">
        <svg
          viewBox="0 0 120 120"
          class="h-full w-full -rotate-90"
          role="img"
          :aria-label="ariaLabel"
        >
          <!-- Empty track when there is no data -->
          <circle
            cx="60"
            cy="60"
            :r="radius"
            fill="none"
            stroke="var(--color-line)"
            :stroke-width="thickness"
          />

          <circle
            v-for="arc in arcs"
            :key="arc.key"
            cx="60"
            cy="60"
            :r="radius"
            fill="none"
            :stroke="arc.color"
            :stroke-width="hovered === arc.key ? thickness + 3 : thickness"
            :stroke-dasharray="`${arc.length} ${circumference - arc.length}`"
            :stroke-dashoffset="-arc.offset"
            class="cursor-pointer transition-[stroke-width,opacity] duration-150"
            :opacity="hovered && hovered !== arc.key ? 0.35 : 1"
            @mouseenter="hovered = arc.key"
            @mouseleave="hovered = null"
            @click="emit('select', arc.key)"
          />
        </svg>

        <!-- Centre: total, or the hovered slice -->
        <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
          <template v-if="hoveredSegment">
            <span class="text-2xl font-bold text-ink">{{ format(hoveredSegment.value) }}</span>
            <span class="mt-0.5 max-w-[7rem] text-xs leading-4 text-muted">{{ hoveredSegment.label }}</span>
            <span class="text-xs font-semibold text-ink-soft">{{ percent(hoveredSegment.value) }}</span>
          </template>
          <template v-else>
            <span class="text-3xl font-bold text-ink">{{ format(total) }}</span>
            <span class="mt-0.5 text-xs text-muted">{{ centerLabel }}</span>
          </template>
        </div>
      </div>

      <!-- Legend: always present, carries identity + exact numbers -->
      <ul class="w-full min-w-0 flex-1 space-y-1.5">
        <li v-for="segment in segments" :key="segment.key">
          <button
            type="button"
            class="flex w-full cursor-pointer items-center gap-3 rounded-xl px-3 py-2.5 text-start transition hover:bg-canvas focus-visible:bg-canvas"
            :class="hovered === segment.key ? 'bg-canvas' : ''"
            @mouseenter="hovered = segment.key"
            @mouseleave="hovered = null"
            @focus="hovered = segment.key"
            @blur="hovered = null"
            @click="emit('select', segment.key)"
          >
            <span
              class="h-3 w-3 flex-shrink-0 rounded-full"
              :style="{ backgroundColor: segment.color }"
              aria-hidden="true"
            ></span>
            <span class="min-w-0 flex-1 truncate text-sm font-medium text-ink-soft">
              {{ segment.label }}
            </span>
            <span class="text-sm font-bold text-ink">{{ format(segment.value) }}</span>
            <span class="w-11 text-end text-xs text-muted">{{ percent(segment.value) }}</span>
          </button>
        </li>
      </ul>
    </div>

    <!-- Same numbers as a table, for screen readers -->
    <table class="sr-only">
      <caption>{{ ariaLabel }}</caption>
      <tbody>
        <tr v-for="segment in segments" :key="segment.key">
          <th scope="row">{{ segment.label }}</th>
          <td>{{ format(segment.value) }}</td>
          <td>{{ percent(segment.value) }}</td>
        </tr>
      </tbody>
    </table>
  </figure>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

export type DonutSegment = {
  key: string;
  label: string;
  value: number;
  color: string;
};

const props = withDefaults(
  defineProps<{
    segments: DonutSegment[];
    centerLabel: string;
    ariaLabel: string;
    formatValue?: (value: number) => string;
  }>(),
  {
    formatValue: undefined,
  }
);

const emit = defineEmits<{
  (event: "select", key: string): void;
}>();

const radius = 46;
const thickness = 14;
const circumference = 2 * Math.PI * radius;
// 2px surface gap between slices (in viewBox units ≈ 2px at this size).
const GAP = 1.6;

const hovered = ref<string | null>(null);

const total = computed(() =>
  props.segments.reduce((sum, segment) => sum + Math.max(segment.value, 0), 0)
);

const arcs = computed(() => {
  const visible = props.segments.filter((segment) => segment.value > 0);
  const gap = visible.length > 1 ? GAP : 0;
  let offset = 0;

  return visible.map((segment) => {
    const full = (segment.value / (total.value || 1)) * circumference;
    const arc = {
      key: segment.key,
      color: segment.color,
      offset,
      length: Math.max(full - gap, 0.5),
    };
    offset += full;
    return arc;
  });
});

const hoveredSegment = computed(() =>
  props.segments.find((segment) => segment.key === hovered.value) || null
);

function format(value: number): string {
  return props.formatValue ? props.formatValue(value) : String(value);
}

function percent(value: number): string {
  if (!total.value) {
    return "0%";
  }

  return `${Math.round((value / total.value) * 100)}%`;
}
</script>
