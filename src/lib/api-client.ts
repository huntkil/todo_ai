export interface WorkInputResponse {
  category: 'calendar' | 'worklog' | 'meeting' | 'gantt';
  calendar_events: unknown[];
  obsidian_notes: unknown[];
  gantt_tasks: unknown[];
  confidence: number;
  original_text: string;
  keywords: string[];
  entities: {
    persons?: string[];
    organizations?: string[];
    locations?: string[];
    misc?: string[];
  };
  dates: string[];
  times: string[];
  sentiment: string;
  contact_info?: {
    id: number;
    name: string;
    email?: string;
    phone?: string;
    company?: string;
    position?: string;
    department?: string;
    notes?: string;
    created_at: string;
    updated_at: string;
    user_id: string;
  };
} 