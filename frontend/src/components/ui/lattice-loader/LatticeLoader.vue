<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, type CSSProperties } from 'vue'

type LatticeStatus = 'working' | 'done' | 'error'
type LatticeGrid = 3 | 4
type PatternName = 'arrow' | 'dots' | 'orbit' | 'ripple' | 'snake' | 'spiral' | 'sweep' | 'spin' | 'rain' | 'pulse'
type Pattern = { cells: (number | null)[]; loop?: number; scale?: number; lit?: 0.25 | 0.35 | 0.45 | 0.62 }
type ResolvedPattern = { cells: (number | null)[]; loop: number; scale: number; lit?: number }

const props = withDefaults(defineProps<{
  label?: string
  doneLabel?: string
  errorLabel?: string
  status?: LatticeStatus
  pattern?: PatternName | Pattern
  grid?: LatticeGrid
  shape?: 'square' | 'round'
  color?: string
  doneColor?: string
  errorColor?: string
  cellSize?: number
  gap?: number
  fontSize?: number
  step?: number
  idleOpacity?: number
  glow?: boolean
  glowColor?: string
  showTimer?: boolean
  elapsed?: number
  className?: string
}>(), {
  label: 'Thinking', doneLabel: 'Done in', errorLabel: 'Failed after',
  status: 'working', pattern: 'orbit', grid: 3, shape: 'round', color: 'currentColor',
  doneColor: '#22c55e', errorColor: '#ef4444', cellSize: 6, gap: 2,
  fontSize: 14, step: 90, idleOpacity: 0.15, glow: false, glowColor: '', showTimer: true,
  elapsed: undefined, className: '',
})

const PATTERNS: Record<PatternName, Partial<Record<LatticeGrid, ResolvedPattern>>> = {
  arrow: { 3: { cells: [1, 2, 3, 0, 1, 2, 1, 2, 3], loop: 7.2, scale: 1 } },
  dots: { 3: { cells: [0, 1, 2, 0, 1, 2, 0, 1, 2], loop: 3, scale: 2.4 } },
  ripple: { 3: { cells: [2, 1, 2, 1, 0, 1, 2, 1, 2], loop: 4.8, scale: 1.5 } },
  spiral: { 3: { cells: [0, 1, 2, 7, 8, 3, 6, 5, 4], loop: 9, scale: 1.2, lit: 0.35 } },
  orbit: {
    3: { cells: [0, 1, 2, 7, null, 3, 6, 5, 4], loop: 8, scale: 1.2 },
    4: { cells: [0, 1, 2, 3, 11, null, null, 4, 10, null, null, 5, 9, 8, 7, 6], loop: 6, scale: 1.2, lit: 0.45 },
  },
  snake: {
    3: { cells: [0, 1, 2, 5, 4, 3, 6, 7, 8], loop: 9, scale: 1, lit: 0.35 },
    4: { cells: [0, 1, 2, 3, 7, 6, 5, 4, 8, 9, 10, 11, 15, 14, 13, 12], loop: 16, scale: 1, lit: 0.25 },
  },
  sweep: { 4: { cells: [0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5, 3, 4, 5, 6], loop: 5, scale: 1, lit: 0.45 } },
  spin: { 4: { cells: [0, 0, 1, 1, 0, 0, 1, 1, 3, 3, 2, 2, 3, 3, 2, 2], loop: 4, scale: 1.6, lit: 0.35 } },
  rain: { 4: { cells: [0, 2, 1, 3, 1, 3, 2, 4, 2, 4, 3, 5, 3, 5, 4, 6], loop: 4, scale: 1.2, lit: 0.35 } },
  pulse: { 4: { cells: [2, 1, 1, 2, 1, 0, 0, 1, 1, 0, 0, 1, 2, 1, 1, 2], loop: 2.4, scale: 2.5, lit: 0.45 } },
}
const DEFAULT_PATTERN: Record<LatticeGrid, PatternName> = { 3: 'orbit', 4: 'sweep' }
const MARKS: Record<LatticeGrid, Record<'done' | 'error', number[]>> = {
  3: { done: [2, 3, 5, 7], error: [0, 2, 4, 6, 8] },
  4: { done: [7, 8, 10, 13], error: [0, 3, 5, 6, 9, 10, 12, 15] },
}
const CELL = 'h-[var(--ll-cell)] w-[var(--ll-cell)] [border-radius:max(1px,calc(var(--ll-cell)*0.25))] [background:var(--ll-color)] group-data-[shape=round]:rounded-full'
const HOLE_CLASS = `${CELL} [opacity:calc(var(--ll-idle)*0.47)]`
const LIT: Record<number, string> = {
  62: 'animate-[lattice-on_var(--ll-cycle)_infinite]',
  45: 'animate-[lattice-on-45_var(--ll-cycle)_infinite]',
  35: 'animate-[lattice-on-35_var(--ll-cycle)_infinite]',
  25: 'animate-[lattice-on-25_var(--ll-cycle)_infinite]',
}
const LIT_CLASS = '[opacity:var(--ll-idle)] [animation-timing-function:var(--ll-ease-in-out)] group-data-[glow]:[box-shadow:0_0_calc(var(--ll-cell)*1.2)_calc(var(--ll-cell)*0.12)_var(--ll-glow)]'
const MARK_CELL_CLASS = '[opacity:var(--ll-idle)] [transition:opacity_200ms_ease,background-color_200ms_ease] data-[on]:[background:var(--ll-mark)] data-[on]:[opacity:var(--ll-peak)] group-data-[glow]:data-[on]:[box-shadow:0_0_calc(var(--ll-cell)*1.2)_calc(var(--ll-cell)*0.12)_var(--ll-mark-glow)]'
const TEXT_CLASS = 'll-text absolute top-0 left-0 whitespace-nowrap opacity-0 [filter:blur(2px)] [transition:opacity_200ms_ease,filter_200ms_ease] data-[active]:static data-[active]:opacity-100 data-[active]:[filter:blur(0)]'
const gridSize = computed<LatticeGrid>(() => props.grid === 4 ? 4 : 3)
const resolvedPattern = computed<ResolvedPattern>(() => {
  if (typeof props.pattern === 'string') {
    const named = PATTERNS[props.pattern]?.[gridSize.value]
    return named || PATTERNS[DEFAULT_PATTERN[gridSize.value]][gridSize.value]!
  }
  const cells = Array.from({ length: gridSize.value ** 2 }, (_, index) => props.pattern!.cells[index] ?? null)
  const max = Math.max(0, ...cells.filter((value): value is number => value != null))
  return { cells, loop: props.pattern!.loop ?? max + 4.2, scale: props.pattern!.scale ?? 1, lit: props.pattern!.lit ?? 0.62 }
})
const stepDuration = computed(() => props.step * resolvedPattern.value.scale)
const cycleDuration = computed(() => Math.round(resolvedPattern.value.loop * stepDuration.value))
const lastMark = ref<'done' | 'error'>('done')
const mark = computed(() => {
  if (props.status !== 'working') lastMark.value = props.status
  return lastMark.value
})
const timerRef = ref<HTMLSpanElement | null>(null)
const elapsedDeciseconds = ref(0)
let clock: ReturnType<typeof setInterval> | undefined
const announce = ref(`${props.label}, in progress`)

