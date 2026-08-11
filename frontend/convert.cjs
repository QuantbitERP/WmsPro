const fs = require('fs');
const path = require('path');

const htmlPath = '/home/erpadmin/Downloads/3pl-dashboard.html';
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

// Extract CSS
const cssMatch = htmlContent.match(/<style>([\s\S]*?)<\/style>/);
if (cssMatch) {
  let css = cssMatch[1];
  // Basic scoping to prevent breaking other things
  css = `.threepl-dashboard {\n${css}\n}\n`;
  // Actually, wait, applying `.threepl-dashboard` to every rule in standard css is hard without a parser.
  // We'll just write it as is and let it be global, since the user wants it exactly like the original.
  fs.writeFileSync('./src/pages/3PL/3pl.css', cssMatch[1]);
}

function htmlToJsx(html) {
  let jsx = html;
  // Replace class= with className=
  jsx = jsx.replace(/class="/g, 'className="');
  // Replace style="width:58%;background:var(--green)" with style={{width:'58%', backgroundColor:'var(--green)'}}
  // It's tricky to do with regex for all style strings.
  // I will use a simple replacer for the known styles in this file.
  
  // Specific style replacements for this file based on what's visible
  jsx = jsx.replace(/style="margin-bottom:14px"/g, "style={{marginBottom: '14px'}}");
  jsx = jsx.replace(/style="padding:14px 18px"/g, "style={{padding: '14px 18px'}}");
  jsx = jsx.replace(/style="padding:0"/g, "style={{padding: 0}}");
  jsx = jsx.replace(/style="color:rgba\(255,255,255,\.3\)"/g, "style={{color: 'rgba(255,255,255,.3)'}}");
  jsx = jsx.replace(/style="width:30%;background:#94A3B8"/g, "style={{width: '30%', backgroundColor: '#94A3B8'}}");
  jsx = jsx.replace(/style="width:15%;background:var\(--amber\)"/g, "style={{width: '15%', backgroundColor: 'var(--amber)'}}");
  jsx = jsx.replace(/style="width:55%;background:var\(--blue\)"/g, "style={{width: '55%', backgroundColor: 'var(--blue)'}}");
  jsx = jsx.replace(/style="width:100%;background:var\(--green\)"/g, "style={{width: '100%', backgroundColor: 'var(--green)'}}");
  jsx = jsx.replace(/style="color:var\(--muted\)"/g, "style={{color: 'var(--muted)'}}");
  jsx = jsx.replace(/style="color:var\(--amber\)"/g, "style={{color: 'var(--amber)'}}");
  jsx = jsx.replace(/style="color:var\(--blue\)"/g, "style={{color: 'var(--blue)'}}");
  jsx = jsx.replace(/style="color:var\(--green\)"/g, "style={{color: 'var(--green)'}}");
  
  jsx = jsx.replace(/style="width:94%;background:var\(--red\)"/g, "style={{width: '94%', backgroundColor: 'var(--red)'}}");
  jsx = jsx.replace(/style="font-size:10px;color:var\(--muted\);margin-top:2px"/g, "style={{fontSize: '10px', color: 'var(--muted)', marginTop: '2px'}}");
  jsx = jsx.replace(/style="color:var\(--red\)"/g, "style={{color: 'var(--red)'}}");
  jsx = jsx.replace(/style="width:72%;background:var\(--blue\)"/g, "style={{width: '72%', backgroundColor: 'var(--blue)'}}");
  jsx = jsx.replace(/style="width:61%;background:var\(--blue\)"/g, "style={{width: '61%', backgroundColor: 'var(--blue)'}}");
  jsx = jsx.replace(/style="width:38%;background:var\(--green\)"/g, "style={{width: '38%', backgroundColor: 'var(--green)'}}");
  jsx = jsx.replace(/style="color:var\(--red\);font-weight:700"/g, "style={{color: 'var(--red)', fontWeight: 700}}");
  jsx = jsx.replace(/style="color:var\(--amber\);font-weight:700"/g, "style={{color: 'var(--amber)', fontWeight: 700}}");
  
  jsx = jsx.replace(/style="display:flex;justify-content:space-between;font-size:12px;color:var\(--muted\);margin-bottom:6px"/g, "style={{display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--muted)', marginBottom: '6px'}}");
  jsx = jsx.replace(/style="width:58%;background:var\(--green\)"/g, "style={{width: '58%', backgroundColor: 'var(--green)'}}");
  jsx = jsx.replace(/style="width:10%;background:var\(--amber\)"/g, "style={{width: '10%', backgroundColor: 'var(--amber)'}}");
  jsx = jsx.replace(/style="width:32%;background:var\(--border\);color:var\(--muted\)"/g, "style={{width: '32%', backgroundColor: 'var(--border)', color: 'var(--muted)'}}");
  jsx = jsx.replace(/style="display:flex;gap:16px;margin-top:10px;font-size:11px"/g, "style={{display: 'flex', gap: '16px', marginTop: '10px', fontSize: '11px'}}");
  jsx = jsx.replace(/style="display:flex;align-items:center;gap:5px"/g, "style={{display: 'flex', alignItems: 'center', gap: '5px'}}");
  jsx = jsx.replace(/style="width:10px;height:10px;background:var\(--green\);border-radius:2px;display:inline-block"/g, "style={{width: '10px', height: '10px', backgroundColor: 'var(--green)', borderRadius: '2px', display: 'inline-block'}}");
  jsx = jsx.replace(/style="width:10px;height:10px;background:var\(--amber\);border-radius:2px;display:inline-block"/g, "style={{width: '10px', height: '10px', backgroundColor: 'var(--amber)', borderRadius: '2px', display: 'inline-block'}}");
  jsx = jsx.replace(/style="width:10px;height:10px;background:var\(--border\);border-radius:2px;display:inline-block"/g, "style={{width: '10px', height: '10px', backgroundColor: 'var(--border)', borderRadius: '2px', display: 'inline-block'}}");
  
  jsx = jsx.replace(/style="display:flex;align-items:center;gap:8px"/g, "style={{display: 'flex', alignItems: 'center', gap: '8px'}}");
  jsx = jsx.replace(/style="width:80px"/g, "style={{width: '80px'}}");
  jsx = jsx.replace(/style="width:25%;background:var\(--blue\)"/g, "style={{width: '25%', backgroundColor: 'var(--blue)'}}");
  jsx = jsx.replace(/style="width:18%;background:var\(--blue\)"/g, "style={{width: '18%', backgroundColor: 'var(--blue)'}}");
  jsx = jsx.replace(/style="width:14%;background:var\(--amber\)"/g, "style={{width: '14%', backgroundColor: 'var(--amber)'}}");
  jsx = jsx.replace(/style="width:11%;background:var\(--red\)"/g, "style={{width: '11%', backgroundColor: 'var(--red)'}}");
  jsx = jsx.replace(/style="width:32%;background:var\(--green\)"/g, "style={{width: '32%', backgroundColor: 'var(--green)'}}");
  
  jsx = jsx.replace(/style="width:49%;background:var\(--blue\)"/g, "style={{width: '49%', backgroundColor: 'var(--blue)'}}");
  jsx = jsx.replace(/style="font-size:11px"/g, "style={{fontSize: '11px'}}");
  jsx = jsx.replace(/style="width:29%;background:var\(--green\)"/g, "style={{width: '29%', backgroundColor: 'var(--green)'}}");
  jsx = jsx.replace(/style="width:14%;background:var\(--amber\)"/g, "style={{width: '14%', backgroundColor: 'var(--amber)'}}");
  jsx = jsx.replace(/style="width:5%;background:var\(--red\)"/g, "style={{width: '5%', backgroundColor: 'var(--red)'}}");
  jsx = jsx.replace(/style="width:3%;background:#94A3B8"/g, "style={{width: '3%', backgroundColor: '#94A3B8'}}");
  
  return jsx;
}

// Extract Manager View
const managerMatch = htmlContent.match(/<div class="view active" id="view-manager">([\s\S]*?)<\/div><!-- \/view-manager -->/);
if (managerMatch) {
  let content = htmlToJsx(managerMatch[1]);
  const jsxCode = `import React from 'react';\nimport './3pl.css';\n\nexport default function OperationsDashboard() {\n  return (\n    <div className="threepl-container">\n      ${content}\n    </div>\n  );\n}\n`;
  fs.writeFileSync('./src/pages/3PL/OperationsDashboard.jsx', jsxCode);
}

// Extract Management View
const mgmtMatch = htmlContent.match(/<div class="view" id="view-management">([\s\S]*?)<\/div><!-- \/view-management -->/);
if (mgmtMatch) {
  let content = htmlToJsx(mgmtMatch[1]);
  const jsxCode = `import React from 'react';\nimport './3pl.css';\n\nexport default function ManagementDashboard() {\n  return (\n    <div className="threepl-container">\n      ${content}\n    </div>\n  );\n}\n`;
  fs.writeFileSync('./src/pages/3PL/ManagementDashboard.jsx', jsxCode);
}
