let API = document.getElementById('apiBase').value;

function headers() {
  const key = document.getElementById('apiKey').value || '';
  return { 'Content-Type': 'application/json', 'X-API-KEY': key };
}

async function fetchJSON(url, opts={}) {
  const r = await fetch(url, { ...opts, headers: { ...(opts.headers||{}), ...headers() } });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function setTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab[data-tab="${tab}"]`).classList.add('active');
  document.querySelectorAll('.tabpane').forEach(p => p.style.display = 'none');
  document.getElementById(tab).style.display = 'block';
}

document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  setTab(t.dataset.tab);
  refresh();
}));

async function loadPending() {
  const rows = await fetchJSON(`${API}/help_requests/pending`);
  const el = document.getElementById('pending');
  if (rows.length === 0) { el.innerHTML = '<p class="card">No pending requests 🎉</p>'; return; }
  el.innerHTML = rows.map(r => `
    <div class="card">
      <div class="row"><strong>#${r.id}</strong><span class="badge ${r.status}">${r.status}</span></div>
      <div><strong>Caller:</strong> ${r.caller_id}</div>
      <div><strong>Question:</strong> ${r.question_text}</div>
      <div style="margin-top:8px">
        <textarea id="ans_${r.id}" placeholder="Type your answer to text back..."></textarea>
        <button onclick="reply(${r.id})">Submit Answer</button>
      </div>
    </div>
  `).join('');
}

async function loadHistory() {
  const rows = await fetchJSON(`${API}/help_requests/`);
  const el = document.getElementById('history');
  if (rows.length === 0) { el.innerHTML = '<p class="card">No requests yet.</p>'; return; }
  el.innerHTML = `
    <table>
      <thead><tr><th>ID</th><th>Status</th><th>Caller</th><th>Question</th><th>Answer</th><th>Created</th><th>Resolved</th></tr></thead>
      <tbody>
        ${rows.map(r => `
          <tr>
            <td>${r.id}</td>
            <td><span class="badge ${r.status}">${r.status}</span></td>
            <td>${r.caller_id}</td>
            <td>${r.question_text}</td>
            <td>${r.supervisor_answer ?? ''}</td>
            <td>${new Date(r.created_at).toLocaleString()}</td>
            <td>${r.resolved_at ? new Date(r.resolved_at).toLocaleString() : ''}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

async function loadKB() {
  const rows = await fetchJSON(`${API}/kb/`);
  const el = document.getElementById('kb');
  if (rows.length === 0) { el.innerHTML = '<p class="card">No learned answers yet.</p>'; return; }
  el.innerHTML = rows.map(r => `
    <div class="card">
      <div class="row"><strong>#${r.id}</strong><span>Source: ${r.source}</span><span>Used: ${r.usage_count}</span></div>
      <div><strong>Q:</strong> ${r.question_text}</div>
      <div><strong>A:</strong> ${r.answer_text}</div>
    </div>
  `).join('');
}

async function reply(id) {
  const textarea = document.getElementById(`ans_${id}`);
  const answer_text = textarea.value.trim();
  if (!answer_text) { alert('Please enter an answer.'); return; }
  await fetchJSON(`${API}/help_requests/${id}/reply`, {
    method: 'POST',
    body: JSON.stringify({ answer_text })
  });
  alert('Replied and texted the caller.');
  textarea.value = '';
  refresh();
}
async function connect() {
  const btn = document.getElementById('connectBtn');
  const status = document.getElementById('connStatus');
  try {
    btn.disabled = true;
    status.textContent = 'Connecting...';
    // pick up latest values
    API = (document.getElementById('apiBase').value || '').trim();
    if (!API || !API.startsWith('http')) {
      throw new Error('Please enter a valid API Base like http://localhost:8000');
    }

    // 1) health (no auth)
    const health = await fetch(`${API}/health`);
    if (!health.ok) throw new Error(await health.text());

    // 2) protected route (validates X-API-KEY)
    await fetchJSON(`${API}/help_requests/pending`);

    // 3) load current tab
    await refresh();

    status.textContent = 'Connected ✅';
  } catch (e) {
    status.textContent = 'Connect failed ❌';
    alert('Connect failed:\n' + e);
  } finally {
    btn.disabled = false;
  }
}


async function refresh() {
  API = document.getElementById('apiBase').value;
  const active = document.querySelector('.tab.active').dataset.tab;
  if (active === 'pending') await loadPending();
  if (active === 'history') await loadHistory();
  if (active === 'kb') await loadKB();
}

async function simulate() {
  API = document.getElementById('apiBase').value;
  const caller = document.getElementById('simCaller').value.trim();
  const question = document.getElementById('simQuestion').value.trim();
  const out = document.getElementById('simOut');
  try {
    const res = await fetchJSON(`${API}/agent/simulate_call`, {
      method: 'POST',
      body: JSON.stringify({ caller_id: caller, question })
    });
    out.textContent = JSON.stringify(res, null, 2);
    refresh();
  } catch (e) {
    out.textContent = 'Error: ' + e;
  }
}

setTab('pending');
refresh();
setInterval(refresh, 5000);