function paint(value: number) {
  elapsedDeciseconds.value = value
  if (timerRef.value) timerRef.value.textContent = formatTime(value)
}
function formatTime(value: number) {
  return value < 600 ? `${(value / 10).toFixed(1)}s` : `${Math.floor(value / 600)}m ${((value % 600) / 10).toFixed(1)}s`
}
function spokenTime(value: number) {
  return value < 600 ? `${(value / 10).toFixed(1)} seconds` : `${Math.floor(value / 600)} minutes ${((value % 600) / 10).toFixed(1)} seconds`
}
function syncClock() {
  clearInterval(clock)
  if (props.elapsed != null) {
    paint(Math.round(props.elapsed * 10))
    return
  }
  if (props.status !== 'working') return
  const startedAt = performance.now()
  paint(0)
  clock = setInterval(() => paint(Math.floor((performance.now() - startedAt) / 100)), 100)
}
function syncAnnounce() {
  announce.value = props.status === 'working'
    ? `${props.label}, in progress`
    : `${props.status === 'done' ? props.doneLabel : props.errorLabel}${props.showTimer ? ` ${spokenTime(elapsedDeciseconds.value)}` : ''}`
}
onMounted(() => { syncClock(); syncAnnounce() })
watch(() => [props.status, props.elapsed], () => { syncClock(); syncAnnounce() }, { flush: 'post' })
onUnmounted(() => clearInterval(clock))

