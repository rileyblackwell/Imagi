<template>
  <div 
    class="avatar"
    :class="[
      size,
      variant,
      { 'is-online': status === 'online' },
      { 'is-away': status === 'away' },
      { 'is-busy': status === 'busy' },
      { 'is-offline': status === 'offline' }
    ]"
    :style="{ backgroundColor: bgColor }"
  >
    <img 
      v-if="src"
      :src="src"
      :alt="alt"
      class="avatar-image"
      @error="handleImageError"
    >
    
    <span v-else-if="initials" class="avatar-initials">
      {{ initials }}
    </span>
    
    <i v-else :class="icon || 'fas fa-user'" class="avatar-icon"></i>
    
    <span v-if="status" class="status-indicator"></span>
    
    <div v-if="$slots.badge" class="avatar-badge">
      <slot name="badge"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseAvatar',
  
  props: {
    src: {
      type: String,
      default: null
    },
    alt: {
      type: String,
      default: 'Avatar'
    },
    initials: {
      type: String,
      default: null,
      validator: value => !value || value.length <= 3
    },
    icon: {
      type: String,
      default: null
    },
    size: {
      type: String,
      default: 'md',
      validator: value => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
    },
    variant: {
      type: String,
      default: 'circle',
      validator: value => ['circle', 'square', 'rounded'].includes(value)
    },
    status: {
      type: String,
      default: null,
      validator: value => !value || ['online', 'away', 'busy', 'offline'].includes(value)
    },
    bgColor: {
      type: String,
      default: null
    }
  },
  
  data() {
    return {
      hasError: false
    }
  },
  
  methods: {
    handleImageError() {
      this.hasError = true
      this.$emit('error')
    }
  }
}
</script>

<style scoped>
.avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--global-text-color);
  font-weight: 500;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

/* Sizes */
.avatar.xs {
  width: 24px;
  height: 24px;
  font-size: 0.75rem;
}

.avatar.sm {
  width: 32px;
  height: 32px;
  font-size: 0.875rem;
}

.avatar.md {
  width: 40px;
  height: 40px;
  font-size: 1rem;
}

.avatar.lg {
  width: 48px;
  height: 48px;
  font-size: 1.25rem;
}

.avatar.xl {
  width: 64px;
  height: 64px;
  font-size: 1.5rem;
}

/* Variants */
.avatar.circle {
  border-radius: 50%;
}

.avatar.square {
  border-radius: 12px;
}

.avatar.rounded {
  border-radius: 8px;
}

/* Image */
.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Initials */
.avatar-initials {
  text-transform: uppercase;
  line-height: 1;
}

/* Icon */
.avatar-icon {
  font-size: 0.8em;
  color: rgba(255, 255, 255, 0.8);
}

/* Status indicator */
.status-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 25%;
  height: 25%;
  border-radius: 50%;
  border: 2px solid rgba(30, 30, 30, 0.95);
  background: rgba(255, 255, 255, 0.2);
}

.is-online .status-indicator {
  background: #00ffcc;
}

.is-away .status-indicator {
  background: #ffab40;
}

.is-busy .status-indicator {
  background: #ff4757;
}

.is-offline .status-indicator {
  background: rgba(255, 255, 255, 0.3);
}

/* Badge */
.avatar-badge {
  position: absolute;
  top: 0;
  right: 0;
  transform: translate(25%, -25%);
  z-index: 1;
}

/* Gradient border effect */
.avatar::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
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
  border-radius: inherit;
}

/* Hover effect */
.avatar {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.avatar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style> 