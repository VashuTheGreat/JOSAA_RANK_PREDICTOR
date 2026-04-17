// ══════════════════════════════════════════════════════
//  JOSAA Rank Predictor — script.js
// ══════════════════════════════════════════════════════

/* ── Tab switching ────────────────────────────────── */
let isAuthenticated = false;

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tabName = btn.dataset.tab;

    // Secure the generate and admin tabs
    if (tabName === 'generate' || tabName === 'admin') {
      if (!isAuthenticated) {
        const pwd = prompt("Enter password to access this secure section:");
        if (pwd !== "alookhalo") {
          toast("Access Denied: Incorrect password.", "error");
          return;
        }
        isAuthenticated = true;
        toast("Access Granted!", "success");
      }
    }

    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('content-' + tabName).classList.add('active');
  });
});

/* ── Toast ────────────────────────────────────────── */
function toast(msg, type = 'info', duration = 3500) {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-icon">${icons[type]}</span><span>${msg}</span>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => {
    el.classList.add('fadeout');
    setTimeout(() => el.remove(), 300);
  }, duration);
}

/* ── Button loading state ─────────────────────────── */
function setLoading(btn, on) {
  if (on) { btn.classList.add('loading'); btn.disabled = true; }
  else { btn.classList.remove('loading'); btn.disabled = false; }
}

