'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { AuditEvent, Overview, Tenant, createTenant, getAuditEvents, getOverview, getTenants, login, setTenantStatus } from '../lib/api';

type View = 'dashboard' | 'tenants' | 'audit';

const navItems: { id: View; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '⌂' },
  { id: 'tenants', label: 'Distribuidores', icon: '◈' },
  { id: 'audit', label: 'Auditoría', icon: '◌' },
];

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
}

function statusLabel(value: string | null | undefined) {
  return value === 'incomplete' ? 'Pendiente' : value === 'sandbox' ? 'Sandbox' : value === 'not_connected' ? 'No conectado' : value === 'not_configured' ? 'No configurado' : value || '—';
}

export default function Page() {
  const [token, setToken] = useState<string | null>(null);
  const [view, setView] = useState<View>('dashboard');
  const [loginError, setLoginError] = useState('');
  const [loading, setLoading] = useState(false);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [dataError, setDataError] = useState('');

  useEffect(() => {
    const saved = window.sessionStorage.getItem('jopets_global_access');
    if (saved) setToken(saved);
  }, []);

  useEffect(() => {
    if (!token) return;
    setDataError('');
    Promise.all([getOverview(token), getAuditEvents(token), getTenants(token)])
      .then(([nextOverview, nextAudit, nextTenants]) => { setOverview(nextOverview); setEvents(nextAudit.events); setTenants(nextTenants); })
      .catch((error: Error) => setDataError(error.message));
  }, [token]);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true); setLoginError('');
    const form = new FormData(event.currentTarget);
    try {
      const session = await login(String(form.get('username')), String(form.get('password')), String(form.get('totp') || '') || undefined);
      window.sessionStorage.setItem('jopets_global_access', session.access);
      setToken(session.access);
    } catch (error) { setLoginError(error instanceof Error ? error.message : 'No se pudo iniciar sesión'); } finally { setLoading(false); }
  }

  function signOut() { window.sessionStorage.removeItem('jopets_global_access'); setToken(null); setOverview(null); setEvents([]); setTenants([]); }

  if (!token) return <LoginScreen onSubmit={handleLogin} loading={loading} error={loginError} />;

  const title = navItems.find((item) => item.id === view)?.label || 'Dashboard';
  return <main className="shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">J</span><div><strong>JOPETS</strong><small>SIMA GLOBAL</small></div></div>
      <div className="side-caption">CONTROL CENTRAL</div>
      <nav>{navItems.map((item) => <button key={item.id} className={view === item.id ? 'nav-item active' : 'nav-item'} onClick={() => setView(item.id)}><span>{item.icon}</span>{item.label}</button>)}</nav>
      <div className="side-foot"><span className="live-dot" /> API conectable<br /><small>Scope: global_read_only</small></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><div><span className="eyebrow">PANEL GLOBAL / SIMA</span><h1>{title}</h1></div><div className="top-actions"><span className="admin-chip"><span className="avatar">S</span> Superadmin</span><button className="text-button" onClick={signOut}>Cerrar sesión</button></div></header>
      {dataError && <div className="alert error">{dataError}</div>}
      {view === 'dashboard' && <Dashboard overview={overview} events={events} />}
      {view === 'tenants' && <Tenants token={token} tenants={tenants} onRefresh={() => getTenants(token).then(setTenants)} />}
      {view === 'audit' && <Audit events={events} />}
    </section>
  </main>;
}

function LoginScreen({ onSubmit, loading, error }: { onSubmit: (event: FormEvent<HTMLFormElement>) => void; loading: boolean; error: string }) {
  return <main className="login-shell"><div className="login-art"><div className="orb orb-one" /><div className="orb orb-two" /><div className="login-brand"><span className="brand-mark large">J</span><div><strong>JOPETS</strong><small>SIMA GLOBAL</small></div></div><div className="login-copy"><span className="eyebrow">CONTROL GLOBAL</span><h1>Supervisión clara.<br /><em>Decisiones seguras.</em></h1><p>El centro de control para administrar el ecosistema de cuidado de mascotas.</p></div></div><div className="login-card"><span className="eyebrow">ACCESO RESTRINGIDO</span><h2>Bienvenido, Superadmin</h2><p className="muted">Inicia sesión con tu identidad global SIMA.</p><form onSubmit={onSubmit}><label>Correo electrónico<input name="username" type="email" placeholder="admin@sima.com" required /></label><label>Contraseña<input name="password" type="password" placeholder="••••••••••••" required /></label><label>Código MFA <span className="optional">opcional</span><input name="totp" inputMode="numeric" placeholder="000000" /></label>{error && <div className="form-error">{error}</div>}<button className="primary-button" disabled={loading}>{loading ? 'Validando…' : 'Entrar al panel'} <span>→</span></button></form><p className="security-note">Acceso protegido · Solo cuentas <strong>admin_global</strong></p></div></main>;
}

