'use strict'

const { app, BrowserWindow, dialog, ipcMain, session, shell } = require('electron')
const { spawn } = require('node:child_process')
const fs = require('node:fs')
const http = require('node:http')
const path = require('node:path')
const { URL } = require('node:url')

const ROOT = path.join(__dirname, '..')
const BACKEND_DIR = path.join(ROOT, 'backend')
// Version installée : le dossier du programme est en lecture seule de fait, les données vont dans %APPDATA%\Cybbig.
const INSTALLED = app.isPackaged
const DATA_DIR = INSTALLED ? path.join(app.getPath('userData'), 'data') : path.join(BACKEND_DIR, 'data')
const HOST = '127.0.0.1'
const PORT = Number(process.env.CYBBIG_PORT || 8765)
const APP_URL = `http://${HOST}:${PORT}`
const DEV = process.argv.includes('--dev')
const DEV_URL = process.env.CYBBIG_DEV_URL || 'http://127.0.0.1:5173'
const START_URL = DEV ? DEV_URL : APP_URL

let mainWindow = null
let backendProcess = null
let backendOwned = false
let backendReady = false
let quitting = false

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function backendHealth(timeout = 1200) {
  return new Promise((resolve) => {
    const request = http.get({ hostname: HOST, port: PORT, path: '/api/health', timeout }, (response) => {
      let body = ''
      response.on('data', (chunk) => { body += chunk })
      response.on('end', () => {
        try {
          const payload = JSON.parse(body)
          resolve(response.statusCode === 200 && payload.status === 'ok')
        } catch {
          resolve(false)
        }
      })
    })
    request.on('timeout', () => request.destroy())
    request.on('error', () => resolve(false))
  })
}

function pythonExecutable() {
  const candidates = [
    process.env.CYBBIG_PYTHON,
    // Python embarqué livré par les installateurs (aucune installation de Python requise).
    path.join(BACKEND_DIR, 'python', 'python.exe'),
    path.join(BACKEND_DIR, '.venv', 'Scripts', 'python.exe'),
    path.join(BACKEND_DIR, '.venv', 'bin', 'python'),
    'python',
  ].filter(Boolean)
  for (const candidate of candidates) {
    if (candidate === 'python' || fs.existsSync(candidate)) return candidate
  }
  return 'python'
}

function backendLog() {
  fs.mkdirSync(DATA_DIR, { recursive: true })
  const file = path.join(DATA_DIR, 'backend.log')
  try {
    if (fs.existsSync(file) && fs.statSync(file).size > 5 * 1024 * 1024) {
      fs.renameSync(file, path.join(DATA_DIR, 'backend.old.log'))
    }
  } catch { /* rotation best-effort */ }
  return fs.createWriteStream(file, { flags: 'a' })
}

async function ensureBackend() {
  if (await backendHealth()) {
    console.log('[cybbig] backend déjà actif, réutilisation')
    return
  }

  const log = backendLog()
  const python = pythonExecutable()
  console.log(`[cybbig] démarrage du backend : ${python}`)
  backendProcess = spawn(
    python,
    ['-m', 'uvicorn', 'app.main:app', '--host', HOST, '--port', String(PORT), '--log-level', 'info'],
    {
      cwd: BACKEND_DIR,
      windowsHide: true,
      env: {
        ...process.env,
        CYBBIG_PORT: String(PORT),
        CYBBIG_DATA_DIR: DATA_DIR,
        CYBBIG_DB_PATH: path.join(DATA_DIR, 'cybbig.db'),
        PYTHONUNBUFFERED: '1',
        PYTHONDONTWRITEBYTECODE: INSTALLED ? '1' : '',
        PYTHONIOENCODING: 'utf-8',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  )
  backendOwned = true
  backendProcess.stdout.on('data', (chunk) => { log.write(chunk); process.stdout.write(chunk) })
  backendProcess.stderr.on('data', (chunk) => { log.write(chunk); process.stderr.write(chunk) })
  backendProcess.on('error', (error) => {
    log.write(`[cybbig] erreur de démarrage : ${error.message}\n`)
  })
  backendProcess.on('exit', (code) => {
    log.write(`[cybbig] backend arrêté (code ${code})\n`)
    if (!quitting && code === RESTART_EXIT_CODE) {
      // Redémarrage demandé depuis l'éditeur de code de l'administration.
      backendProcess = null
      backendOwned = false
      backendReady = false
      restartBackend().catch(() => undefined)
      return
    }
    if (!quitting && backendReady) {
      dialog.showErrorBox(
        'Cybbig — service local arrêté',
        `Le backend s’est arrêté de manière inattendue (code ${code}).\nConsultez ${path.join(DATA_DIR, 'backend.log')} puis relancez l’application.`,
      )
      app.quit()
    }
  })

  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (await backendHealth()) {
      backendReady = true
      console.log('[cybbig] backend prêt')
      return
    }
    if (backendProcess && backendProcess.exitCode !== null) break
    await sleep(500)
  }
  throw new Error(`Le service local n’a pas répondu sur ${APP_URL} dans le délai imparti.`)
}

const RESTART_EXIT_CODE = 75

// Remet en place la dernière série de fichiers sauvegardés par l'éditeur de code.
function restoreLatestCodeBackup() {
  const root = path.join(DATA_DIR, 'code-backups')
  if (!fs.existsSync(root)) return 0
  const latest = fs.readdirSync(root).filter((name) => fs.statSync(path.join(root, name)).isDirectory()).sort().pop()
  if (!latest) return 0
  let restored = 0
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) { walk(full); continue }
      const target = path.join(ROOT, path.relative(path.join(root, latest), full))
      if (!path.resolve(target).startsWith(path.resolve(ROOT))) continue
      fs.mkdirSync(path.dirname(target), { recursive: true })
      fs.copyFileSync(full, target)
      restored += 1
    }
  }
  walk(path.join(root, latest))
  return restored
}