const rootStyle = computed(() => ({
  '--ll-n': gridSize.value,
  '--ll-cell': `${props.cellSize}px`,
  '--ll-gap': `${props.gap}px`,
  '--ll-font': `${props.fontSize}px`,
  '--ll-color': props.color,
  '--ll-mark': props.status === 'error' ? props.errorColor : props.doneColor,
  '--ll-idle': props.idleOpacity,
  '--ll-glow': props.glowColor || props.color,
  '--ll-mark-glow': props.glowColor || (props.status === 'error' ? props.errorColor : props.doneColor),
  '--ll-cycle': `${cycleDuration.value}ms`,
  '--ll-peak': 1,
  '--ll-ease-out': 'cubic-bezier(0.23, 1, 0.32, 1)',
  '--ll-ease-in-out': 'cubic-bezier(0.77, 0, 0.175, 1)',
}) as CSSProperties)
const cellClass = (unit: number | null) => unit == null
  ? HOLE_CLASS
  : `${CELL} ${LIT_CLASS} ${LIT[Math.round((resolvedPattern.value.lit ?? 0.62) * 100)] || LIT[62]}`
</script>

<template>
  <span
    role="status"
    class="ll-root group relative inline-flex items-center leading-none [font-family:inherit] [gap:calc(var(--ll-font)*0.625)] [font-size:var(--ll-font)]"
    :class="className"
    :data-status="status"
    :data-shape="shape"
    :data-glow="glow ? '' : undefined"
    :style="rootStyle"
  >
    <span class="grid shrink-0" aria-hidden="true">
      <span class="ll-run [grid-area:1/1] grid [grid-template-columns:repeat(var(--ll-n),var(--ll-cell))] [gap:var(--ll-gap)] [transition:opacity_200ms_ease] group-data-[status=done]:opacity-0 group-data-[status=error]:opacity-0 group-data-[status=done]:[&>span]:[animation-play-state:paused] group-data-[status=error]:[&>span]:[animation-play-state:paused]">
        <span v-for="(unit, index) in resolvedPattern.cells" :key="index" :class="cellClass(unit)" :data-hole="unit == null ? '' : undefined" :data-lit="resolvedPattern.lit && resolvedPattern.lit !== 0.62 ? Math.round(resolvedPattern.lit * 100) : undefined" :style="unit == null ? undefined : { animationDelay: `${Math.round(unit * stepDuration)}ms` }" />
      </span>
      <span class="ll-mark [grid-area:1/1] grid [grid-template-columns:repeat(var(--ll-n),var(--ll-cell))] [gap:var(--ll-gap)] origin-center opacity-0 [transform:scale(0.9)] [transition:opacity_160ms_var(--ll-ease-out),transform_160ms_var(--ll-ease-out)] group-data-[status=done]:opacity-100 group-data-[status=done]:[transform:none] group-data-[status=done]:[transition:opacity_200ms_ease,transform_200ms_var(--ll-ease-out)] group-data-[status=error]:opacity-100 group-data-[status=error]:[transform:none] group-data-[status=error]:[transition:opacity_200ms_ease,transform_200ms_var(--ll-ease-out)]">
        <span v-for="(_, index) in resolvedPattern.cells" :key="index" :class="[CELL, MARK_CELL_CLASS]" :data-on="MARKS[gridSize][mark].includes(index) ? '' : undefined" />
      </span>
    </span>
    <span class="relative inline-block font-medium" aria-hidden="true">
      <span :class="TEXT_CLASS" :data-active="status === 'working' ? '' : undefined">{{ label }}</span>
      <span :class="TEXT_CLASS" :data-active="status === 'done' ? '' : undefined">{{ doneLabel }}</span>
      <span :class="TEXT_CLASS" :data-active="status === 'error' ? '' : undefined">{{ errorLabel }}</span>
    </span>
    <span v-if="showTimer" ref="timerRef" class="opacity-60 font-mono tabular-nums [font-size:calc(var(--ll-font)*0.875)]" aria-hidden="true">0.0s</span>
    <span class="sr-only">{{ announce }}</span>
  </span>
</template>

<style>
@keyframes lattice-on {
  0%, 100% { opacity: var(--ll-idle); }
  18%, 42% { opacity: var(--ll-peak); }
  62% { opacity: var(--ll-idle); }
}
@keyframes lattice-on-45 {
  0%, 100% { opacity: var(--ll-idle); }
  13%, 31% { opacity: var(--ll-peak); }
  45% { opacity: var(--ll-idle); }
}
@keyframes lattice-on-35 {
  0%, 100% { opacity: var(--ll-idle); }
  10%, 24% { opacity: var(--ll-peak); }
  35% { opacity: var(--ll-idle); }
}
@keyframes lattice-on-25 {
  0%, 100% { opacity: var(--ll-idle); }
  7%, 17% { opacity: var(--ll-peak); }
  25% { opacity: var(--ll-idle); }
}
@media (prefers-reduced-motion: reduce) {
  .ll-run { --ll-peak: 0.7; }
  .ll-run > span { animation-delay: 0ms !important; animation-duration: 1400ms !important; }
  .ll-mark { transform: none !important; }
  .ll-text { filter: none !important; }
}
</style>