function Dashboard({ overview, events }: { overview: Overview | null; events: AuditEvent[] }) {
  const metrics = overview?.metrics || {};
  const cards = [{ label: 'Distribuidores activos', value: '—', note: 'Endpoint pendiente' }, { label: 'Transacciones auditadas', value: String(events.length), note: 'Últimos eventos cargados' }, { label: 'Ingresos de plataforma', value: metrics.mrr?.value == null ? '—' : String(metrics.mrr.value), note: statusLabel(metrics.mrr?.status) }];
  return <><div className="welcome-row"><div><h2>Resumen global</h2><p>Estado operativo del ecosistema Jopets en una sola vista.</p></div><span className="readonly-badge">● Lectura global</span></div><div className="metric-grid">{cards.map((card) => <article className="metric-card" key={card.label}><div className="metric-icon">◈</div><span>{card.label}</span><strong>{card.value}</strong><small>{card.note}</small></article>)}</div><div className="content-grid"><section className="panel"><div className="panel-heading"><div><h3>Integraciones</h3><p>Estado de servicios conectados</p></div></div>{Object.entries(overview?.integrations || { payments: { status: 'sandbox' }, gps: { status: 'not_connected' }, ai: { status: 'not_configured' } }).map(([name, item]) => <div className="integration-row" key={name}><span className="integration-symbol">{name === 'payments' ? '$' : name === 'gps' ? '⌖' : '✦'}</span><strong>{name.toUpperCase()}</strong><span className="status-pill">{statusLabel(item.status)}</span></div>)}</section><section className="panel"><div className="panel-heading"><div><h3>Actividad reciente</h3><p>Últimos eventos de auditoría</p></div><span className="count-badge">{events.length}</span></div>{events.slice(0, 4).map((event) => <EventRow event={event} key={event.id} />)}{events.length === 0 && <Empty text="No hay eventos disponibles." />}</section></div></>;
}

function Tenants({ token, tenants, onRefresh }: { token: string; tenants: Tenant[]; onRefresh: () => Promise<void> }) {
  const [name, setName] = useState('');
  const [plan, setPlan] = useState('starter');
  const [error, setError] = useState('');
  async function addTenant() {
    if (!name.trim()) return;
    try { await createTenant(token, name.trim(), plan); setName(''); setError(''); await onRefresh(); } catch (error) { setError(error instanceof Error ? error.message : 'No se pudo crear el distribuidor'); }
  }
  async function changeStatus(id: string, status: 'approved' | 'rejected') {
    try { await setTenantStatus(token, id, status); await onRefresh(); } catch (error) { setError(error instanceof Error ? error.message : 'No se pudo actualizar el estado'); }
  }
  return <><div className="welcome-row"><div><h2>Distribuidores</h2><p>Gestiona las marcas blancas del ecosistema.</p></div><div className="top-actions"><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Nombre" /><select value={plan} onChange={(event) => setPlan(event.target.value)}><option value="starter">Starter</option><option value="premium">Premium</option><option value="enterprise">Enterprise</option></select><button className="primary-button compact" onClick={addTenant}>+ Crear</button></div></div>{error && <div className="alert error">{error}</div>}<div className="panel"><div className="table-wrap"><table><thead><tr><th>Nombre</th><th>Plan</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{tenants.map((tenant) => <tr key={tenant.id}><td><strong>{tenant.name}</strong><br /><small>{tenant.id}</small></td><td>{tenant.plan}</td><td><span className={tenant.is_active ? 'result' : 'result rejected'}>{tenant.is_active ? 'Aprobado' : 'Pendiente'}</span></td><td>{tenant.is_active ? <button className="text-button" onClick={() => changeStatus(tenant.id, 'rejected')}>Rechazar</button> : <button className="text-button" onClick={() => changeStatus(tenant.id, 'approved')}>Aprobar</button>}</td></tr>)}</tbody></table>{tenants.length === 0 && <Empty text="No hay distribuidores registrados." />}</div></div></>;
}

function Audit({ events }: { events: AuditEvent[] }) { return <div className="panel audit-panel"><div className="panel-heading"><div><h2>Auditoría global</h2><p>Eventos sensibles registrados por toda la plataforma.</p></div><span className="count-badge">{events.length} eventos</span></div><div className="table-wrap"><table><thead><tr><th>Fecha</th><th>Acción</th><th>Recurso</th><th>Tenant</th><th>Resultado</th></tr></thead><tbody>{events.map((event) => <tr key={event.id}><td>{event.created_at ? formatDate(event.created_at) : '—'}</td><td><strong>{event.action}</strong></td><td>{event.resource_type}<br /><small>{event.resource_id || '—'}</small></td><td><code>{event.tenant_id || 'global'}</code></td><td><span className={event.outcome === 'rejected' ? 'result rejected' : 'result'}>{event.outcome || 'accepted'}</span></td></tr>)}</tbody></table>{events.length === 0 && <Empty text="No hay eventos de auditoría disponibles." />}</div></div>; }

function EventRow({ event }: { event: AuditEvent }) { return <div className="event-row"><span className="event-dot" /><div><strong>{event.action}</strong><small>{event.resource_type} · {event.outcome || 'accepted'}</small></div><time>{event.created_at ? formatDate(event.created_at) : '—'}</time></div>; }
function Empty({ text }: { text: string }) { return <div className="empty-state">{text}</div>; }
