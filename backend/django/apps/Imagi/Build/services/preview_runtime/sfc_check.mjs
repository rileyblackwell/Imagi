// Compile Vue single-file components the way Vite would, and report what
// fails, before the files reach the app the preview serves.
//
// Usage: node sfc_check.mjs <node_modules dir>
// stdin:  {"files": [{"path": "...", "source": "..."}]}
// stdout: {"ok": true, "problems": [{"file": "...", "error": "..."}]}
//         {"ok": false, "error": "..."} when the compiler can't be loaded.
import { createRequire } from 'node:module'
import path from 'node:path'

function line(loc) {
  return loc && loc.start ? ` (line ${loc.start.line})` : ''
}

function message(e) {
  return `${(e && e.message) || String(e)}`.split('\n')[0] + line(e && e.loc)
}

async function main() {
  const modules = process.argv[2]
  let sfc
  try {
    const require = createRequire(path.join(path.dirname(path.resolve(modules)), 'noop.js'))
    sfc = require('@vue/compiler-sfc')
  } catch (e) {
    process.stdout.write(JSON.stringify({ ok: false, error: `compiler unavailable: ${message(e)}` }))
    return
  }
  let input = ''
  for await (const chunk of process.stdin) input += chunk
  const { files = [] } = JSON.parse(input || '{}')
  const problems = []
  for (const { path: file, source } of files) {
    const id = 'imagi-check'
    try {
      const { descriptor, errors } = sfc.parse(source, { filename: file })
      if (errors.length) {
        for (const e of errors.slice(0, 5)) problems.push({ file, error: message(e) })
        continue
      }
      let bindings
      if (descriptor.script || descriptor.scriptSetup) {
        try {
          bindings = sfc.compileScript(descriptor, { id }).bindings
        } catch (e) {
          problems.push({ file, error: message(e) })
          continue
        }
      }
      if (descriptor.template && !descriptor.template.src) {
        const result = sfc.compileTemplate({
          source: descriptor.template.content,
          filename: file,
          id,
          compilerOptions: { bindingMetadata: bindings },
        })
        for (const e of (result.errors || []).slice(0, 5)) {
          problems.push({ file, error: typeof e === 'string' ? e.split('\n')[0] : message(e) })
        }
      }
    } catch (e) {
      problems.push({ file, error: message(e) })
    }
  }
  process.stdout.write(JSON.stringify({ ok: true, problems }))
}

main().catch((e) => {
  process.stdout.write(JSON.stringify({ ok: false, error: message(e) }))
})
