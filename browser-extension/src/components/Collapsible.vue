<script setup lang="ts">
import { ref, watch } from 'vue'
import { ChevronUpIcon, ChevronDownIcon } from 'vue-tabler-icons'

const props = defineProps<{
  title: string
  content: string
  open?: boolean
  showButtonVisible?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', open: boolean): void
  (e: 'stop'): void
  (e: 'content-updated'): void
}>()

const visible = ref(props.open ?? false)
watch(() => props.open, v => {
  if (v !== undefined) visible.value = v
})

watch(() => props.content, () => {
  emit('content-updated')
})

function toggleVisible() {
  visible.value = !visible.value
  emit('update:open', visible.value)
}

function onStop() {
  emit('stop')
}
</script>

<template>
  <div
    class="collapsible border rounded overflow-hidden shadow p-4 max-w-full
           bg-purple-100 text-gray-900 border-purple-300"
  >
    <div
      class="flex items-center justify-between cursor-pointer select-none"
      @click="toggleVisible"
    >
    <h3 class="font-semibold text-base inline-flex items-center space-x-1 cursor-pointer select-none">
      <ChevronUpIcon v-if="visible" class="w-4 h-4" />
      <ChevronDownIcon v-else class="w-4 h-4" />
      <span>{{ visible ? ' Ocultar razonamiento' : ' Ver razonamiento' }}</span>
    </h3>
      <button
        v-if="visible && !showButtonVisible"
        @click.stop="onStop"
        class="text-white px-2 py-1 rounded bg-purple-700 hover:bg-purple-800 transition-colors text-xs whitespace-nowrap max-w-max inline-flex"
        aria-label="Cerrar"
      >
        Stop
      </button>
    </div>

    <transition name="fade-slide">
      <div
        v-show="visible"
        class="mt-2 text-base leading-relaxed whitespace-pre-wrap break-words font-sans"
      >
        <p v-html="content" />
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* Animación fade-slide para abrir/cerrar */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>
