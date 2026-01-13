<template>
  <div class="controls">
    <div class="input-wrapper">
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @keydown.enter="$emit('send')"
        :disabled="disabled"
        placeholder="Ask about security incidents, policies, cloud hardening..."
        ref="inputField"
      />
    </div>
    <button 
      @click="$emit('send')" 
      :disabled="disabled || !modelValue.trim()"
    >
      Send
    </button>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'ChatInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'send'],
  setup() {
    const inputField = ref(null);

    onMounted(() => {
      inputField.value?.focus();
    });

    return {
      inputField
    };
  }
};
</script>

<style scoped>
.controls {
  display: flex;
  gap: 12px;
  background: rgba(15, 24, 48, 0.8);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #22335f;
}

.input-wrapper {
  flex: 1;
}

input {
  width: 100%;
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px solid #22335f;
  background: rgba(15, 24, 48, 0.9);
  color: #e8eefc;
  font-size: 15px;
  transition: all 0.2s;
  outline: none;
}

input:focus {
  border-color: #4a9eff;
  box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
}

input::placeholder {
  color: #6b7a99;
}

input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button {
  padding: 14px 28px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #4a9eff 0%, #7b68ee 100%);
  color: white;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(74, 158, 255, 0.4);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style>
