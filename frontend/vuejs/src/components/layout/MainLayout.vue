<template>
  <div class="main-layout">
    <nav class="home-nav-buttons" v-if="isAuthenticated">
      <ul class="home-nav-list">
        <li class="home-nav-item dropdown">
          <a class="home-nav-btn btn-products dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i class="fas fa-th"></i> Products
          </a>
          <div class="home-dropdown-menu dropdown-menu" aria-labelledby="navbarDropdown">
            <router-link class="home-dropdown-btn dropdown-item" to="/dashboard">
              <i class="fas fa-magic"></i> Imagi Oasis
            </router-link>
          </div>
        </li>
        <li class="home-nav-item">
          <router-link to="/payments/checkout" class="btn btn-success">
            <i class="fas fa-coins"></i>
            <span>Buy Credits</span>
          </router-link>
        </li>
        <li class="home-nav-item">
          <a @click.prevent="logout" href="#" class="btn btn-secondary">
            <i class="fas fa-sign-out-alt"></i>
            <span>Logout</span>
          </a>
        </li>
      </ul>
    </nav>
    <nav class="home-nav-buttons" v-else>
      <ul class="home-nav-list">
        <li class="home-nav-item">
          <router-link to="/auth/login" class="btn btn-secondary">
            <i class="fas fa-sign-in-alt"></i>
            <span>Login</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <router-view></router-view>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'MainLayout',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const isAuthenticated = computed(() => store.state.auth.isAuthenticated)
    
    const logout = async () => {
      await store.dispatch('auth/logout')
      router.push('/')
    }
    
    return {
      isAuthenticated,
      logout
    }
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Navigation Buttons */
.home-nav-buttons {
  margin-left: auto;
  padding-right: 15px;
  display: flex;
  align-items: center;
}

.home-nav-list {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 16px;
  align-items: center;
}

.home-nav-item {
  position: relative;
}

/* Primary Navigation Button */
.home-nav-btn {
  background: rgba(255, 255, 255, 0.03);
  color: var(--global-text-color);
  padding: 10px 18px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 0.95rem;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.home-nav-btn i {
  font-size: 1.1rem;
  color: #00ffcc;
}

/* Special Button Variants */
.home-nav-btn.btn-products {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.1),
    rgba(0, 255, 204, 0.1)
  );
  border-color: rgba(99, 102, 241, 0.2);
}

/* Dropdown Menu */
.home-dropdown-menu {
  background: rgba(13, 12, 34, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-top: 8px;
  padding: 8px;
  min-width: 200px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.home-dropdown-btn {
  color: var(--global-text-color);
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  width: 100%;
  text-align: left;
  transition: background-color 0.2s ease;
}

.home-dropdown-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--global-text-color);
}

.home-dropdown-btn i {
  color: #00ffcc;
  font-size: 1.1rem;
}

/* Responsive Navigation */
@media (max-width: 768px) {
  .home-nav-buttons {
    width: 100%;
    padding: 15px;
  }

  .home-nav-list {
    flex-direction: column;
    width: 100%;
    gap: 12px;
  }

  .home-nav-item {
    width: 100%;
  }

  .home-nav-btn {
    width: 100%;
    justify-content: center;
    padding: 12px 20px;
  }

  .home-dropdown-menu {
    width: 100%;
    margin-top: 5px;
  }

  .home-dropdown-btn {
    justify-content: center;
  }
}

/* Update hover styles for nav buttons */
.home-nav-btn:hover {
  text-decoration: none;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Products button hover */
.home-nav-btn.btn-products:hover {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.2),
    rgba(0, 255, 204, 0.15)
  );
  border-color: rgba(99, 102, 241, 0.3);
}

/* Dropdown button hover */
.home-dropdown-btn:hover {
  background: linear-gradient(135deg,
    rgba(99, 102, 241, 0.15),
    rgba(0, 255, 204, 0.1)
  );
  color: var(--global-text-color);
  transform: translateX(4px);
  transition: all 0.2s ease;
}

/* Ensure no underline on dropdown toggle */
.home-nav-btn.dropdown-toggle:hover {
  text-decoration: none;
}
</style>
