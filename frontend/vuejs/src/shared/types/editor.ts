export interface Editor {
  getValue(): string
  setValue(value: string): void
  dispose(): void
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
  language?: string
  theme?: 'light' | 'dark'
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
