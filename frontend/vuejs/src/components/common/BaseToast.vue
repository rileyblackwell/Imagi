<template>
  <Teleport to="body">
    <Transition name="toast">
      <div 
        v-if="show"
        class="toast-container"
        :class="[
          position,
          variant,
          { 'with-icon': icon }
        ]"
        role="alert"
      >
        <i v-if="icon" :class="icon" class="toast-icon"></i>
        
        <div class="toast-content">
          <div v-if="title" class="toast-title">{{ title }}</div>
          <div class="toast-message">{{ message }}</div>
        </div>
        
        <button 
          v-if="dismissible"
          class="toast-close"
          @click="dismiss"
          aria-label="Close toast"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
export default {
  name: 'BaseToast',
  
  props: {
    show: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: null
    },
    message: {
      type: String,
      required: true
    },
    variant: {
      type: String,
      default: 'info',
      validator: value => ['info', 'success', 'warning', 'error'].includes(value)
    },
    position: {
      type: String,
      default: 'top-right',
      validator: value => [
        'top-left',
        'top-center',
        'top-right',
        'bottom-left',
        'bottom-center',
        'bottom-right'
      ].includes(value)
    },
    duration: {
      type: Number,
      default: 5000
    },
    dismissible: {
      type: Boolean,
      default: true
    },
    icon: {
      type: String,
      default: null
    }
  },
  
  emits: ['update:show'],
  
  data() {
    return {
      timeout: null
    }
  },
  
  watch: {
    show(newVal) {
      if (newVal && this.duration > 0) {
        this.setAutoDismiss()
      }
    }
  },
  
  mounted() {
    if (this.show && this.duration > 0) {
      this.setAutoDismiss()
    }
  },
  
  beforeUnmount() {
    if (this.timeout) {
      clearTimeout(this.timeout)
    }
  },
  
  methods: {
    dismiss() {
      this.$emit('update:show', false)
    },
    
    setAutoDismiss() {
      if (this.timeout) {
        clearTimeout(this.timeout)
      }
      
      this.timeout = setTimeout(() => {
        this.dismiss()
      }, this.duration)
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  min-width: 300px;
  max-width: 400px;
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  z-index: 1100;
}

/* Positions */
.top-left {
  top: 20px;
  left: 20px;
}

.top-center {
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.top-right {
  top: 20px;
  right: 20px;
}

.bottom-left {
  bottom: 20px;
  left: 20px;
}

.bottom-center {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.bottom-right {
  bottom: 20px;
  right: 20px;
}

/* Variants */
.info {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.1),
    rgba(0, 255, 204, 0.1)
  );
  border-color: rgba(99, 102, 241, 0.2);
}

.success {
  background: linear-gradient(135deg, 
    rgba(0, 255, 204, 0.1),
    rgba(0, 162, 255, 0.1)
  );
  border-color: rgba(0, 255, 204, 0.2);
}

.warning {
  background: linear-gradient(135deg, 
    rgba(255, 171, 64, 0.1),
    rgba(255, 196, 0, 0.1)
  );
  border-color: rgba(255, 171, 64, 0.2);
}

.error {
  background: linear-gradient(135deg, 
    rgba(255, 71, 87, 0.1),
    rgba(255, 126, 126, 0.1)
  );
  border-color: rgba(255, 71, 87, 0.2);
}

.toast-icon {
  font-size: 1.2rem;
  margin-top: 2px;
}

.info .toast-icon {
  color: #6366f1;
}

.success .toast-icon {
  color: #00ffcc;
}

.warning .toast-icon {
  color: #ffab40;
}

.error .toast-icon {
  color: #ff4757;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
  color: var(--global-text-color);
}

.toast-message {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.toast-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  margin: -4px;
  margin-left: 8px;
}

.toast-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Transition animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Gradient border effect */
.toast-container::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: 12px;
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.2),
    rgba(0, 255, 204, 0.2)
  );
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

/* Responsive */
@media (max-width: 480px) {
  .toast-container {
    width: calc(100% - 40px);
    max-width: none;
  }
  
  .top-center,
  .bottom-center {
    left: 20px;
    transform: none;
  }
}
</style> 