async function restartBackend() {
  try {
    await ensureBackend()
    if (mainWindow) await mainWindow.loadURL(START_URL)
  } catch (error) {
    const choice = await dialog.showMessageBox({
      type: 'error',
      title: 'Cybbig — le service ne redémarre pas',
      message: 'Le service local ne démarre plus après la dernière modification du code.',
      detail: `${error instanceof Error ? error.message : error}\n\nJournal : ${path.join(DATA_DIR, 'backend.log')}`,
      buttons: ['Restaurer la dernière sauvegarde et réessayer', 'Quitter'],
      defaultId: 0,
      cancelId: 1,
    })
    if (choice.response === 0 && restoreLatestCodeBackup() > 0) {
      await restartBackend()
      return
    }
    quitting = true
    app.quit()
  }
}

function stopBackend() {
  if (!backendOwned || !backendProcess) return
  const pid = backendProcess.pid
  backendProcess = null
  backendOwned = false
  try {
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', String(pid), '/T', '/F'], { windowsHide: true })
    } else {
      process.kill(pid, 'SIGTERM')
    }
  } catch { /* already stopped */ }
}

function isLocalUrl(raw) {
  try {
    const origin = new URL(raw).origin
    return origin === new URL(APP_URL).origin || origin === new URL(START_URL).origin
  } catch {
    return false
  }
}

function installSecurity(window) {
  const appOrigin = new URL(START_URL).origin

  window.webContents.setWindowOpenHandler(({ url }) => {
    try {
      const target = new URL(url)
      if (target.origin === appOrigin && target.pathname.startsWith('/api/reports/') && target.pathname.endsWith('/download')) {
        window.webContents.downloadURL(target.toString())
        return { action: 'deny' }
      }
      if (target.protocol === 'https:' || target.protocol === 'http:') {
        shell.openExternal(target.toString()).catch(() => undefined)
      }
    } catch { /* ignore invalid URLs */ }
    return { action: 'deny' }
  })

  window.webContents.on('will-navigate', (event, url) => {
    try {
      if (new URL(url).origin !== appOrigin) {
        event.preventDefault()
        const target = new URL(url)
        if (target.protocol === 'https:' || target.protocol === 'http:') {
          shell.openExternal(url).catch(() => undefined)
        }
      }
    } catch {
      event.preventDefault()
    }
  })

  window.webContents.on('will-attach-webview', (event) => event.preventDefault())
}

