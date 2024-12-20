<template>
  <div class="dropdown-wrapper" v-click-outside="close">
    <div 
      class="dropdown-trigger"
      :class="{ 'is-active': isOpen }"
      @click="toggle"
    >
      <slot name="trigger">
        <button class="trigger-button">
          {{ label }}
          <i class="fas fa-chevron-down chevron-icon" :class="{ 'is-open': isOpen }"></i>
        </button>
      </slot>
    </div>
    
    <Transition name="dropdown">
      <div 
        v-if="isOpen"
        class="dropdown-menu"
        :class="[position, size]"
        :style="{ width }"
      >
        <div class="dropdown-content">
          <slot></slot>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
export default {
  name: 'BaseDropdown',
  
  props: {
    label: {
      type: String,
      default: 'Select'
    },
    position: {
      type: String,
      default: 'bottom-start',
      validator: value => [
        'top-start',
        'top-end',
        'bottom-start',
        'bottom-end'
      ].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: value => ['sm', 'md', 'lg'].includes(value)
    },
    width: {
      type: String,
      default: 'auto'
    }
  },
  
  data() {
    return {
      isOpen: false
    }
  },
  
  methods: {
    toggle() {
      this.isOpen = !this.isOpen
    },
    
    close() {
      this.isOpen = false
    }
  },
  
  directives: {
    'click-outside': {
      mounted(el, binding) {
        el.clickOutsideEvent = function(event) {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value(event)
          }
        }
        document.addEventListener('click', el.clickOutsideEvent)
      },
      unmounted(el) {
        document.removeEventListener('click', el.clickOutsideEvent)
      }
    }
  }
}
</script>

<style scoped>
.dropdown-wrapper {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  cursor: pointer;
}

.trigger-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--global-text-color);
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.trigger-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.dropdown-trigger.is-active .trigger-button {
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.chevron-icon {
  font-size: 0.8rem;
  transition: transform 0.2s ease;
}

.chevron-icon.is-open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  min-width: 200px;
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  z-index: 1000;
  margin-top: 8px;
}

/* Positions */
.bottom-start {
  top: 100%;
  left: 0;
}

.bottom-end {
  top: 100%;
  right: 0;
}

.top-start {
  bottom: 100%;
  left: 0;
  margin-top: 0;
  margin-bottom: 8px;
}

.top-end {
  bottom: 100%;
  right: 0;
  margin-top: 0;
  margin-bottom: 8px;
}

/* Sizes */
.dropdown-menu.sm {
  font-size: 0.875rem;
}

.dropdown-menu.md {
  font-size: 0.95rem;
}

.dropdown-menu.lg {
  font-size: 1rem;
}

.dropdown-content {
  padding: 8px;
}

/* Transition animations */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Gradient border effect */
.dropdown-menu::before {
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

/* Default slot styles */
:slotted(a),
:slotted(button) {
  display: block;
  width: 100%;
  padding: 8px 12px;
  color: var(--global-text-color);
  text-decoration: none;
  border: none;
  background: transparent;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

:slotted(a:hover),
:slotted(button:hover) {
  background: rgba(255, 255, 255, 0.1);
}

:slotted(.dropdown-divider) {
  height: 1px;
  margin: 8px 0;
  background: rgba(255, 255, 255, 0.1);
}

:slotted(.dropdown-header) {
  padding: 8px 12px;
  font-size: 0.875em;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}
</style> 