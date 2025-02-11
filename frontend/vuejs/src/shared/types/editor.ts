export interface Editor {
  id: string
  content: string
  language: string
  theme?: string
  readOnly?: boolean
}

export type EditorLanguage = 
  | 'html'
  | 'css'
  | 'javascript'
  | 'typescript'
  | 'python'
  | 'markdown'
  | 'text'

export type EditorTheme = 'dark' | 'light'

export interface EditorOptions {
  language?: EditorLanguage
  theme?: EditorTheme
  readOnly?: boolean
  lineNumbers?: boolean
  minimap?: boolean
}

export interface EditorConfig {
  language: EditorLanguage
  theme: string
  tabSize: number
  insertSpaces: boolean
  wordWrap: 'off' | 'on' | 'wordWrapColumn' | 'bounded'
}
