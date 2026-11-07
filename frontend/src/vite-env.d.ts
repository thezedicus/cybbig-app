/// <reference types="vite/client" />

// Pont exposé par desktop/preload.js (absent dans un navigateur classique).
interface Window {
  cybbigDesktop?: { saveReportPdf: (reportId: string, filename?: string) => Promise<string> }
}
