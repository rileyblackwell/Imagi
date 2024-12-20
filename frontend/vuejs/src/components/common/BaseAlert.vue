<template>
  <Transition name="alert">
    <div 
      v-if="modelValue"
      class="alert"
      :class="[
        variant,
        { 'is-dismissible': dismissible },
        { 'has-icon': icon || defaultIcon }
      ]"
      role="alert"
    >
      <i 
        v-if="icon || defaultIcon" 
        :class="icon || defaultIcon"
        class="alert-icon"
      ></i>
      
      <div class="alert-content">
        <div v-if="title" class="alert-title">{{ title }}</div>
        <div class="alert-message">
          <slot>{{ message }}</slot>
        </div>
      </div>
      
      <button 
        v-if="dismissible"
        class="alert-close"
        @click="dismiss"
        aria-label="Close alert"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>
  </Transition>
</template>

<script>
export default {
  name: 'BaseAlert',
  
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: null
    },
    message: {
      type: String,
      default: null
    },
    variant: {
      type: String,
      default: 'info',
      validator: value => [
        'info',
        'success',
        'warning',
        'error'
      ].includes(value)
    },
    icon: {
      type: String,
      default: null
    },
    dismissible: {
      type: Boolean,
      default: true
    },
    duration: {
      type: Number,
      default: 0
    }
  },
  
  emits: ['update:modelValue'],
  
  data() {
    return {
      timeout: null
    }
  },
  
  computed: {
    defaultIcon() {
      if (this.icon) return null
      
      const icons = {
        info: 'fas fa-info-circle',
        success: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-triangle',
        error: 'fas fa-times-circle'
      }
      
      return icons[this.variant]
    }
  },
  
  watch: {
    modelValue(newVal) {
      if (newVal && this.duration > 0) {
        this.setAutoDismiss()
      }
    }
  },
  
  mounted() {
    if (this.modelValue && this.duration > 0) {
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
      this.$emit('update:modelValue', false)
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
.alert {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  overflow: hidden;
}

/* Variants */
.alert.info {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.1),
    rgba(0, 255, 204, 0.1)
  );
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.alert.success {
  background: linear-gradient(135deg, 
    rgba(0, 255, 204, 0.1),
    rgba(0, 162, 255, 0.1)
  );
  border: 1px solid rgba(0, 255, 204, 0.2);
}

.alert.warning {
  background: linear-gradient(135deg, 
    rgba(255, 171, 64, 0.1),
    rgba(255, 196, 0, 0.1)
  );
  border: 1px solid rgba(255, 171, 64, 0.2);
}

.alert.error {
  background: linear-gradient(135deg, 
    rgba(255, 71, 87, 0.1),
    rgba(255, 126, 126, 0.1)
  );
  border: 1px solid rgba(255, 71, 87, 0.2);
}

/* Icon */
.alert-icon {
  font-size: 1.25rem;
  margin-top: 2px;
}

.info .alert-icon {
  color: #6366f1;
}

.success .alert-icon {
  color: #00ffcc;
}

.warning .alert-icon {
  color: #ffab40;
}

.error .alert-icon {
  color: #ff4757;
}

/* Content */
.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
  color: var(--global-text-color);
}

.alert-message {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

/* Close button */
.alert-close {
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

.alert-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Transition animations */
.alert-enter-active,
.alert-leave-active {
  transition: all 0.3s ease;
  max-height: 200px;
  opacity: 1;
  margin-bottom: 16px;
}

.alert-enter-from,
.alert-leave-to {
  max-height: 0;
  opacity: 0;
  margin-bottom: 0;
}

/* Gradient border effect */
.alert::before {
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

/* Spacing adjustments */
.alert:not(:last-child) {
  margin-bottom: 16px;
}

.alert.has-icon .alert-content {
  padding-left: 4px;
}

.alert.is-dismissible .alert-content {
  padding-right: 4px;
}
</style> 