function installSessionGuards() {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback, details) => {
    const origin = details?.requestingUrl || webContents?.getURL() || ''
    callback(isLocalUrl(origin) && permission === 'clipboard-sanitized-write')
  })

  session.defaultSession.on('will-download', (event, item) => {
    const targetDir = app.getPath('downloads')
    const safeName = path.basename(item.getFilename() || 'cybbig-rapport.html')
    const extension = path.extname(safeName)
    const stem = path.basename(safeName, extension)
    let target = path.join(targetDir, safeName)
    let counter = 1
    while (fs.existsSync(target)) {
      target = path.join(targetDir, `${stem}-${counter}${extension}`)
      counter += 1
    }
    item.setSavePath(target)
    item.once('done', async (_event, state) => {
      if (state !== 'completed') return
      const result = await dialog.showMessageBox({
        type: 'info',
        title: 'Rapport exporté',
        message: 'Le rapport a été enregistré.',
        detail: target,
        buttons: ['Ouvrir', 'Fermer'],
        defaultId: 0,
        cancelId: 1,
      })
      if (result.response === 0) {
        shell.openPath(target).catch(() => undefined)
      }
    })
  })
}

function uniquePath(dir, name) {
  const extension = path.extname(name)
  const stem = path.basename(name, extension)
  let target = path.join(dir, name)
  for (let counter = 1; fs.existsSync(target); counter += 1) target = path.join(dir, `${stem}-${counter}${extension}`)
  return target
}

// Exporte un rapport HTML local en PDF (fenêtre cachée + printToPDF), dans le dossier Téléchargements.
function installPdfExport() {
  ipcMain.handle('cybbig:save-report-pdf', async (_event, reportId, filename) => {
    if (!/^[A-Za-z0-9_-]{1,80}$/.test(reportId)) throw new Error('Identifiant de rapport invalide.')
    const worker = new BrowserWindow({ show: false, webPreferences: { sandbox: true, contextIsolation: true, javascript: false } })
    try {
      await worker.loadURL(`${APP_URL}/api/reports/${reportId}/download`)
      const pdf = await worker.webContents.printToPDF({ printBackground: true, pageSize: 'A4', margins: { marginType: 'default' } })
      const safeName = path.basename(String(filename || `cybbig-${reportId}`)).replace(/[^\w.\- ]+/g, '_').replace(/\.pdf$/i, '') + '.pdf'
      const target = uniquePath(app.getPath('downloads'), safeName)
      fs.writeFileSync(target, pdf)
      shell.openPath(target).catch(() => undefined)
      return target
    } finally {
      worker.destroy()
    }
  })
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1460,
    height: 920,
    minWidth: 1040,
    minHeight: 680,
    show: false,
    title: 'Cybbig — Défense locale',
    icon: path.join(__dirname, process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
    backgroundColor: '#060e19',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webviewTag: false,
      spellcheck: false,
      preload: path.join(__dirname, 'preload.js'),
      devTools: DEV || process.env.CYBBIG_DEVTOOLS === '1',
    },
  })

  installSecurity(mainWindow)

  mainWindow.once('ready-to-show', () => mainWindow.show())
  mainWindow.on('closed', () => { mainWindow = null })
}

async function boot() {
  const window = mainWindow
  if (!window) return
  try {
    await window.loadFile(path.join(__dirname, 'splash.html'))
    await ensureBackend()
    await window.loadURL(START_URL)
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    console.error('[cybbig] démarrage impossible :', message)
    await dialog.showMessageBox({
      type: 'error',
      title: 'Cybbig — démarrage impossible',
      message: 'Le service local n’a pas pu démarrer.',
      detail: `${message}\n\n${INSTALLED ? 'Réinstallez Cybbig avec scripts\\install.ps1.' : 'Vérifiez que Python et les dépendances sont installés : scripts\\setup.ps1.'}\nJournaux : ${path.join(DATA_DIR, 'backend.log')}`,
      buttons: ['Fermer'],
    })
    quitting = true
    stopBackend()
    app.quit()
  }
}

// Regroupe la fenêtre sous l'icône Cybbig dans la barre des tâches (même ID que les raccourcis).
if (process.platform === 'win32') app.setAppUserModelId('Cybbig.Desktop')

const gotLock = app.requestSingleInstanceLock()
if (!gotLock) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (!mainWindow) return
    if (mainWindow.isMinimized()) mainWindow.restore()
    mainWindow.focus()
  })

  app.whenReady().then(async () => {
    installSessionGuards()
    installPdfExport()
    await createWindow()
    await boot()

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow().then(boot).catch(() => undefined)
      }
    })
  })

  app.on('before-quit', () => {
    quitting = true
    stopBackend()
  })

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
  })
}
