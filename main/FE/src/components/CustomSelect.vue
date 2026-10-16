<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue"

interface SelectOption {
  label: string
  value: string | number
}

const props = withDefaults(
  defineProps<{
    modelValue?: string | number | null
    options: readonly SelectOption[]
    placeholder?: string
    disabled?: boolean
    size?: "md" | "sm"
  }>(),
  {
    modelValue: "",
    placeholder: "请选择",
    disabled: false,
    size: "md"
  }
)

const emit = defineEmits<{
  (e: "update:modelValue", value: string | number): void
  (e: "change", value: string | number): void
}>()

const rootRef = ref<HTMLElement | null>(null)
const triggerRef = ref<HTMLElement | null>(null)
const panelRef = ref<HTMLElement | null>(null)
const open = ref(false)
const panelStyle = ref<Record<string, string>>({})

const selectedOption = computed(() =>
  props.options.find((item) => String(item.value) === String(props.modelValue ?? ""))
)

// 面板用 fixed 定位并挂到 body，避免被表格 overflow / 弹窗层级裁剪
function positionPanel() {
  const trigger = triggerRef.value
  if (!trigger) return
  const rect = trigger.getBoundingClientRect()
  panelStyle.value = {
    left: `${rect.left}px`,
    top: `${rect.bottom + 6}px`,
    width: `${rect.width}px`
  }
}

function close() {
  open.value = false
}

function openPanel() {
  open.value = true
  nextTick(positionPanel)
}

function toggle() {
  if (props.disabled) return
  if (open.value) close()
  else openPanel()
}

function select(option: SelectOption) {
  emit("update:modelValue", option.value)
  emit("change", option.value)
  close()
}

function onDocPointerDown(event: MouseEvent) {
  const target = event.target as Node
  if (rootRef.value?.contains(target) || panelRef.value?.contains(target)) return
  close()
}

// 页面滚动时关闭面板；但面板内部滚动（滚动选项列表）不应关闭
function onWindowScroll(event: Event) {
  const target = event.target
  if (target instanceof Node && panelRef.value?.contains(target)) return
  close()
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" || event.key === "Tab") {
    close()
    return
  }
  if (event.key === "Enter" || event.key === " " || event.key === "ArrowDown") {
    event.preventDefault()
    if (open.value) close()
    else openPanel()
  }
}

watch(open, (value) => {
  if (value) {
    document.addEventListener("mousedown", onDocPointerDown)
    window.addEventListener("resize", positionPanel)
    window.addEventListener("scroll", onWindowScroll, true)
  } else {
    document.removeEventListener("mousedown", onDocPointerDown)
    window.removeEventListener("resize", positionPanel)
    window.removeEventListener("scroll", onWindowScroll, true)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", onDocPointerDown)
  window.removeEventListener("resize", positionPanel)
  window.removeEventListener("scroll", onWindowScroll, true)
})
</script>

<template>
  <div
    ref="rootRef"
    class="cs"
    :class="[{ 'is-open': open, 'is-disabled': disabled }, `cs-${size}`]"
  >
    <button
      ref="triggerRef"
      type="button"
      class="cs-trigger"
      :disabled="disabled"
      :aria-expanded="open"
      @click="toggle"
      @keydown="onKeydown"
    >
      <span class="cs-label" :class="{ 'is-placeholder': !selectedOption }">
        {{ selectedOption ? selectedOption.label : placeholder }}
      </span>
      <svg class="cs-arrow" viewBox="0 0 24 24" aria-hidden="true">
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>

    <Teleport to="body">
      <Transition name="cs-fade">
        <div v-if="open" ref="panelRef" class="cs-panel" :style="panelStyle" role="listbox">
          <button
            v-for="option in options"
            :key="option.value"
            type="button"
            class="cs-option"
            :class="{ 'is-active': String(option.value) === String(modelValue ?? '') }"
            role="option"
            :aria-selected="String(option.value) === String(modelValue ?? '')"
            @click="select(option)"
          >
            {{ option.label }}
          </button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.cs {
  position: relative;
  min-width: 0;
}

.cs-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  box-sizing: border-box;
  padding: 8px 12px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.4;
  color: var(--cs-text, #111827);
  background: #fff;
  border: 1px solid var(--cs-border, #d1d5db);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
}

.cs-sm .cs-trigger {
  padding: 5px 10px;
  font-size: 12px;
}

.cs-trigger:hover {
  border-color: var(--cs-border-hover, #9ca3af);
  background: var(--cs-bg-hover, #f9fafb);
}

.cs-trigger:focus-visible {
  outline: none;
}

.cs.is-open .cs-trigger {
  border-color: var(--cs-accent, #3b82f6);
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--cs-accent, #3b82f6);
}

.cs.is-disabled .cs-trigger {
  opacity: 0.6;
  cursor: not-allowed;
}

.cs-label {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.cs-label.is-placeholder {
  color: var(--cs-placeholder, #9ca3af);
}

.cs-arrow {
  flex: none;
  width: 16px;
  height: 16px;
  fill: none;
  stroke: var(--cs-arrow-color, #6b7280);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: transform 0.22s ease, stroke 0.22s ease;
}

.cs.is-open .cs-arrow {
  transform: rotate(180deg);
  stroke: var(--cs-accent, #3b82f6);
}

.cs-panel {
  position: fixed;
  z-index: 3000;
  box-sizing: border-box;
  max-height: 260px;
  overflow-y: auto;
  padding: 6px;
  background: #fff;
  border: 1px solid var(--cs-panel-border, #e5e7eb);
  border-radius: 10px;
  box-shadow: 0 10px 24px -6px rgba(15, 23, 42, 0.18), 0 4px 10px -4px rgba(15, 23, 42, 0.1);
}

.cs-option {
  display: block;
  width: 100%;
  box-sizing: border-box;
  margin: 0;
  padding: 8px 10px;
  text-align: left;
  font-size: 13px;
  font-family: inherit;
  line-height: 1.4;
  color: var(--cs-text, #334155);
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  white-space: normal;
  transition: background-color 0.15s ease, color 0.15s ease, padding-left 0.15s ease;
}

.cs-option:hover {
  padding-left: 14px;
  background: var(--cs-option-hover, #f1f5f9);
  color: var(--cs-text-strong, #0f172a);
}

.cs-option.is-active {
  color: var(--cs-accent, #3b82f6);
  font-weight: 600;
  background: var(--cs-option-active, rgba(59, 130, 246, 0.08));
}

.cs-fade-enter-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.cs-fade-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}

.cs-fade-enter-from,
.cs-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>