<template>
  <div class="chat-window" ref="chatContainer">
    <!-- Welcome message -->
    <div v-if="messages.length === 0" class="welcome">
      <h2>Welcome to C&S Wholesale Groceries Assistant</h2>
      <p>Your cybersecurity assistant for incident response, threat analysis, and security best practices.</p>
      
      <div class="suggestions">
        <div 
          class="suggestion-chip" 
          @click="$emit('sendSuggestion', 'How do I triage a suspicious email?')"
        >
           Triage Phishing Email
        </div>
        <div 
          class="suggestion-chip"
          @click="$emit('sendSuggestion', 'Summarize best practices for MFA rollout')"
        >
           MFA Best Practices
        </div>
        <div 
          class="suggestion-chip"
          @click="$emit('sendSuggestion', 'What should be in an incident response plan?')"
        >
           Incident Response
        </div>
        <div 
          class="suggestion-chip"
          @click="$emit('sendSuggestion', 'How to secure AWS S3 buckets?')"
        >
          Cloud Security
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div 
      v-for="msg in messages" 
      :key="msg.id" 
      :class="['message', msg.type]"
    >
      <div>{{ msg.text }}</div>
      <div v-if="msg.timestamp" class="timestamp">{{ msg.timestamp }}</div>
    </div>

    <!-- Typing indicator -->
    <div v-if="isTyping" class="message bot">
      <div class="typing">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick } from 'vue';

export default {
  name: 'ChatWindow',
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    isTyping: {
      type: Boolean,
      default: false
    }
  },
  emits: ['sendSuggestion'],
  setup(props) {
    const chatContainer = ref(null);

    const scrollToBottom = () => {
      nextTick(() => {
        if (chatContainer.value) {
          chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
        }
      });
    };

    watch(() => props.messages.length, scrollToBottom);
    watch(() => props.isTyping, scrollToBottom);

    return {
      chatContainer
    };
  }
};
</script>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  background: rgba(15, 24, 48, 0.6);
  border: 1px solid #22335f;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  scroll-behavior: smooth;
}

.chat-window::-webkit-scrollbar {
  width: 8px;
}

.chat-window::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.chat-window::-webkit-scrollbar-thumb {
  background: rgba(74, 158, 255, 0.3);
  border-radius: 4px;
}

.welcome {
  text-align: center;
  padding: 40px 20px;
  opacity: 0.8;
}

.welcome h2 {
  color: #4a9eff;
  margin-bottom: 12px;
  font-size: 24px;
}

.welcome p {
  color: #8fa3c8;
  line-height: 1.6;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.suggestion-chip {
  padding: 8px 16px;
  background: rgba(74, 158, 255, 0.1);
  border: 1px solid rgba(74, 158, 255, 0.3);
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  background: rgba(74, 158, 255, 0.2);
  border-color: #4a9eff;
  transform: translateY(-2px);
}

.message {
  margin: 16px 0;
  padding: 14px 18px;
  border-radius: 12px;
  white-space: pre-wrap;
  max-width: 85%;
  line-height: 1.6;
  animation: fadeIn 0.3s ease-in;
  word-wrap: break-word;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user {
  background: linear-gradient(135deg, #1a2a55 0%, #2d3f6f 100%);
  margin-left: auto;
  text-align: right;
  border: 1px solid #2d3f6f;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.bot {
  background: rgba(20, 34, 68, 0.8);
  border: 1px solid #22335f;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #fca5a5;
}

.typing {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
}

.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4a9eff;
  animation: typing 1.4s infinite;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
  30% { transform: translateY(-10px); opacity: 1; }
}

.timestamp {
  font-size: 11px;
  opacity: 0.5;
  margin-top: 6px;
}
</style>
