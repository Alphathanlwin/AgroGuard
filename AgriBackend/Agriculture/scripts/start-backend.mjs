import { existsSync } from 'node:fs'
import { spawn } from 'node:child_process'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const backendDirectory = join(projectRoot, 'fastapi')
const virtualEnvironmentPython = process.platform === 'win32'
  ? join(backendDirectory, '.venv', 'Scripts', 'python.exe')
  : join(backendDirectory, '.venv', 'bin', 'python')

const python = process.env.AGROGUARD_PYTHON || (
  existsSync(virtualEnvironmentPython) ? virtualEnvironmentPython : 'python'
)

const backend = spawn(
  python,
  ['-m', 'uvicorn', 'app.main:app', '--reload'],
  {
    cwd: backendDirectory,
    env: process.env,
    stdio: 'inherit',
  },
)

backend.on('error', (error) => {
  console.error(`Unable to start the backend with "${python}": ${error.message}`)
  console.error('Create fastapi/.venv and install fastapi/requirements.txt, then try again.')
  process.exitCode = 1
})

backend.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal)
    return
  }
  process.exitCode = code ?? 1
})

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => backend.kill(signal))
}
