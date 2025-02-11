import type { RouteRecordRaw } from 'vue-router'

export interface AppRouteModule {
  default: RouteRecordRaw[]
}

export type RouteModule = {
  routes: RouteRecordRaw[]
} | {
  default: RouteRecordRaw[]
}

export interface AppRoutes {
  home: RouteRecordRaw[]
  auth: RouteRecordRaw[]
  builder: RouteRecordRaw[]
  payments: RouteRecordRaw[]
}
