/**
 * Languages the build workspace's code editor understands.
 *
 * This sat in shared/types/ with two consumers, both in this app — no other
 * app has an editor. A code editor's language list is the build app's
 * vocabulary, so it lives with it.
 */
export type EditorLanguage =
  | 'html'
  | 'css'
  | 'javascript'
  | 'typescript'
  | 'python'
  | 'markdown'
  | 'text'
