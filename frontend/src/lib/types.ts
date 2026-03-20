export interface UserPreferences {
  roles: string[]
  locations: string[]
  target_companies: string[]
  platforms: string[]
  match_threshold: number
  experience_level: string
}

export interface User {
  _id: string
  email: string
  name: string
  phone: string
  summary: string
  preferences: UserPreferences
  autopilot_enabled: boolean
  is_paused: boolean
  autopilot_started_at: string | null
  last_scraped_at: string | null
  stats: {
    total_applied: number
    applied_today: number
    applied_this_week: number
  }
}

export interface Job {
  _id: string
  source: string
  company: string
  title: string
  location: string
  description: string
  apply_url: string
  scraped_at: string
}

export interface Application {
  application_id: string
  status: string
  match_score: number
  job_title: string
  company: string
  location: string
  apply_url: string
  applied_at: string | null
  reasons: string
  error: string
}

export interface Dashboard {
  autopilot_enabled: boolean
  is_paused: boolean
  last_scraped_at: string | null
  stats: {
    total_applied: number
    applied_today: number
    applied_this_week: number
    avg_match_score: number
  }
  status_counts: Record<string, number>
  feed: Application[]
}
