<template>
  <header>
    <div class="header-left">
      <div class="logo">🏪 C&S Wholesale Groceries</div>
      <div class="subtitle">Cybersecurity Assistant</div>
    </div>
    <div class="header-right">
      <div class="status">
        <span class="status-dot"></span>
        <span>{{ status }}</span>
      </div>
      <button class="btn btn-danger" @click="$emit('reset')">
        Reset Chat
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Header',
  props: {
    status: {
      type: String,
      default: 'Connected'
    }
  },
  emits: ['reset']
};
</script>

<style scoped>
header {
  padding: 16px 24px;
  background: rgba(17, 27, 51, 0.95);
  border-bottom: 1px solid #22335f;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #4a9eff 0%, #7b68ee 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  opacity: 0.7;
  font-size: 14px;
  color: #8fa3c8;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 6px 12px;
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.1);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #22335f;
  background: rgba(15, 24, 48, 0.8);
  color: #e8eefc;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  font-weight: 500;
}

.btn:hover {
  background: rgba(34, 51, 95, 0.8);
  border-color: #4a9eff;
  transform: translateY(-1px);
}

.btn-danger {
  border-color: #ef4444;
  color: #fca5a5;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #dc2626;
}
</style>
