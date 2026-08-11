#!/bin/bash
cat << 'CSS' >> src/dashboard.css

/* ─── RESTORED PROCUREX CSS ───────────────────────────────────────── */
:root {
  --sidebar-bg: #0B1121;
}

.login-container { display: flex; height: 100vh; overflow: hidden; background: var(--surface); }
.login-left { flex: 1; background: var(--sidebar-bg); color: #fff; padding: 40px; display: flex; flex-direction: column; justify-content: space-between; }
.login-brand { display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 700; color: #fff; }
.login-hero h1 { font-size: 32px; font-weight: 700; margin-bottom: 16px; line-height: 1.2; }
.login-hero p { font-size: 16px; color: rgba(255,255,255,0.7); margin-bottom: 32px; max-width: 500px; line-height: 1.5; }
.badge-dark { display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 24px; }
.login-features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 32px; }
.feature-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; transition: all 0.2s; }
.feature-card:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2); }
.feature-card svg { margin-bottom: 12px; color: var(--blue); }
.ft-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.ft-desc { font-size: 12px; color: rgba(255,255,255,0.6); }
.login-footer { font-size: 13px; color: rgba(255,255,255,0.4); }
.login-right { flex: 1; background-color: var(--white); display: flex; align-items: center; justify-content: center; padding: 40px; }
.login-form-wrapper { width: 100%; max-width: 400px; }
.login-form-wrapper h2 { font-size: 28px; font-weight: 700; color: var(--ink); margin-bottom: 8px; letter-spacing: -0.5px; }
.login-form-wrapper p { font-size: 14px; color: var(--muted); margin-bottom: 32px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; color: var(--ink); margin-bottom: 6px; }
.form-control { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; font-family: 'Inter', sans-serif; transition: all 0.2s; }
.form-control:focus { outline: none; border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-lt); }

.btn-primary { width: 100%; padding: 12px; background: var(--blue); color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; }
.btn-primary:hover { background: var(--blue-md); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.alert { padding: 12px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; margin-bottom: 24px; }
.alert.danger { background: var(--red-lt); color: var(--red); border: 1px solid rgba(239,68,68,0.2); }

/* ProcureX App Shell */
.app-container { display: flex; height: 100vh; overflow: hidden; }
.sidebar-px { width: 260px; background-color: var(--sidebar-bg); color: #fff; display: flex; flex-direction: column; flex-shrink: 0; }
.sidebar-header { padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.sidebar-brand { display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 700; }
.sidebar-content { padding: 24px 16px; flex: 1; overflow-y: auto; }
.nav-section { margin-bottom: 24px; }
.nav-label { font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; padding: 0 12px; }
.nav-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-radius: 8px; color: rgba(255,255,255,0.7); cursor: pointer; transition: all 0.2s; font-weight: 500; font-size: 14px; margin-bottom: 4px; }
.nav-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
.nav-item.active { background: var(--blue); color: #fff; }
.nav-item-left { display: flex; align-items: center; gap: 12px; }

.main-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: var(--surface); }
.topbar-px { height: 64px; background: #fff; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; flex-shrink: 0; }
.breadcrumbs { font-size: 14px; color: var(--muted); }
.breadcrumbs strong { color: var(--ink); font-weight: 600; }
.content-wrapper { padding: 24px 32px; flex: 1; overflow-y: auto; }

.search-bar { position: relative; display: flex; align-items: center; }
.search-bar svg { position: absolute; left: 12px; }
.search-bar input { padding: 8px 12px 8px 36px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; font-family: 'Inter', sans-serif; width: 240px; background: var(--surface); transition: all 0.2s; }
.search-bar input:focus { outline: none; background: #fff; border-color: var(--blue); }
.shortcut { position: absolute; right: 8px; font-size: 10px; font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--muted); background: var(--white); border: 1px solid var(--border); padding: 2px 4px; border-radius: 4px; }

.icon-btn { background: none; border: none; color: var(--muted); cursor: pointer; padding: 6px; border-radius: 6px; transition: all 0.2s; position: relative; }
.icon-btn:hover { background: var(--surface); color: var(--ink); }
.indicator { position: absolute; top: 6px; right: 6px; width: 6px; height: 6px; background: var(--red); border-radius: 50%; border: 1.5px solid #fff; }
.avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--blue); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; cursor: pointer; }

CSS
bash fix_css.sh