/* ── Build table from records array ──────────────── */
function buildTable(records, containerEl, colsConfig) {
  if (!records || records.length === 0) return null;
  const cols = colsConfig || Object.keys(records[0]);

  let html = '<table><thead><tr>';
  cols.forEach(c => {
    const label = typeof c === 'object' ? c.label : c;
    html += `<th>${label}</th>`;
  });
  html += '</tr></thead><tbody>';

  records.forEach(row => {
    html += '<tr>';
    cols.forEach(c => {
      const key = typeof c === 'object' ? c.key : c;
      let val = row[key];
      if (key === 'status') {
        const cls = val === 'Safe' ? 'status-safe' : val === 'Borderline' ? 'status-borderline' : 'status-low';
        val = `<span class="status-badge ${cls}">${val}</span>`;
      } else if (typeof val === 'number') {
        val = Number.isInteger(val) ? val.toLocaleString() : val.toFixed(1);
      } else {
        val = val !== null && val !== undefined ? val : '—';
      }
      html += `<td>${val}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  containerEl.innerHTML = html;
  return html;
}

/* ════════════════════════════════════════════════════
   TAB 1 — Rank-based Recommendations
════════════════════════════════════════════════════ */
async function fetchRecommendations() {
  const btn = document.getElementById('btn-recommend');
  setLoading(btn, true);

  const params = new URLSearchParams({
    rank:      document.getElementById('rec-rank').value,
    category:  document.getElementById('rec-category').value,
    gender:    document.getElementById('rec-gender').value,
    quota:     document.getElementById('rec-quota').value,
    round:     document.getElementById('rec-round').value,
    year:      document.getElementById('rec-year').value,
  });

  try {
    const res = await fetch(`/api/cuttOff/rank_based_recommend?${params}`, { method: 'POST' });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    const wrap   = document.getElementById('rec-results-wrap');
    const tableW = document.getElementById('rec-table-wrap');
    const empty  = document.getElementById('rec-empty');
    const countEl = document.getElementById('rec-count');

    if (!Array.isArray(data) || data.length === 0) {
      wrap.style.display  = 'none';
      empty.classList.remove('hidden');
      toast('No colleges found for this rank. Try relaxing your filters.', 'info');
    } else {
      empty.classList.add('hidden');
      wrap.style.display = 'block';
      countEl.textContent = data.length;
      buildTable(data, tableW, [
        { key: 'Institute', label: 'Institute' },
        { key: 'Academic Program Name', label: 'Program' },
        { key: 'Seat Type', label: 'Category' },
        { key: 'Quota', label: 'Quota' },
        { key: 'Round', label: 'Round' },
        { key: 'Opening Rank', label: 'Opening' },
        { key: 'Closing Rank', label: 'Closing' },
        { key: 'status', label: 'Chance' },
      ]);
      toast(`Found ${data.length} colleges!`, 'success');
    }
  } catch (err) {
    toast('Error: ' + err.message, 'error');
  } finally {
    setLoading(btn, false);
  }
}

/* ════════════════════════════════════════════════════
   TAB 2 — Cutoff Checker
════════════════════════════════════════════════════ */
async function fetchCutoffs() {
  const btn = document.getElementById('btn-cutoff');
  setLoading(btn, true);

  const params = new URLSearchParams({
    category: document.getElementById('cut-category').value,
    gender:   document.getElementById('cut-gender').value,
    quota:    document.getElementById('cut-quota').value,
    year:     document.getElementById('cut-year').value,
  });

  const college = document.getElementById('cut-college').value.trim();
  const branch  = document.getElementById('cut-branch').value.trim();
  if (college) params.append('college', college);
  if (branch)  params.append('branch', branch);

  try {
    const res = await fetch(`/api/cuttOff/cutOffcheck?${params}`, { method: 'POST' });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    const wrap   = document.getElementById('cut-results-wrap');
    const tableW = document.getElementById('cut-table-wrap');
    const empty  = document.getElementById('cut-empty');
    const countEl = document.getElementById('cut-count');

    if (!Array.isArray(data) || data.length === 0) {
      wrap.style.display  = 'none';
      empty.classList.remove('hidden');
      toast('No cutoff data found. Try different filters.', 'info');
    } else {
      empty.classList.add('hidden');
      wrap.style.display = 'block';
      countEl.textContent = data.length;
      buildTable(data, tableW, [
        { key: 'Institute', label: 'Institute' },
        { key: 'Academic Program Name', label: 'Program' },
        { key: 'Seat Type', label: 'Category' },
        { key: 'Gender', label: 'Gender' },
        { key: 'Quota', label: 'Quota' },
        { key: 'Round', label: 'Round' },
        { key: 'Year', label: 'Year' },
        { key: 'Opening Rank', label: 'Opening' },
        { key: 'Closing Rank', label: 'Closing' },
      ]);
      toast(`Loaded ${data.length} cutoff records.`, 'success');
    }
  } catch (err) {
    toast('Error: ' + err.message, 'error');
  } finally {
    setLoading(btn, false);
  }
}

/* ════════════════════════════════════════════════════
   TAB 3 — Generate Predictions
════════════════════════════════════════════════════ */
function setStep(id, state, statusText) {
  const el = document.getElementById(id);
  el.className = `step ${state}`;
  el.querySelector('.step-status').textContent = statusText;
}

async function runGenerate() {
  const btn = document.getElementById('btn-generate');
  setLoading(btn, true);

  const year       = document.getElementById('gen-year').value;
  const candidates = document.getElementById('gen-candidates').value;
  const stepsCard  = document.getElementById('gen-steps-card');

  stepsCard.style.display = 'block';
  ['step-download','step-transform','step-predict','step-save'].forEach(id => setStep(id, '', 'Waiting'));

  // Animate visual steps while request is in-flight
  setTimeout(() => setStep('step-download', 'active', 'Running…'), 200);
  setTimeout(() => setStep('step-transform', 'active', 'Running…'), 4000);
  setTimeout(() => setStep('step-predict', 'active', 'Running…'), 8000);

  try {
    const params = new URLSearchParams({ year, appeared_candidates: candidates });
    const res = await fetch(`/api/fit_on_year/fit_on_year?${params}`, { method: 'POST' });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    if (data.success) {
      setStep('step-download', 'done', 'Done ✓');
      setStep('step-transform', 'done', 'Done ✓');
      setStep('step-predict', 'done', 'Done ✓');
      setStep('step-save', 'done', 'Done ✓');
      toast(`Predictions generated for ${year}!`, 'success', 5000);
    } else {
      setStep('step-download', 'error', 'Error');
      setStep('step-transform', 'error', 'Error');
      setStep('step-predict', 'error', 'Error');
      setStep('step-save', 'error', 'Error');
      toast('Failed: ' + data.message, 'error', 6000);
    }
  } catch (err) {
    setStep('step-predict', 'error', 'Error');
    toast('Error: ' + err.message, 'error');
  } finally {
    setLoading(btn, false);
  }
}

/* ════════════════════════════════════════════════════
   TAB 4 — Admin / Retrain
════════════════════════════════════════════════════ */
async function runRetrain() {
  const btn    = document.getElementById('btn-retrain');
  const logBox = document.getElementById('retrain-log');
  setLoading(btn, true);
  logBox.style.display = 'block';
  logBox.innerHTML = '<p>⏳ Starting full training pipeline…</p>';
  toast('Retraining started. This may take several minutes.', 'info', 5000);

  try {
    const res = await fetch('/api/retrain_model/retrain', { method: 'GET' });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    if (data.success) {
      logBox.innerHTML += '<p>✅ Training complete. New model logged to MLflow.</p>';
      toast('Model retrained successfully!', 'success', 5000);
    } else {
      logBox.innerHTML += `<p>❌ Error: ${data.message || 'Unknown error'}</p>`;
      toast('Retraining failed: ' + (data.message || ''), 'error', 6000);
    }
  } catch (err) {
    logBox.innerHTML += `<p>❌ ${err.message}</p>`;
    toast('Error: ' + err.message, 'error');
  } finally {
    setLoading(btn, false);
  }
}

/* ════════════════════════════════════════════════════
   Hero stats + college dropdown
════════════════════════════════════════════════════ */
let instituteBranchMap = {};

async function loadStats() {
  try {
    const res = await fetch('/api/available_data/available_data');
    if (!res.ok) return;
    const { data } = await res.json();
    if (!data) return;

    const institutes = data['Institute'] ? data['Institute'].length : 0;
    const programs   = data['Academic Program Name'] ? data['Academic Program Name'].length : 0;

    animateNumber(document.getElementById('stat-institutes'), institutes);
    animateNumber(document.getElementById('stat-programs'), programs);

    // Populate college dropdown
    const collegeSelect = document.getElementById('cut-college');
    if (data['Institute']) {
      [...data['Institute']]
        .sort()
        .forEach(inst => {
          const opt = document.createElement('option');
          opt.value = inst;
          opt.textContent = inst;
          collegeSelect.appendChild(opt);
        });
    }
  } catch (_) { /* silently skip */ }
}

async function loadInstituteBranches() {
  try {
    const res = await fetch('/api/available_data/institute_branches');
    if (!res.ok) return;
    const { data } = await res.json();
    if (!data) return;
    instituteBranchMap = data;

    const collegeSelect = document.getElementById('cut-college');
    const branchSelect  = document.getElementById('cut-branch');

    function updateBranches() {
      const selected = collegeSelect.value;
      branchSelect.innerHTML = '<option value="">— All Branches —</option>';

      const branches = selected && instituteBranchMap[selected]
        ? instituteBranchMap[selected]
        : [...new Set(Object.values(instituteBranchMap).flat())].sort();

      branches.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b;
        opt.textContent = b;
        branchSelect.appendChild(opt);
      });
    }

    // Initial fill (all branches) + reactive update on college change
    updateBranches();
    collegeSelect.addEventListener('change', updateBranches);
  } catch (_) { /* silently skip */ }
}

function animateNumber(el, target) {
  const duration = 1200;
  const start = performance.now();
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(eased * target).toLocaleString();
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

// Boot
loadStats();
loadInstituteBranches();
