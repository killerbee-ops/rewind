// REWIND - Client Application Logic (Clean & Simple)

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const taskInput = document.getElementById('taskInput');
  const taskTag = document.getElementById('taskTag');
  const taskTime = document.getElementById('taskTime');
  const taskHour = document.getElementById('taskHour');
  const liveScanner = document.getElementById('liveScanner');
  const scannerText = document.getElementById('scannerText');
  const todoForm = document.getElementById('todoForm');
  const todoList = document.getElementById('todoList');

  const regretForm = document.getElementById('regretForm');
  const regretDesc = document.getElementById('regretDesc');
  const regretTag = document.getElementById('regretTag');
  const regretTime = document.getElementById('regretTime');
  const regretHour = document.getElementById('regretHour');
  const regretContext = document.getElementById('regretContext');
  const regretIntensity = document.getElementById('regretIntensity');
  const intensityVal = document.getElementById('intensityVal');
  const regretSearch = document.getElementById('regretSearch');
  const regretFilterTag = document.getElementById('regretFilterTag');
  const regretList = document.getElementById('regretList');

  const patternsGrid = document.getElementById('patternsGrid');
  const statPrevented = document.getElementById('statPrevented');
  const statWarnings = document.getElementById('statWarnings');
  const statRegrets = document.getElementById('statRegrets');
  const statActive = document.getElementById('statActive');
  const statTopTag = document.getElementById('statTopTag');

  const btnSeed = document.getElementById('btnSeed');
  const btnReset = document.getElementById('btnReset');

  // Modal elements
  const warningModal = document.getElementById('warningModal');
  const modalHeadline = document.getElementById('modalHeadline');
  const modalMessage = document.getElementById('modalMessage');
  const evidenceMatchTag = document.getElementById('evidenceMatchTag');
  const evidenceScore = document.getElementById('evidenceScore');
  const evidenceQuote = document.getElementById('evidenceQuote');
  const evidenceReasons = document.getElementById('evidenceReasons');
  const btnProceedAnyway = document.getElementById('btnProceedAnyway');
  const btnReconsider = document.getElementById('btnReconsider');

  // Academic Modal Elements
  const btnAcademicInfo = document.getElementById('btnAcademicInfo');
  const linkAcademic = document.getElementById('linkAcademic');
  const academicModal = document.getElementById('academicModal');
  const btnCloseAcademic = document.getElementById('btnCloseAcademic');

  let currentTodoFilter = 'All';
  let pendingTaskData = null;
  let debounceTimer = null;

  // --- Tab Navigation ---
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.dataset.tab;
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });

  // --- Quick Example Chips ---
  document.querySelectorAll('.example-chip[data-task]').forEach(btn => {
    btn.addEventListener('click', () => {
      taskInput.value = btn.dataset.task;
      taskTag.value = btn.dataset.tag;
      taskTime.value = btn.dataset.time;
      taskHour.value = btn.dataset.hour;
      triggerLiveEvaluation();
      taskInput.focus();
    });
  });

  // --- Intensity Slider Listener ---
  if (regretIntensity && intensityVal) {
    regretIntensity.addEventListener('input', (e) => {
      const val = e.target.value;
      intensityVal.textContent = `${val}/5`;
    });
  }

  // --- Live Typing Evaluation Scanner ---
  function triggerLiveEvaluation() {
    clearTimeout(debounceTimer);
    const task = taskInput.value.trim();
    if (!task) {
      liveScanner.classList.remove('warning-state');
      scannerText.textContent = "Live Scanner: Type an upcoming action to scan against past regrets.";
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const res = await API.evaluateTask({
          task: task,
          tag: taskTag.value,
          planned_time: taskTime.value,
          planned_hour: parseInt(taskHour.value) || 20
        });

        if (res.should_warn) {
          liveScanner.classList.add('warning-state');
          scannerText.innerHTML = `<strong>⚠️ Evidence Alert (${res.confidence_pct}%):</strong> ${res.message}`;
        } else {
          liveScanner.classList.remove('warning-state');
          scannerText.innerHTML = `<strong>✓ Clear:</strong> No significant regret pattern matched. Safe to proceed.`;
        }
      } catch (err) {
        console.error("Live scanner evaluation error:", err);
      }
    }, 250);
  }

  taskInput.addEventListener('input', triggerLiveEvaluation);
  taskTag.addEventListener('change', triggerLiveEvaluation);
  taskTime.addEventListener('change', triggerLiveEvaluation);
  taskHour.addEventListener('input', triggerLiveEvaluation);

  // --- Todo Form Submit (Decision Intervention Point) ---
  todoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const task = taskInput.value.trim();
    if (!task) return;

    const taskPayload = {
      task: task,
      tag: taskTag.value,
      planned_time: taskTime.value,
      planned_hour: parseInt(taskHour.value) || 20
    };

    // Evaluate against regrets
    const evalResult = await API.evaluateTask(taskPayload);

    if (evalResult.should_warn) {
      pendingTaskData = taskPayload;
      showWarningModal(evalResult);
    } else {
      await API.createTodo({ ...taskPayload, user_action: 'proceed' });
      taskInput.value = '';
      triggerLiveEvaluation();
      refreshAll();
    }
  });

  function showWarningModal(evalResult) {
    modalHeadline.textContent = evalResult.headline || "Wait a moment — check your history";
    modalMessage.textContent = evalResult.message;
    const top = evalResult.top_match;
    if (top) {
      evidenceMatchTag.textContent = `Category: ${top.regret_tag}`;
      evidenceScore.textContent = `Similarity: ${evalResult.confidence_pct}%`;
      evidenceQuote.textContent = `"${top.regret_description}"`;
      evidenceReasons.innerHTML = top.reasons.map(r => `• ${r}`).join('<br>');
    }
    warningModal.classList.add('active');
  }

  function hideWarningModal() {
    warningModal.classList.remove('active');
    pendingTaskData = null;
  }

  // Warning Modal Actions
  btnReconsider.addEventListener('click', async () => {
    if (!pendingTaskData) return;
    await API.createTodo({ ...pendingTaskData, user_action: 'reconsider' });
    hideWarningModal();
    taskInput.value = '';
    triggerLiveEvaluation();
    refreshAll();
  });

  btnProceedAnyway.addEventListener('click', async () => {
    if (!pendingTaskData) return;
    await API.createTodo({ ...pendingTaskData, user_action: 'proceed' });
    hideWarningModal();
    taskInput.value = '';
    triggerLiveEvaluation();
    refreshAll();
  });

  warningModal.addEventListener('click', (e) => {
    if (e.target === warningModal) {
      hideWarningModal();
    }
  });

  // --- Regret Form Submit ---
  regretForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const desc = regretDesc.value.trim();
    if (!desc) return;

    await API.addRegret({
      description: desc,
      tag: regretTag.value,
      time_of_day: regretTime.value,
      hour_of_day: parseInt(regretHour.value) || 1,
      intensity: parseInt(regretIntensity.value) || 3,
      context: regretContext.value.trim()
    });

    regretDesc.value = '';
    regretContext.value = '';
    triggerLiveEvaluation();
    refreshAll();
  });

  // --- Filters ---
  document.querySelectorAll('.todo-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.todo-filter').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTodoFilter = btn.dataset.status;
      loadTodos();
    });
  });

  if (regretSearch) regretSearch.addEventListener('input', () => loadRegrets());
  if (regretFilterTag) regretFilterTag.addEventListener('change', () => loadRegrets());

  // --- Demo & Reset Handlers ---
  btnSeed.addEventListener('click', async () => {
    btnSeed.disabled = true;
    btnSeed.textContent = "Loading...";
    await API.seedData();
    btnSeed.disabled = false;
    btnSeed.textContent = "✨ Demo";
    refreshAll();
  });

  btnReset.addEventListener('click', async () => {
    if (confirm("Reset database and clear all records?")) {
      await API.resetData();
      refreshAll();
    }
  });

  // --- Academic Modal Handlers ---
  function openAcademicModal(e) {
    if (e) e.preventDefault();
    if (academicModal) academicModal.classList.add('active');
  }

  function closeAcademicModal() {
    if (academicModal) academicModal.classList.remove('active');
  }

  if (btnAcademicInfo) btnAcademicInfo.addEventListener('click', openAcademicModal);
  if (linkAcademic) linkAcademic.addEventListener('click', openAcademicModal);
  if (btnCloseAcademic) btnCloseAcademic.addEventListener('click', closeAcademicModal);
  if (academicModal) {
    academicModal.addEventListener('click', (e) => {
      if (e.target === academicModal) closeAcademicModal();
    });
  }

  // --- Data Loading & Rendering ---
  async function loadStats() {
    try {
      const stats = await API.getStats();
      if (statPrevented) statPrevented.textContent = stats.prevented_todos;
      if (statWarnings) statWarnings.textContent = stats.warnings_count;
      if (statRegrets) statRegrets.textContent = stats.total_regrets;
      if (statActive) statActive.textContent = stats.active_todos;
      if (statTopTag) statTopTag.textContent = stats.top_regret_tag || 'None';
    } catch (err) {
      console.error("Error loading stats:", err);
    }
  }

  async function loadTodos() {
    try {
      const todos = await API.getTodos(currentTodoFilter);
      todoList.innerHTML = '';

      if (todos.length === 0) {
        todoList.innerHTML = `<div style="text-align: center; padding: 28px; color: var(--text-muted); font-size: 13px;">No decisions in this list yet.</div>`;
        return;
      }

      todos.forEach(t => {
        const card = document.createElement('div');
        card.className = `item-card ${t.status === 'Prevented' ? 'prevented-card' : ''} ${t.warning_triggered ? 'warned-card' : ''}`;

        const tagClass = `badge-${(t.tag || 'general').toLowerCase()}`;
        const statusBadgeClass = `badge-${t.status.toLowerCase()}`;

        card.innerHTML = `
          <div class="item-main">
            <div class="item-title">${escapeHtml(t.task)}</div>
            <div class="item-badges">
              <span class="badge ${tagClass}">${escapeHtml(t.tag)}</span>
              <span class="badge" style="background: rgba(241, 245, 249, 0.9);">🕒 ${escapeHtml(t.planned_time)} (${t.planned_hour}:00)</span>
              <span class="badge ${statusBadgeClass}">${t.status}</span>
              ${t.warning_triggered ? '<span class="badge" style="background: var(--amber-bg); color: var(--amber);">⚠️ Warning Fired</span>' : ''}
            </div>
          </div>
          <div class="item-actions">
            ${t.status === 'Pending' ? `
              <button class="btn-icon check" title="Mark Completed" onclick="window.markTodoComplete(${t.id})">✓</button>
            ` : ''}
            <button class="btn-icon delete" title="Delete" onclick="window.deleteTodoItem(${t.id})">✕</button>
          </div>
        `;
        todoList.appendChild(card);
      });
    } catch (err) {
      console.error("Error loading todos:", err);
    }
  }

  async function loadRegrets() {
    try {
      const tag = regretFilterTag ? regretFilterTag.value : 'All';
      const search = regretSearch ? regretSearch.value.trim() : '';
      const regrets = await API.getRegrets(tag, search);
      regretList.innerHTML = '';

      if (regrets.length === 0) {
        regretList.innerHTML = `<div style="text-align: center; padding: 28px; color: var(--text-muted); font-size: 13px;">No regret records found.</div>`;
        return;
      }

      regrets.forEach(r => {
        const card = document.createElement('div');
        card.className = 'item-card';

        const tagClass = `badge-${(r.tag || 'general').toLowerCase()}`;
        const dots = Array.from({ length: 5 }, (_, i) => 
          `<span class="intensity-dot ${i < (r.intensity || 3) ? 'active' : ''}"></span>`
        ).join('');

        card.innerHTML = `
          <div class="item-main">
            <div class="item-title">"${escapeHtml(r.description)}"</div>
            <div class="item-badges">
              <span class="badge ${tagClass}">${escapeHtml(r.tag)}</span>
              <span class="badge" style="background: rgba(241, 245, 249, 0.9);">🕒 ${escapeHtml(r.time_of_day)} (${r.hour_of_day}:00)</span>
              <span class="badge" style="display: inline-flex; align-items: center;">
                Intensity: <span class="intensity-meter">${dots}</span>
              </span>
            </div>
            ${r.context ? `<div class="regret-context">${escapeHtml(r.context)}</div>` : ''}
          </div>
          <div class="item-actions">
            <button class="btn-icon delete" title="Delete Record" onclick="window.deleteRegretItem(${r.id})">✕</button>
          </div>
        `;
        regretList.appendChild(card);
      });
    } catch (err) {
      console.error("Error loading regrets:", err);
    }
  }

  async function loadPatterns() {
    try {
      const patterns = await API.getPatterns();
      patternsGrid.innerHTML = '';

      if (patterns.length === 0) {
        patternsGrid.innerHTML = `
          <div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 13px;">
            No patterns detected yet. Log 2 or more regrets with similar timing and tags to uncover behavioral loops.
          </div>
        `;
        return;
      }

      patterns.forEach(p => {
        const card = document.createElement('div');
        card.className = 'pattern-card';
        card.innerHTML = `
          <div class="pattern-title">${escapeHtml(p.title)}</div>
          <div class="pattern-meta">${escapeHtml(p.context_summary)} • ${p.frequency} recorded occurrences</div>
          <p class="pattern-desc">${escapeHtml(p.explanation)}</p>
        `;
        patternsGrid.appendChild(card);
      });
    } catch (err) {
      console.error("Error loading patterns:", err);
    }
  }

  function refreshAll() {
    loadStats();
    loadTodos();
    loadRegrets();
    loadPatterns();
  }

  // Global window functions for inline onclick handlers
  window.markTodoComplete = async (id) => {
    await API.updateTodo(id, 'Completed');
    refreshAll();
  };

  window.deleteTodoItem = async (id) => {
    await API.deleteTodo(id);
    refreshAll();
  };

  window.deleteRegretItem = async (id) => {
    await API.deleteRegret(id);
    refreshAll();
  };

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
  }

  // Initial load
  refreshAll();
});
