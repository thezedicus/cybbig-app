export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info' | 'unknown'
export type ScanKind = 'php' | 'web' | 'api' | 'checkout'
export type ScanStatus = 'queued' | 'running' | 'completed' | 'failed' | 'blocked' | 'cancelled'
export type FindingStatus = 'open' | 'acknowledged' | 'fixed' | 'accepted_risk' | 'false_positive'

export interface SeverityCounts {
  critical: number
  high: number
  medium: number
  low: number
  info: number
}

export interface ConsentRecord {
  id?: number
  version?: string
  accepted_at?: string
  user_name?: string
  organization?: string
  purpose?: string
  text_hash?: string
}

export interface ConsentStatus {
  accepted: boolean
  version: string
  record: ConsentRecord | null
  current_version: string
  text?: string
  text_hash?: string
}

export interface Project {
  id: string
  name: string
  client: string
  description: string
  path: string
  base_url: string
  environment: string
  authorization_ref: string
  authorized_by: string
  authorized_at: string | null
  authorization_confirmed: number | boolean
  scope_domains: string[] | string
  scope_paths: string[]
  activity_level: string
  activity_label?: string
  created_at: string
  updated_at: string
  severity: SeverityCounts
  findings_count: number
  open_findings: number
  risk_score: number
  scans_count: number
  last_scan: Pick<Scan, 'id' | 'kind' | 'status' | 'created_at' | 'finished_at'> | null
  path_exists: boolean
  recent_scans?: Scan[]
  top_findings?: Finding[]
}

export interface Scan {
  id: string
  project_id: string
  kind: ScanKind
  mode: string
  target: string
  status: ScanStatus
  progress: number
  message: string
  error?: string
  config: Record<string, unknown>
  summary: ScanSummary
  created_at: string
  started_at?: string | null
  finished_at?: string | null
  project?: Pick<Project, 'id' | 'name' | 'client' | 'base_url' | 'path' | 'activity_level'> | null
  project_name?: string
  findings?: Finding[]
  severity?: SeverityCounts
  dependencies?: Dependency[]
}

export interface ScanSummary {
  findings?: number
  severity?: SeverityCounts
  risk_score?: number
  dependencies?: number
  vulnerable_dependencies?: number
  extra?: Record<string, unknown>
}

export interface Finding {
  id: string
  project_id: string
  ai_verdict?: string
  ai_notes?: string
  scan_id: string
  engine: string
  rule_id: string
  category: string
  title: string
  severity: Severity
  confidence: string
  description: string
  evidence: string
  file_path: string
  line_start: number | null
  line_end: number | null
  url: string
  cwe: string
  owasp: string
  remediation: string
  references: string[]
  status: FindingStatus
  risk_score: number
  created_at: string
  updated_at: string
  project_name?: string
  scan?: Pick<Scan, 'id' | 'kind' | 'status' | 'target' | 'created_at'> | null
}

export interface Dependency {
  id: string
  package: string
  version: string
  vulnerable: number | boolean
  vuln_id: string
  severity: string
  summary: string
  fixed_version: string
  source: string
}

export interface IntelItem {
  id: number
  source: string
  external_id: string
  title: string
  summary: string
  severity: Severity
  cvss: number | null
  epss?: number | null
  published_at: string
  modified_at: string
  product: string
  cve: string
  exploited: number | boolean
  url: string
  tags: string[]
  fetched_at: string
  raw?: Record<string, unknown>
}

export interface IntelSource {
  name: string
  label: string
  url: string
  kind: string
  enabled: number | boolean
  last_sync_at: string | null
  status: string
  items_count: number
  error: string
}

export interface IntelStats {
  total: number
  exploited: number
  last_fetch: string | null
  by_source: Array<{ source: string; count: number; exploited: number }>
  by_severity: Array<{ severity: string; count: number }>
  recent: IntelItem[]
  sources: IntelSource[]
}

export interface KnowledgeDoc {
  id: string
  title: string
  category: string
  content: string
  source: string
  tags: string
  created_at: string
  updated_at: string
  excerpt?: string
}

export interface Report {
  id: string
  project_id: string
  scan_id: string | null
  kind: string
  title: string
  path: string
  meta: { findings?: number; severity?: SeverityCounts; risk_score?: number; ai_summary?: boolean }
  ai_summary?: boolean
  created_at: string
  download_url: string
  json_url: string
}

export interface AutomationRun {
  id: string
  automation_id: string
  started_at: string
  finished_at: string | null
  status: string
  log: string
}

export interface Automation {
  id: string
  project_id: string | null
  project_name?: string | null
  name: string
  kind: string
  interval_minutes: number
  config: Record<string, unknown>
  enabled: boolean | number
  last_run_at: string | null
  next_run_at: string
  last_status: string
  created_at: string
  updated_at: string
  runs: AutomationRun[]
}

export interface SchedulerStatus {
  running: boolean
  executing: number
  queued: number
  total: number
  enabled: number
  next_runs: Array<{ id: string; name: string; next_run_at: string }>
}

export interface DashboardData {
  counts: {
    projects: number
    scans: number
    findings: number
    findings_total: number
    alerts_unread: number
    critical: number
    high: number
  }
  risk_score: number
  severity: SeverityCounts
  trend: Array<{ date: string; total: number; critical: number; high: number }>
  by_engine: Array<{ engine: string; count: number }>
  projects: Array<Pick<Project, 'id' | 'name' | 'client' | 'base_url' | 'path' | 'activity_level' | 'updated_at'> & { risk_score: number; findings: number }>
  recent_scans: Scan[]
  alerts: Alert[]
  intel: { items: number; exploited: number; last_fetch: string | null }
  scheduler: SchedulerStatus
  ai: OllamaStatus
  top_findings: Array<Pick<Finding, 'id' | 'title' | 'severity' | 'engine' | 'file_path' | 'url' | 'project_id'> & { project_name?: string }>
  generated_at: string
}

export interface Alert {
  id: string
  project_id: string | null
  source: string
  severity: Severity
  title: string
  message: string
  link: string
  read: number | boolean
  created_at: string
}

export interface OllamaEndpoint {
  available: boolean
  url: string
  models: string[]
  selected_model: string
  error: string
}

export interface OllamaStatus extends OllamaEndpoint {
  provider?: 'local' | 'cloud' | 'none'
  /** « daemon » : modèle en ligne servi par l'Ollama local (compte ollama.com) ; « direct » : HTTPS + clé API. */
  route?: 'local' | 'direct' | 'daemon'
  preferred?: 'auto' | 'local' | 'cloud' | 'training'
  local?: OllamaEndpoint & { daemon_cloud_models?: string[] }
  cloud?: OllamaEndpoint & { enabled: boolean; configured: boolean; route?: 'direct' | 'daemon' }
}

export interface LabScenario {
  id: string
  slug: string
  title: string
  category: string
  level: string
  description: string
  objective: string
  vulnerable_code: string
  secure_code: string
  test_steps: string
  detection: string
  references: string[]
  created_at: string
}

export interface AssistantMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  model: string
  created_at: string
}

export interface ChatResponse {
  answer: string
  model: string
  offline: boolean
  sources: Array<{ id: string; title: string; category: string }>
  context: { findings_used: number; documents_used: number }
  ollama: OllamaStatus
}

export interface EngineInfo {
  id: string
  name: string
  mode: string
  status: string
  capabilities: string[]
}

export interface AuditEntry {
  id: number
  actor: string
  action: string
  details: string
  created_at: string
}
