<template>
  <div class="app-container">
    <Header :status="status" @reset="resetChat" />
    
    <div class="container">
      <ChatWindow 
        :messages="messages" 
        :isTyping="isTyping"
        @sendSuggestion="sendSuggestion"
      />
      
      <ChatInput 
        v-model="inputMessage"
        :disabled="isTyping"
        @send="sendMessage"
      />
      
      <div class="hint">
         Tip: I maintain conversation context, so you can ask follow-up questions naturally
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Header from './components/Header.vue';
import ChatWindow from './components/ChatWindow.vue';
import ChatInput from './components/ChatInput.vue';

export default {
  name: 'App',
  components: {
    Header,
    ChatWindow,
    ChatInput
  },
  setup() {
    const messages = ref([]);
    const inputMessage = ref('');
    const isTyping = ref(false);
    const status = ref('Connected');
    const sessionId = ref(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

    const API_BASE = 'http://localhost:3001';

    const checkHealth = async () => {
      try {
        await axios.get(`${API_BASE}/health`);
        status.value = 'Connected';
      } catch (error) {
        status.value = 'Backend offline';
        console.error('Health check failed:', error);
      }
    };

    const sendSuggestion = (text) => {
      inputMessage.value = text;
      sendMessage();
    };

    const sendMessage = async () => {
      const message = inputMessage.value.trim();
      if (!message || isTyping.value) return;

      // Add user message
      messages.value.push({
        id: Date.now(),
        type: 'user',
        text: message,
        timestamp: new Date().toLocaleTimeString()
      });

      inputMessage.value = '';
      isTyping.value = true;
      status.value = 'Thinking...';

      try {
        const response = await axios.post(`${API_BASE}/chat`, {
          message,
          sessionId: sessionId.value
        });

        messages.value.push({
          id: Date.now() + 1,
          type: 'bot',
          text: response.data.reply || 'No reply',
          timestamp: new Date().toLocaleTimeString()
        });

        status.value = 'Connected';
      } catch (error) {
        messages.value.push({
          id: Date.now() + 1,
          type: 'error',
          text: `Error: ${error.response?.data?.error || error.message}`
        });
        status.value = 'Connection failed';
        console.error('Error:', error);
      } finally {
        isTyping.value = false;
      }
    };

    const resetChat = async () => {
      if (!confirm('Are you sure you want to reset the conversation?')) {
        return;
      }

      try {
        await axios.post(`${API_BASE}/reset`, {
          sessionId: sessionId.value
        });

        messages.value = [];
        status.value = 'Reset successful';
        
        setTimeout(() => {
          status.value = 'Connected';
        }, 2000);
      } catch (error) {
        console.error('Reset error:', error);
        status.value = 'Reset failed';
      }
    };

    onMounted(() => {
      checkHealth();
    });

    return {
      messages,
      inputMessage,
      isTyping,
      status,
      sendMessage,
      sendSuggestion,
      resetChat
    };
  }
};
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.hint {
  opacity: 0.6;
  font-size: 13px;
  margin-top: 12px;
  text-align: center;
  color: #8fa3c8;
}
</style>
