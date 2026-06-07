export interface Asset {
  asset_id: string;
  asset_name: string;
  asset_type: string;
  category: string;
  brand: string;
  model_number: string;
  assigned_to: string;
  purchase_date: string;
  warranty_expiry: string;
  location: string;
  notes: string;
  status: string;
  last_updated_at: string;
}

export interface AuditLog {
  log_id: string;
  asset_id: string;
  action: string;
  performed_by: string;
  details: string;
  timestamp: string;
}

export interface DashboardStats {
  total_assets: number;
  assigned_assets: number;
  available_assets: number;
  returned_assets: number;
  under_audit: number;
  pending_clearance: number;
  cleared_assets: number;
  categories: Record<string, number>;
  recent_assets: Asset[];
  status_distribution: Record<string, number>;
}

export interface ChatMessage {
  id: string;
  content: {
    role: string;
    parts: ChatPart[];
  };
  timestamp: Date;
}

export interface ChatPart {
  text?: string;
  functionCall?: { name: string; args?: Record<string, unknown> };
  functionResponse?: { name: string; response?: unknown };
  inlineData?: { data: string; mimeType: string; displayName: string };
}

export interface Session {
  id: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}
