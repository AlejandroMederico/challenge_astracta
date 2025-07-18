<script lang="ts" setup>
import { ref, nextTick, watch, computed } from 'vue'
import { SettingsIcon } from 'vue-tabler-icons'
import { ChatMessage } from '../scripts/tab-state'
import CopilotName from './CopilotName.vue'
import Message from './Message.vue'
import ChatInput from './ChatInput.vue'
import CopilotConfig from './CopilotConfig.vue'
import PageOverlay from './PageOverlay.vue'
import BtnClose from './BtnClose.vue'

const props = defineProps<{ 
  agentId: string,
  agentName: string,
  agentLogo: string,
  agentCapabilities: string[],
  messages: ChatMessage[]
}>()
const emit = defineEmits<{
  (e: 'close'): void,
  (e: 'userMessage',
  text: string,
  file: Record<string, string>): void
}>()

const messagesDiv = ref<HTMLElement | null>(null)
const showConfig = ref(false)

function scrollToBottom() {
  if (!messagesDiv.value) return
  requestAnimationFrame(() => {
    messagesDiv.value!.scrollTop = messagesDiv.value!.scrollHeight
  })
}

watch(
  () => props.messages,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

function onContentUpdated() {
  scrollToBottom()
}


const onUserMessage = async (text: string, file: Record<string, string>) => {
  emit('userMessage', text, file)
}

const lastMessage = computed((): ChatMessage => props.messages[props.messages.length - 1])
</script>

<template>
  <PageOverlay>
    <template v-slot:headerContent>
      <img :src="agentLogo" class="w-7 h-7" />
      <div class="text-xl font-semibold">
        <CopilotName :agentName="agentName" />
      </div>
    </template>
    <template v-slot:headerActions>
      <button @click="showConfig = true"><settings-icon /></button>
      <BtnClose @click="$emit('close')" />
    </template>
    <template v-slot:content>
      <div class="h-full flex flex-col">
        <div
          ref="messagesDiv"
          class="flex-1 overflow-y-auto mb-4"
        >
          <Message
            v-for="message in messages"
            :text="message.text"
            :file="message.file"
            :is-user="message.isUser"
            @content-updated="onContentUpdated"
            :is-complete="message.isComplete"
            :is-success="message.isSuccess"
            :agent-logo="agentLogo"
            :agent-name="agentName"
            :agent-id="agentId"
            :reasoning-steps="message.reasoningSteps || []"
            :final-answer="message.finalAnswer"
          />
        </div>
        <ChatInput
          :can-send-message="lastMessage.isComplete"
          :agent-id="agentId"
          :support-recording="agentCapabilities.includes('transcripts')"
          @send-message="onUserMessage"
        />
      </div>
    </template>
    <template v-slot:modalsContainer>
      <CopilotConfig
        :show="showConfig"
        :agent-id="agentId"
        :agent-name="agentName"
        :agent-logo="agentLogo"
        @close="showConfig = false" />
    </template>
  </PageOverlay>
</template>
