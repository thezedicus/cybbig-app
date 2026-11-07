'use strict'

// Pont minimal entre l'interface et Electron : seule l'exportation PDF d'un rapport est exposée.
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('cybbigDesktop', {
  saveReportPdf: (reportId, filename) => ipcRenderer.invoke('cybbig:save-report-pdf', String(reportId), String(filename || '')),
})
