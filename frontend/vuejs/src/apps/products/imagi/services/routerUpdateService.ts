import { FileService } from './fileService'

function toKebabCase(input: string): string {
  return input
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/\s+/g, '-')
    .replace(/_+/g, '-')
    .toLowerCase()
}

function deriveRouteInfo(appName: string, viewFileName: string) {
  const componentName = viewFileName.replace(/\.vue$/i, '')
  const base = componentName.endsWith('View') ? componentName.slice(0, -4) : componentName
  const slug = toKebabCase(base)
  // path like /<app>/<slug>
  const path = `/${appName}/${slug}`
  const name = `${appName}-${slug}-view`
  const importName = componentName
  return { path, name, importName, componentName }
}

function buildNewRouterContent(appName: string, viewFileName: string) {
  const { path, name, importName } = deriveRouteInfo(appName, viewFileName)
  return `import type { RouteRecordRaw } from 'vue-router'\nimport ${importName} from '../views/${viewFileName}'\n\nconst routes: RouteRecordRaw[] = [\n  {\n    path: '${path}',\n    name: '${name}',\n    component: ${importName},\n    meta: { requiresAuth: false, title: '${importName.replace(/View$/, '')}'\n    }\n  }\n]\n\nexport { routes }\n`
}

function injectImport(content: string, importLine: string): string {
  if (content.includes(importLine)) return content
  // place after existing imports
  const lines = content.split('\n')
  let lastImportIdx = -1
  for (let i = 0; i < lines.length; i++) {
    if (/^\s*import\s+/.test(lines[i])) lastImportIdx = i
  }
  if (lastImportIdx >= 0) {
    lines.splice(lastImportIdx + 1, 0, importLine)
    return lines.join('\n')
  }
  return importLine + '\n' + content
}

function injectRouteRecord(content: string, routeRecord: string, routeName: string): string {
  if (content.includes(`name: '${routeName}'`) || content.includes(`name: \"${routeName}\"`)) {
    return content
  }
  const startIdx = content.indexOf('const routes')
  const bracketIdx = content.indexOf('[', startIdx)
  const closingIdx = content.lastIndexOf(']')
  if (startIdx === -1 || bracketIdx === -1 || closingIdx === -1) {
    // fallback: append routes array
    const appended = `\n\nconst routes: RouteRecordRaw[] = [\n${routeRecord}\n]\n\nexport { routes }\n`
    return content.trimEnd() + appended
  }
  const before = content.slice(0, closingIdx)
  const between = content.slice(bracketIdx + 1, closingIdx).trim()
  const needsComma = between.length > 0 && !/[,]\s*$/.test(before)
  const insertion = (between ? (between.endsWith(',') ? '' : ',') : '') + '\n' + routeRecord + '\n'
  const after = content.slice(closingIdx)
  return before + insertion + after
}

export const RouterUpdateService = {
  async addViewRoute(projectId: string, viewFilePath: string): Promise<void> {
    // Expecting path to contain /src/apps/<app>/views/<ViewName>.vue
    // Support both root-level and frontend-prefixed paths:
    // - src/apps/<app>/views/<ViewName>.vue
    // - frontend/vuejs/src/apps/<app>/views/<ViewName>.vue
    const match = viewFilePath.match(/(?:^|\/)(?:frontend\/vuejs\/)?src\/apps\/([^\/]+)\/views\/([^\/]+\.vue)$/i)
    if (!match) return
    const appName = match[1]
    const viewFileName = match[2]

    // Always target the frontend Vue app router path
    const routerPath = `frontend/vuejs/src/apps/${appName}/router/index.ts`
    const { path, name, importName } = deriveRouteInfo(appName, viewFileName)

    const importLine = `import ${importName} from '../views/${viewFileName}'`
    const routeRecord = `  {\n    path: '${path}',\n    name: '${name}',\n    component: ${importName},\n    meta: { requiresAuth: false, title: '${importName.replace(/View$/, '')}' }\n  }`

    try {
      // Try to get existing router content
      let exists = true
      let content = ''
      try {
        content = await FileService.getFileContent(projectId, routerPath)
      } catch (e) {
        exists = false
      }

      if (!exists || !content.trim()) {
        const newContent = buildNewRouterContent(appName, viewFileName)
        await FileService.createFile(projectId, routerPath, newContent)
        return
      }

      // Update existing content
      let updated = content
      updated = injectImport(updated, importLine)
      updated = injectRouteRecord(updated, routeRecord, name)

      if (updated !== content) {
        await FileService.updateFileContent(projectId, routerPath, updated)
      }
    } catch (err) {
      console.warn('RouterUpdateService: failed to add view route', { viewFilePath, err })
    }
  }
}

export default RouterUpdateService
