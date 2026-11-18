export type ApiConfig = { baseUrl: string };

export type Overview = {
  metrics: Record<string, { value: number | null; status: string }>;
  integrations: Record<string, { status: string }>;
  scope: string;
};

export type AuditEvent = {
  id: string;
  actor_id: string | null;
  tenant_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  outcome: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type Tenant = {
  id: string;
  name: string;
  parent_tenant_id: string | null;
  plan: string;
  isolation_mode: string;
  is_active: boolean;
  branding: Record<string, unknown>;
  created_at: string;
};

export const apiConfig: ApiConfig = {
  baseUrl: (process.env.NEXT_PUBLIC_API_BASE_URL || '').replace(/\/$/, ''),
};

const apiRoot = apiConfig.baseUrl ? `${apiConfig.baseUrl}/api` : '/backend-api';

async function request<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiRoot}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      ...(init.headers || {}),
    },
    cache: 'no-store',
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || 'La solicitud no pudo completarse');
  return body as T;
}

export async function login(username: string, password: string, totpCode?: string) {
  const response = await fetch(`${apiRoot}/auth/token`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, ...(totpCode ? { totp_code: totpCode } : {}) }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || 'Credenciales inválidas');
  if (body.role !== 'admin_global') throw new Error('Esta cuenta no tiene permisos de Superadmin Global');
  return body as { access: string; refresh: string; role: string; tenant_id: string | null };
}

export const getOverview = (token: string) => request<Overview>('/global/overview', token);
export const getAuditEvents = (token: string) => request<{ count: number; events: AuditEvent[]; limit: number }>('/global/audit-events?limit=50', token);
export const getTenants = (token: string) => request<Tenant[]>('/global/tenants', token);
export const createTenant = (token: string, name: string, plan: string) => request<Pick<Tenant, 'id' | 'name' | 'plan' | 'is_active'>>('/global/tenants', token, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, plan }) });
export const setTenantStatus = (token: string, tenantId: string, status: 'approved' | 'rejected') => request<{ id: string; is_active: boolean; status: string }>(`/global/tenants/${tenantId}/status`, token, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) });
