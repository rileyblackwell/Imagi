<template>
  <span 
    class="badge"
    :class="[
      variant,
      size,
      { 'is-dot': dot },
      { 'is-pill': pill },
      { 'is-outlined': outlined },
      { 'has-icon': $slots.icon }
    ]"
  >
    <slot name="icon"></slot>
    <slot v-if="!dot">{{ text }}</slot>
  </span>
</template>

<script>
export default {
  name: 'BaseBadge',
  
  props: {
    text: {
      type: String,
      default: null
    },
    variant: {
      type: String,
      default: 'primary',
      validator: value => [
        'primary',
        'secondary',
        'success',
        'warning',
        'error',
        'info'
      ].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: value => ['sm', 'md', 'lg'].includes(value)
    },
    dot: {
      type: Boolean,
      default: false
    },
    pill: {
      type: Boolean,
      default: false
    },
    outlined: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
  border-radius: 6px;
  transition: all 0.2s ease;
}

/* Sizes */
.badge.sm {
  font-size: 0.75rem;
  padding: 4px 8px;
}

.badge.md {
  font-size: 0.875rem;
  padding: 6px 10px;
}

.badge.lg {
  font-size: 0.95rem;
  padding: 8px 12px;
}

/* Dot variant */
.badge.is-dot {
  width: 8px;
  height: 8px;
  padding: 0;
  border-radius: 50%;
}

.badge.is-dot.sm {
  width: 6px;
  height: 6px;
}

.badge.is-dot.lg {
  width: 10px;
  height: 10px;
}

/* Pill variant */
.badge.is-pill {
  border-radius: 100px;
}

/* Icon styles */
.badge.has-icon {
  padding-left: 8px;
}

:slotted(i) {
  font-size: 0.9em;
}

/* Variants */
.badge.primary {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.1),
    rgba(0, 255, 204, 0.1)
  );
  color: #6366f1;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.badge.secondary {
  background: linear-gradient(135deg, 
    rgba(236, 72, 153, 0.1),
    rgba(0, 255, 204, 0.1)
  );
  color: #ec4899;
  border: 1px solid rgba(236, 72, 153, 0.2);
}

.badge.success {
  background: linear-gradient(135deg, 
    rgba(0, 255, 204, 0.1),
    rgba(0, 162, 255, 0.1)
  );
  color: #00ffcc;
  border: 1px solid rgba(0, 255, 204, 0.2);
}

.badge.warning {
  background: linear-gradient(135deg, 
    rgba(255, 171, 64, 0.1),
    rgba(255, 196, 0, 0.1)
  );
  color: #ffab40;
  border: 1px solid rgba(255, 171, 64, 0.2);
}

.badge.error {
  background: linear-gradient(135deg, 
    rgba(255, 71, 87, 0.1),
    rgba(255, 126, 126, 0.1)
  );
  color: #ff4757;
  border: 1px solid rgba(255, 71, 87, 0.2);
}

.badge.info {
  background: linear-gradient(135deg, 
    rgba(0, 162, 255, 0.1),
    rgba(99, 102, 241, 0.1)
  );
  color: #00a2ff;
  border: 1px solid rgba(0, 162, 255, 0.2);
}

/* Outlined variants */
.badge.is-outlined {
  background: transparent;
}

.badge.is-outlined.primary {
  color: #6366f1;
  border-color: rgba(99, 102, 241, 0.4);
}

.badge.is-outlined.secondary {
  color: #ec4899;
  border-color: rgba(236, 72, 153, 0.4);
}

.badge.is-outlined.success {
  color: #00ffcc;
  border-color: rgba(0, 255, 204, 0.4);
}

.badge.is-outlined.warning {
  color: #ffab40;
  border-color: rgba(255, 171, 64, 0.4);
}

.badge.is-outlined.error {
  color: #ff4757;
  border-color: rgba(255, 71, 87, 0.4);
}

.badge.is-outlined.info {
  color: #00a2ff;
  border-color: rgba(0, 162, 255, 0.4);
}

/* Hover effects */
.badge:not(.is-dot):hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Gradient border effect */
.badge:not(.is-outlined)::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: inherit;
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
  opacity: 0;
  transition: opacity 0.2s ease;
}

.badge:not(.is-outlined):hover::before {
  opacity: 1;
}
</style> 