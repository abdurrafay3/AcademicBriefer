export type StepStatus = "success" | "failed" | "skipped";

export interface Deadline {
  title: string;
  due_date: string;
  description: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
}

export interface Opportunity {
  title: string;
  deadline: string | null;
  description: string;
}

export interface Event {
  title: string;
  date: string;
  location: string | null;
}

export interface Assignment {
  title: string;
  due_date: string | null;
  description: string;
  max_points: number | null;
  available: string | null;
  course_id: string | null;
}

export interface EmailDigest {
  summary: string;
  deadlines: Deadline[];
  opportunities: Opportunity[];
  events: Event[];
  important_announcements: string[];
}

export interface BriefingResponse {
  generated_at: string;
  email_status: "success" | "failed";
  canvas_status: "success" | "failed";
  calendar_status: StepStatus;
  emails_scraped: number;
  assignments: Assignment[];
  summary: EmailDigest | null;
}
