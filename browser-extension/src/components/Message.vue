<script lang="ts" setup>
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/base16/gigavolt.min.css'
import MarkdownItPlantuml from 'markdown-it-plantuml'
import { CircleFilledIcon, ExclamationCircleIcon } from 'vue-tabler-icons'
import CopyButton from './CopyButton.vue'
import NewPromptButton from './NewPromptButton.vue'
import Collapsible from './Collapsible.vue'

const props = defineProps<{
  text: string
  file: Record<string, string>
  isUser: boolean
  isComplete: boolean
  isSuccess: boolean
  agentLogo: string
  agentName: string
  agentId: string
  reasoningSteps?: string[]
  finalAnswer?: string
}>()

const { t } = useI18n()
const emit = defineEmits(['stopReasoning', 'content-updated'])
const showReasoningPanel = ref(true)
const showFinalAnswer   = ref(false)
const showFinalDarkCollapsible = ref(false)
const showButtonStopReasoning = ref(true)
const revealedSteps = ref<string[]>([])
let collapseTimer: ReturnType<typeof setTimeout> | null = null

function renderMarkdown(text: string) {
  const md = new MarkdownIt({
    highlight: (code, lang) => {
      if (lang && hljs.getLanguage(lang)) {
        try { return hljs.highlight(code, { language: lang }).value } catch {}
      }
      return code
    }
  })
  md.use(MarkdownItPlantuml)
  const defaultRender = md.renderer.rules.link_open
  md.renderer.rules.link_open = (tokens, idx, opts, env, self) => {
    tokens[idx].attrSet('target', '_blank')
    return (defaultRender || self.renderToken)(tokens, idx, opts, env, self)
  }
  return md.render(text)
}

const renderedMsg = computed(() =>
  props.isUser ? props.text.replace(/\n/g, '<br/>') : renderMarkdown(props.text)
)

const renderedFinal = computed(() =>
  props.finalAnswer ? renderMarkdown(props.finalAnswer) : ''
)

const displaySteps = computed(() => {
  const steps = props.reasoningSteps ? [...props.reasoningSteps] : []
  return [
    'Analizando pedido del usuario',
    'Elaborando respuesta',
    ...steps
  ]
})

const formattedReasoningContent = computed(() => {
  const content = revealedSteps.value.map(line => line.trim()).join('<br/><br/>')
  emit('content-updated')
  return content
})

watch(
  () => props.reasoningSteps?.length,
  (len) => {
    if (len && len > 0) {
      showReasoningPanel.value = true
    }
  },
  { immediate: true }
)

watch(
  () => props.finalAnswer,
  (fa) => {
    if (!fa) return
    if (!props.reasoningSteps?.length) {
      showFinalAnswer.value = true
      return
    }
    if (collapseTimer) clearTimeout(collapseTimer)
    collapseTimer = setTimeout(() => {
      showReasoningPanel.value = false
      showFinalAnswer.value   = true
      showFinalDarkCollapsible.value = true
    }, 7000)
  }
)

watch(
  () => displaySteps.value,
  (allSteps) => {
    revealedSteps.value = []
    let idx = 0
    const timer = setInterval(() => {
      revealedSteps.value.push(allSteps[idx++])
      if (idx >= allSteps.length) {
        clearInterval(timer)
        showFinalAnswer.value = true
      }
    }, 500)
  },
  { immediate: true }
)

function handleStopReasoning() {
  if (collapseTimer) clearTimeout(collapseTimer)
  showButtonStopReasoning.value = false
  emit('stopReasoning')
}

onBeforeUnmount(() => {
  if (collapseTimer) clearTimeout(collapseTimer)
})
</script>

<template>
  <div
    class="flex flex-col mb-1 p-1 min-w-7"
    :class="!isSuccess ? ['border-red-500','border-b'] : []"
  >
    <div class="flex items-center flex-row">
      <template v-if="isUser">
        <CircleFilledIcon class="text-violet-600" />
      </template>
      <template v-else-if="!isUser && isSuccess">
        <img :src="agentLogo" class="w-5 mr-1 rounded-full" />
      </template>
      <template v-else>
        <ExclamationCircleIcon class="text-red-600" />
      </template>
      <span class="text-base">{{ isUser ? t('you') : agentName }}</span>
      <div class="flex-auto flex justify-end">
        <CopyButton
          v-if="!isUser && text"
          :text="text"
          :html="renderedMsg"
        />
        <NewPromptButton
          v-if="isUser && text"
          :is-large-icon="false"
          :text="text"
          :agent-id="agentId"
        />
      </div>
    </div>

    <div class="mt-2 ml-8 mr-2">
      <template v-if="file.data">
        <audio controls>
          <source :src="file.url" type="audio/webm" />
        </audio>
      </template>

      <template v-if="isUser || props.text !== ''">
        <div v-html="renderedMsg" class="mt-2 p-2 bg-white rounded text-gray-800 text-sm" />
      </template>

      <template
        v-else-if="!props.reasoningSteps?.length && props.finalAnswer"
      >
        <div v-html="renderedFinal" class="mt-2 p-2 bg-white rounded text-gray-800 text-sm" />
      </template>

      <template v-else-if="props.reasoningSteps?.length && showButtonStopReasoning">
        <Collapsible
          v-model:open="showReasoningPanel"
          :title="showReasoningPanel ? 'Ocultar razonamiento' : 'Ver razonamiento'"
          @stop="handleStopReasoning"
          @content-updated="$emit('content-updated')"
          :content="formattedReasoningContent"
          :show-button-visible="showFinalDarkCollapsible"
        />
        <div
          v-if="props.finalAnswer && showFinalDarkCollapsible"
          v-html="renderedFinal"
          class="mt-2 p-2 bg-white rounded text-gray-800 text-sm"
        />
      </template>
      <template v-else-if="!showButtonStopReasoning">
        <div v-html="'The reasoning was stopped. ✋'" class="mt-2 p-2 bg-white rounded text-gray-800 text-sm" />
      </template>

      <div class="dot-pulse" v-if="!isComplete" />
    </div>
  </div>
</template>

<style lang="scss">
@use 'three-dots' with (
  $dot-width: 5px,
  $dot-height: 5px,
  $dot-color: var(--accent-color)
);

.rendered-msg pre {
  padding: 15px;
  background: #202126;
  border-radius: 8px;
  word-wrap: break-word;
}

/* Fix: Inadequate gap between code blocks within list items. */
.rendered-msg li pre {
  margin-bottom: 10px;
}

.rendered-msg pre {
  box-shadow: var(--shadow);
}

.rendered-msg pre code.hljs {
  padding: 0px;
}

div a {
  color: var(--accent-color);
  text-decoration: none;
}

.rendered-msg table {
  width: 100%;
  box-shadow: var(--shadow);
}

.rendered-msg thead tr {
  background-color: #ece6f5;
}

.rendered-msg th,
.rendered-msg td {
  padding: var(--half-spacing);
  border: var(--border);
}

.rendered-msg tbody tr:hover {
  background-color: #f1f1f1;
}

.echarts {
  box-shadow: var(--shadow);
  border-radius: var(--spacing);
  width: 100%;
  padding: var(--half-spacing);
}

.rendered-msg > img {
  box-shadow: var(--shadow);
  border-radius: var(--spacing);
  width: fit-content;
}
</style>

<i18n>
{
  "en": {
    "you": "You"
  },
  "es": {
    "you": "Tú"
  }
}
</i18n>
