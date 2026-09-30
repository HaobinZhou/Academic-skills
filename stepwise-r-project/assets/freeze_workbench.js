(() => {
  const root = document.getElementById("sw-freeze-v2");
  const names = { goal: "研究目标", data: "数据与人群", time: "时间与策略", outcome: "结局与偏倚", analysis: "统计与解释", delivery: "复现与交付" };
  const colors = ["#7464ef", "#20b9d1", "#f39b35", "#ee638e", "#48bb82", "#5888ec"];
  const state = { snapshot: { round: 0, questions: [] }, selected: null, group: "all", search: "", csrf: "", exampleScale: 1.5, busy: false };
  const drafts = {}, messageDrafts = {}, draftBases = {}, draftRequests = {};
  let storageKey, storageOK = true, loadedDrafts = false, noticeTimer, returnFocus;
  let exampleView = { id: null, key: null, html: null, generation: 0 };
  const escape = value => String(value ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const questions = () => state.snapshot.questions;
  const byId = id => questions().find(q => q.id === id);
  const selected = () => byId(state.selected);
  const groupName = key => names[key] || key;
  const groups = () => [...new Set(questions().map(q => groupName(q.group)))];
  const groupColor = key => colors[Math.max(0, groups().indexOf(groupName(key))) % colors.length];
  const label = status => status === "answered" ? "已回答" : status === "discussing" ? "讨论中" : "待填写";
  const pill = status => '<span class="sw2-pill sw2-pill-' + (status === "discussing" ? "talk" : status) + '">' + label(status) + "</span>";
  const actorKind = actor => ["user", "codex", "chatgpt"].includes(actor) ? actor : "unknown";
  const actorLabel = actor => ({ user: "你", codex: "Codex", chatgpt: "ChatGPT", web_ai: "网页 AI（历史来源）" })[actor] || "AI（来源未记录）";
  const actorBadge = actor => '<span class="sw2-actor sw2-actor-' + actorKind(actor) + '">' + actorLabel(actor) + "</span>";
  const requestId = () => crypto.randomUUID ? crypto.randomUUID() : Date.now() + "-" + Math.random();
  const visible = () => groups().flatMap(group => questions().filter(q => groupName(q.group) === group &&
    (state.group === "all" || group === state.group) &&
    (!state.search || (q.id + " " + q.title + " " + q.why).toLocaleLowerCase().includes(state.search.toLocaleLowerCase()))));
  const pending = () => questions().filter(q => Object.hasOwn(drafts, q.id) || Boolean(messageDrafts[q.id]?.trim()));
  const conflict = q => Object.hasOwn(drafts, q.id) && draftBases[q.id] && draftBases[q.id].answer !== q.user_answer;
  const overlay = () => root.querySelector("#sw2-overlay");

  function persistDrafts() {
    if (!storageKey) return;
    try {
      sessionStorage.setItem(storageKey, JSON.stringify({ answers: drafts, messages: messageDrafts, bases: draftBases, requests: draftRequests, selected: state.selected }));
      storageOK = true;
    } catch (_) { storageOK = false; }
  }

  function restoreDrafts() {
    storageKey = "stepwise-freeze:drafts:v1:" + state.snapshot.project;
    if (loadedDrafts) return;
    loadedDrafts = true;
    try {
      const saved = JSON.parse(sessionStorage.getItem(storageKey) || "{}");
      for (const q of questions()) {
        if (typeof saved.answers?.[q.id] === "string" && saved.answers[q.id] !== q.user_answer) {
          drafts[q.id] = saved.answers[q.id];
          const base = saved.bases?.[q.id];
          draftBases[q.id] = base && (typeof base.answer === "string" || base.answer === null) ? base : { answer: q.user_answer, revision: q.revision };
        }
        if (typeof saved.messages?.[q.id] === "string" && saved.messages[q.id].trim()) messageDrafts[q.id] = saved.messages[q.id];
        for (const kind of ["answer", "comment"]) {
          const key = q.id + ":" + kind;
          if (typeof saved.requests?.[key] === "string") draftRequests[key] = saved.requests[key];
        }
      }
      if (byId(saved.selected)) state.selected = saved.selected;
    } catch (_) { storageOK = false; }
  }

  function answerDraft(id, value) {
    const q = byId(id);
    if (!q) return;
    if (value === q.user_answer) {
      delete drafts[id]; delete draftBases[id]; delete draftRequests[id + ":answer"];
    } else {
      if (!Object.hasOwn(drafts, id)) draftBases[id] = { answer: q.user_answer, revision: q.revision };
      if (drafts[id] !== value) draftRequests[id + ":answer"] = requestId();
      drafts[id] = value;
    }
    persistDrafts(); updateDraftUI();
  }

  function messageDraft(id, value) {
    if (messageDrafts[id] !== value) draftRequests[id + ":comment"] = requestId();
    if (value.trim()) messageDrafts[id] = value;
    else { delete messageDrafts[id]; delete draftRequests[id + ":comment"]; }
    persistDrafts(); updateDraftUI();
  }

  function updateDraftUI() {
    const count = pending().length;
    const badge = root.querySelector("#sw2-draft-count");
    badge.textContent = count; badge.hidden = !count;
    root.querySelector("#sw2-save-all").disabled = state.busy || !count;
    root.querySelector("#sw2-draft-label").textContent = count
      ? count + " 题未保存 · " + (storageOK ? "草稿已在本窗口暂存" : "浏览器暂存失败，请保存")
      : "无未保存修改";
    for (const button of root.querySelectorAll("[data-action=select]")) {
      const tag = button.querySelector(".sw2-draft-tag");
      if (tag) tag.hidden = !pending().some(q => q.id === button.dataset.id);
    }
    const q = selected();
    const hint = root.querySelector("#sw2-answer-hint");
    if (hint && q) hint.textContent = Object.hasOwn(drafts, q.id) ? "答复未保存" : "答复" + (q.user_answer ? "已保存" : "待填写");
    const messageHint = root.querySelector("#sw2-message-hint");
    if (messageHint && q) messageHint.textContent = messageDrafts[q.id]?.trim() ? "留言未保存" : "";
  }

  function showNotice(message, kind = "success", target = "") {
    const notice = root.querySelector("#sw2-notice");
    notice.textContent = message; notice.dataset.kind = kind;
    notice.setAttribute("role", kind === "error" ? "alert" : "status");
    notice.setAttribute("aria-live", kind === "error" ? "assertive" : "polite");
    notice.hidden = false;
    const footer = root.querySelector("#sw2-save-label");
    footer.textContent = message; footer.dataset.kind = kind;
    const nearby = target && root.querySelector("#sw2-" + target + "-status");
    if (nearby) { nearby.textContent = message; nearby.dataset.kind = kind; nearby.hidden = false; }
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => { notice.hidden = true; }, 6000);
  }

  function friendlyError(error) {
    const message = error.message || String(error);
    if (error.network || /Failed to fetch|NetworkError|Load failed/i.test(message)) {
      return "工作台连接中断，内容尚未确认保存。恢复服务或转发连接后，点击“刷新项目记录”，再重试保存。未保存输入仍在本窗口。";
    }
    if (message.includes("changed since read")) return "这题已被其他窗口更新。点击“刷新项目记录”后比较答复，再重试；本地草稿会保留。";
    if (message.includes("Login required")) return "登录已失效，请重新打开工作台登录链接；本窗口草稿会保留。";
    if (message.includes("CSRF check failed")) return "页面会话已失效。点击“刷新项目记录”后再保存；本窗口草稿会保留。";
    if (error.status >= 500) return "工作台服务暂时无法完成操作。恢复服务后点击“刷新项目记录”，再重试；本地草稿会保留。";
    return message;
  }

  async function api(path, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      let response;
      try {
        response = await fetch(path, body === undefined ? { credentials: "same-origin", cache: "no-store", signal: controller.signal } : {
          method: "POST", credentials: "same-origin", cache: "no-store", signal: controller.signal,
          headers: { "Content-Type": "application/json", "X-Freeze-CSRF": state.csrf }, body: JSON.stringify(body),
        });
      } catch (cause) { const error = new Error(cause.message); error.network = true; throw error; }
      let data;
      try { data = await response.json(); } catch (_) { const error = new Error("响应内容无法读取，请刷新项目记录后重试。"); error.status = response.status; throw error; }
      if (!response.ok) { const error = new Error(data.error || "HTTP " + response.status); error.status = response.status; throw error; }
      return data;
    } finally { clearTimeout(timer); }
  }

  async function refresh() {
    const data = await api("/api/snapshot");
    state.snapshot = data.snapshot; state.csrf = data.csrf;
    restoreDrafts();
    for (const q of questions()) {
      if (Object.hasOwn(drafts, q.id) && drafts[q.id] === q.user_answer) {
        delete drafts[q.id]; delete draftBases[q.id]; delete draftRequests[q.id + ":answer"];
      }
    }
    if (!visible().some(q => q.id === state.selected)) state.selected = visible().find(q => q.example)?.id || visible()[0]?.id || null;
    persistDrafts(); render({ refreshExample: true });
  }

  function renderGroups() {
    const buttons = [["all", "全部问题", "#7464ef", questions().length], ...groups().map(key => [key, key, groupColor(key), questions().filter(q => groupName(q.group) === key).length])];
    root.querySelector("#sw2-group-list").innerHTML = buttons.map(([key, name, color, count]) =>
      '<button type="button" class="sw2-group" data-action="group" data-group="' + escape(key) + '" aria-current="' + (state.group === key) + '"><span class="sw2-dot" style="--group-color:' + color + '"></span><span class="sw2-group-name">' + escape(name) + "</span><small>" + count + "</small></button>").join("");
  }

  function renderList() {
    const items = visible();
    root.querySelector("#sw2-list-heading").textContent = state.group === "all" ? "全部问题" : state.group;
    root.querySelector("#sw2-visible").textContent = items.length + " 项";
    let previous = "";
    root.querySelector("#sw2-question-list").innerHTML = items.map(q => {
      const heading = groupName(q.group) !== previous ? '<div class="sw2-list-group-title"><span class="sw2-dot" style="--group-color:' + groupColor(q.group) + '"></span>' + escape(groupName(q.group)) + "</div>" : "";
      previous = groupName(q.group);
      return heading + '<button type="button" class="sw2-question" data-action="select" data-id="' + q.id + '" aria-current="' + (state.selected === q.id) + '"><span class="sw2-question-top"><span class="sw2-question-id">' + q.id + " · 第 " + q.round + " 轮</span>" + pill(q.status) + '</span><span class="sw2-question-name">' + escape(q.title) + '</span><span class="sw2-draft-tag" hidden>未保存</span></button>';
    }).join("") || '<div class="sw2-empty">' + (questions().length ? '没有匹配的问题。<button class="sw2-button sw2-button-outline" data-action="clear-filter">清除筛选</button>' : "暂无问题") + "</div>";
  }

  function renderDetail() {
    const q = selected(), panel = root.querySelector("#sw2-detail");
    if (panel.dataset.question !== (q?.id || "")) panel.scrollTop = 0;
    panel.dataset.question = q?.id || "";
    if (!q) {
      panel.innerHTML = '<div class="sw2-empty">' + (questions().length ? "没有匹配的问题，请调整搜索或筛选。" : "暂无问题") + "</div>";
      return;
    }
    const thread = q.messages || [];
    const conflictHTML = conflict(q) ? '<section class="sw2-conflict"><strong>项目已有另一份答复</strong><p>' + escape(q.user_answer || "未填写") + '</p><div class="sw2-action-pair"><button class="sw2-button sw2-button-outline" data-action="use-project">使用项目答复</button><button class="sw2-button sw2-button-outline" data-action="keep-draft">保留我的答复</button></div></section>' : "";
    panel.innerHTML = [
      '<div class="sw2-detail-top"><span class="sw2-detail-code">' + q.id + " · " + escape(groupName(q.group)) + " · 第 " + q.round + " 轮</span>" + pill(q.status) + '<span class="sw2-origin">提出 ' + actorBadge(q.created_by) + "</span></div>",
      "<h2>" + escape(q.title) + "</h2>",
      '<div class="sw2-evidence"><div class="sw2-context"><strong>为何需要冻结</strong>' + escape(q.why) + '</div><div class="sw2-source"><strong>识别依据 / 文件</strong>' + escape(q.source_summary) + "</div></div>",
      '<div class="sw2-section-title">当前意见' + actorBadge(q.ai_position_by) + '</div><div class="sw2-ai-note sw2-ai-note-' + actorKind(q.ai_position_by) + '">' + escape(q.ai_position || "暂无意见") + "</div>",
      '<div class="sw2-suggestions">' + (q.suggestions || []).map(value => '<button class="sw2-suggestion" type="button" data-action="suggest" data-value="' + escape(value) + '">' + escape(value) + "</button>").join("") + "</div>",
      conflictHTML,
      '<label class="sw2-section-title" for="sw2-answer">口径答复</label><textarea id="sw2-answer" class="sw2-answer" placeholder="填写答复…">' + escape(drafts[q.id] ?? q.user_answer ?? "") + "</textarea>",
      '<div class="sw2-answer-actions"><span id="sw2-answer-hint"></span><div class="sw2-action-pair">',
      q.status === "discussing" ? (q.user_answer ? '<button type="button" class="sw2-button sw2-button-outline" data-action="resolve">确认分歧已解决</button>' : "") : '<button type="button" class="sw2-button sw2-button-outline" data-action="mark-talk">保留分歧</button>',
      '<button type="button" class="sw2-button sw2-button-purple" data-action="save-answer">保存答复</button></div></div><div id="sw2-answer-status" class="sw2-action-status" role="status" aria-live="polite" hidden></div>',
      '<div class="sw2-section-title">讨论<small>' + thread.length + ' 条记录</small></div><div class="sw2-thread" aria-label="' + escape(q.title) + '的讨论记录">',
      thread.length ? thread.map(message => '<div class="sw2-bubble sw2-bubble-' + actorKind(message.actor) + '"><div class="sw2-bubble-head">' + actorBadge(message.actor) + "<span>第 " + message.round + " 轮 · " + escape(message.at || "") + "</span></div>" + escape(message.text) + "</div>").join("") : '<div class="sw2-empty">暂无讨论</div>',
      '</div><label class="sw2-sr-only" for="sw2-message">讨论留言</label><textarea id="sw2-message" class="sw2-message-input" placeholder="写下讨论…">' + escape(messageDrafts[q.id] || "") + "</textarea>",
      '<div class="sw2-message-actions"><span id="sw2-message-hint"></span><button type="button" class="sw2-button sw2-button-coral" data-action="post">保存讨论留言</button></div><div id="sw2-message-status" class="sw2-action-status" role="status" aria-live="polite" hidden></div>',
    ].join("");
  }

  async function renderExample(force = false) {
    const q = selected(), panel = root.querySelector("#sw2-example");
    if (!q) { exampleView = { id: null, key: null, html: null, generation: exampleView.generation + 1 }; panel.innerHTML = ""; return; }
    const example = q.example, key = JSON.stringify(example);
    const rebuild = exampleView.id !== q.id || exampleView.key !== key;
    if (!rebuild && !force) return;
    if (rebuild) {
      if (exampleView.id !== q.id) panel.scrollTop = 0;
      exampleView = { id: q.id, key, html: null, generation: exampleView.generation + 1 };
      panel.innerHTML = '<div class="sw2-example-head"><span class="sw2-example-kicker">实例推演' + (example ? " · " + actorBadge(example.updated_by) : "") + "</span>" + (example ? '<label class="sw2-example-scale" for="sw2-example-scale">显示比例<select id="sw2-example-scale" aria-label="实例显示比例">' + [1, 1.25, 1.5, 1.75, 2].map(scale => '<option value="' + scale + '"' + (state.exampleScale === scale ? " selected" : "") + ">" + scale * 100 + "%</option>").join("") + "</select></label>" : "") + "</div><h2>" + escape(example ? example.title : "暂无实例") + "</h2>" +
        (example ? "<p>" + escape(example.summary) + '</p><div class="sw2-example-viewport" style="--example-scale:' + state.exampleScale + '"><iframe sandbox="" referrerpolicy="no-referrer" title="' + escape(q.title) + '的 HTML 示例"></iframe></div><details><summary>HTML 源码</summary><pre id="sw2-example-code"></pre></details>' : "") +
        '<button type="button" class="sw2-button sw2-button-outline" data-action="request-example">' + (example ? "请求修改实例" : "请求实例") + '</button><div id="sw2-example-status" class="sw2-action-status" role="status" aria-live="polite" hidden></div>';
      applyBusy();
    }
    if (!example) return;
    const generation = ++exampleView.generation;
    try {
      const data = await api("/api/questions/" + q.id + "/example");
      if (exampleView.generation !== generation || state.selected !== q.id) return;
      const html = data.html || "";
      panel.querySelector("#sw2-example-code").textContent = html;
      if (html !== exampleView.html) {
        exampleView.html = html;
        panel.querySelector("iframe").srcdoc = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">' + html;
      }
    } catch (error) {
      if (exampleView.generation === generation && state.selected === q.id) showNotice("实例读取失败：" + friendlyError(error), "error", "example");
    }
  }

  function applyBusy() {
    root.setAttribute("aria-busy", String(state.busy));
    for (const button of root.querySelectorAll("button")) button.disabled = state.busy;
    for (const field of root.querySelectorAll("#sw2-answer, #sw2-message")) field.readOnly = state.busy;
    const scale = root.querySelector("#sw2-example-scale");
    if (scale) scale.disabled = state.busy;
    updateDraftUI();
  }

  function render({ refreshExample = false } = {}) {
    const all = questions();
    root.querySelector("#sw2-round").textContent = state.snapshot.round || "—";
    root.querySelector("#sw2-total").textContent = all.length;
    root.querySelector("#sw2-open").textContent = all.filter(q => q.status === "open").length;
    root.querySelector("#sw2-talk").textContent = all.filter(q => q.status === "discussing").length;
    root.querySelector("#sw2-answered").textContent = all.filter(q => q.status === "answered").length;
    root.querySelector("#sw2-search").value = state.search;
    renderGroups(); renderList(); renderDetail(); renderExample(refreshExample); applyBusy();
  }

  async function change(id, operation, value, stableRequest) {
    const q = byId(id);
    if (!q) throw new Error("问题已不存在：" + id);
    const data = await api("/api/questions/" + id + "/change", { operation, value, expected_revision: q.revision, request_id: stableRequest || requestId() });
    const index = questions().findIndex(item => item.id === id);
    if (index >= 0) state.snapshot.questions[index] = data.question;
    return data.question;
  }

  async function saveAnswer(id) {
    const q = byId(id), value = (drafts[id] ?? q.user_answer ?? "").trim();
    if (!value) throw new Error(id + "：请先填写口径。");
    if (conflict(q)) throw new Error(id + "：项目答复已改变，请先在该题比较并选择保留哪份答复。");
    const request = draftRequests[id + ":answer"] ||= requestId();
    await change(id, "answer", value, request);
    delete drafts[id]; delete draftBases[id]; delete draftRequests[id + ":answer"]; persistDrafts();
  }

  async function saveMessage(id) {
    const value = (messageDrafts[id] || "").trim();
    if (!value) throw new Error(id + "：请先填写讨论内容。");
    const request = draftRequests[id + ":comment"] ||= requestId();
    await change(id, "comment", value, request);
    delete messageDrafts[id]; delete draftRequests[id + ":comment"]; persistDrafts();
  }

  async function saveAll() {
    const ids = pending().map(q => q.id), failures = [];
    let saved = 0;
    for (const id of ids) {
      try {
        if (Object.hasOwn(drafts, id)) await saveAnswer(id);
        if (messageDrafts[id]?.trim()) await saveMessage(id);
        saved++;
      } catch (error) { const message = friendlyError(error); failures.push(message.startsWith(id + "：") ? message : id + "：" + message); }
    }
    render();
    if (failures.length) throw new Error("已保存 " + saved + " 题；" + failures.length + " 题未全部保存，草稿保留。\n" + failures.join("\n"));
    return saved;
  }

  function handoffText(excluded = []) {
    const all = questions();
    const lines = ["请复核第 " + state.snapshot.round + " 轮已保存的口径记录。项目路径：" + state.snapshot.project + "。请读取 Freeze/manifest.json 和各问题记录，以项目文件为准。",
      "当前问题 " + all.length + " 项：已回答 " + all.filter(q => q.status === "answered").length + "，讨论中 " + all.filter(q => q.status === "discussing").length + "，待填写 " + all.filter(q => q.status === "open").length + "。"];
    if (excluded.length) lines.push("我选择仅交接已保存内容。以下题目的本地未保存草稿未提交：" + excluded.join("、") + "。");
    lines.push("", "全部问题、答复与讨论：");
    for (const q of all) {
      lines.push("", q.id + " " + q.title + " [" + label(q.status) + "]", "提出：" + actorLabel(q.created_by), "答复：" + (q.user_answer || "未填写"));
      if (q.ai_position) lines.push("当前意见（" + actorLabel(q.ai_position_by) + "）：" + q.ai_position);
      for (const m of q.messages || []) lines.push("讨论（" + actorLabel(m.actor) + "，第 " + m.round + " 轮）：" + m.text);
      if (q.example) lines.push("实例（" + actorLabel(q.example.updated_by) + "）：" + q.example.title);
    }
    lines.push("", "请先核对全部答复与分歧，再一次性补充当前可识别的全部新问题。未经我的确认，不要把讨论草稿视为已冻结口径。正式冻结需更新 Canonical 并验证。");
    return lines.join("\n");
  }

  function renderHandoff(exclude = false) {
    const items = pending();
    const waiting = items.length > 0 && !exclude;
    root.querySelector("#sw2-handoff-pending").hidden = !waiting;
    root.querySelector("#sw2-handoff-pending").innerHTML = waiting ? "<strong>" + items.length + " 题尚未保存</strong><ul>" + items.map(q => "<li>" + q.id + " · " + escape(q.title) + "（" + [Object.hasOwn(drafts, q.id) ? "答复" : "", messageDrafts[q.id]?.trim() ? "留言" : ""].filter(Boolean).join("、") + "）</li>").join("") + "</ul>" : "";
    const area = root.querySelector("#sw2-handoff-text");
    area.hidden = waiting; area.value = waiting ? "" : handoffText(exclude ? items.map(q => q.id) : []);
    root.querySelector("[data-action=handoff-save]").hidden = !waiting;
    root.querySelector("[data-action=handoff-saved]").hidden = !waiting;
    root.querySelector("[data-action=copy]").hidden = waiting;
    root.querySelector("#sw2-copy-status").textContent = waiting ? "" : exclude && items.length ? "已排除 " + items.length + " 题未保存草稿" : "项目已保存内容";
    root.querySelector("#sw2-handoff-status").hidden = true;
  }

  function openHandoff(button) {
    returnFocus = button; renderHandoff(); overlay().hidden = false;
    for (const element of root.querySelectorAll(".sw2-app > header, .sw2-app > nav, .sw2-workspace, .sw2-footer")) element.inert = true;
    root.querySelector("[data-action=close]").focus();
  }

  function closeHandoff() {
    if (state.busy) return;
    overlay().hidden = true;
    for (const element of root.querySelectorAll("[inert]")) element.inert = false;
    if (returnFocus?.isConnected) returnFocus.focus();
  }

  root.addEventListener("click", async event => {
    const button = event.target.closest("[data-action]");
    if (!button || !root.contains(button) || state.busy) return;
    const action = button.dataset.action;
    if (action === "group" || action === "clear-filter") {
      state.group = action === "group" ? button.dataset.group : "all";
      if (action === "clear-filter") state.search = "";
      state.selected = visible()[0]?.id || null; persistDrafts(); render(); return;
    }
    if (action === "select") { state.selected = button.dataset.id; persistDrafts(); renderList(); renderDetail(); renderExample(); updateDraftUI(); return; }
    if (action === "suggest") {
      const area = root.querySelector("#sw2-answer"); area.value = button.dataset.value;
      answerDraft(state.selected, area.value); area.focus(); showNotice("选项已填入，尚未保存。", "info", "answer"); return;
    }
    if (action === "use-project" || action === "keep-draft") {
      const q = selected();
      if (action === "use-project") { delete drafts[q.id]; delete draftBases[q.id]; delete draftRequests[q.id + ":answer"]; }
      else draftBases[q.id] = { answer: q.user_answer, revision: q.revision };
      persistDrafts(); renderDetail(); updateDraftUI(); showNotice(action === "use-project" ? "已使用项目答复。" : "已保留本地答复，点击保存后写入项目。", "info", "answer"); return;
    }
    if (action === "handoff") { openHandoff(button); return; }
    if (action === "close") { closeHandoff(); return; }
    if (action === "handoff-saved") { renderHandoff(true); root.querySelector("#sw2-handoff-text").focus(); return; }
    if (action === "copy") {
      const area = root.querySelector("#sw2-handoff-text");
      try { await navigator.clipboard.writeText(area.value); root.querySelector("#sw2-copy-status").textContent = "已复制"; showNotice("交接摘要已复制。"); }
      catch (_) { area.focus(); area.select(); root.querySelector("#sw2-copy-status").textContent = "已选中，请手动复制"; showNotice("自动复制未成功，摘要已选中。", "info"); }
      return;
    }
    state.busy = true; applyBusy();
    const originalLabel = button.textContent;
    if (action !== "save-all") button.textContent = action === "refresh" ? "刷新中…" : "保存中…";
    try {
      const id = state.selected;
      if (action === "refresh") { await refresh(); showNotice("项目记录已刷新 · 第 " + state.snapshot.round + " 轮 · " + questions().length + " 题"); }
      else if (action === "save-all" || action === "handoff-save") {
        const saved = await saveAll();
        if (action === "handoff-save") { renderHandoff(); root.querySelector("#sw2-handoff-text").focus(); }
        showNotice("已保存 " + saved + " 题，全部修改已写入项目。", "success", action === "handoff-save" ? "handoff" : "");
      } else if (action === "save-answer") {
        await saveAnswer(id); render(); showNotice(id + " 答复已保存 · " + label(byId(id).status), "success", "answer");
      } else if (action === "post") {
        await saveMessage(id); render(); showNotice(id + " 讨论已保存 · 讨论中", "success", "message");
      } else if (action === "mark-talk") {
        await change(id, "discuss", null); render(); showNotice(id + " 已保留分歧 · 讨论中", "success", "answer");
      } else if (action === "resolve") {
        if (Object.hasOwn(drafts, id) || messageDrafts[id]?.trim()) throw new Error("请先保存这题的答复和留言，再确认分歧已解决。");
        await change(id, "resolve", null); render(); showNotice(id + " 分歧已解决 · 已回答", "success", "answer");
      } else if (action === "request-example") {
        await change(id, "comment", "请补充或修订具体实例；若简短文字难以说明，请提供可视化 HTML，展示各选择的实际影响。");
        render(); showNotice(id + " 实例请求已保存到讨论。", "success", "example");
      }
    } catch (error) {
      if (action === "handoff-save") renderHandoff();
      const target = ["mark-talk", "resolve", "save-answer"].includes(action) ? "answer" : action === "post" ? "message" : action === "request-example" ? "example" : action === "handoff-save" ? "handoff" : "";
      showNotice("操作未完成：" + friendlyError(error), "error", target);
    } finally {
      if (action !== "save-all") button.textContent = originalLabel;
      state.busy = false; applyBusy();
      if (!overlay().hidden) root.querySelector(action === "handoff-save" && !pending().length ? "#sw2-handoff-text" : "[data-action=close]").focus();
    }
  });

  root.addEventListener("change", event => {
    if (event.target.id !== "sw2-example-scale") return;
    const scale = Number(event.target.value);
    if (![1, 1.25, 1.5, 1.75, 2].includes(scale)) return;
    state.exampleScale = scale;
    root.querySelector(".sw2-example-viewport")?.style.setProperty("--example-scale", scale);
  });

  root.querySelector("#sw2-search").addEventListener("input", event => {
    state.search = event.target.value;
    if (!visible().some(q => q.id === state.selected)) state.selected = visible()[0]?.id || null;
    persistDrafts(); renderList(); renderDetail(); renderExample(); updateDraftUI();
  });
  root.addEventListener("input", event => {
    if (event.target.id === "sw2-answer") { answerDraft(state.selected, event.target.value); root.querySelector("#sw2-answer-status").hidden = true; }
    if (event.target.id === "sw2-message") { messageDraft(state.selected, event.target.value); root.querySelector("#sw2-message-status").hidden = true; }
  });
  document.addEventListener("keydown", event => {
    if (overlay().hidden) return;
    if (event.key === "Escape") { event.preventDefault(); closeHandoff(); return; }
    if (event.key !== "Tab") return;
    const dialog = root.querySelector(".sw2-dialog");
    const focusable = [...dialog.querySelectorAll("button, textarea, [tabindex]")].filter(e => !e.disabled && !e.hidden && e.getClientRects().length && e.tabIndex >= 0);
    const first = focusable[0], last = focusable.at(-1);
    if (!first) { event.preventDefault(); dialog.focus(); return; }
    if (!dialog.contains(document.activeElement) || (event.shiftKey && document.activeElement === first) || (!event.shiftKey && document.activeElement === last)) {
      event.preventDefault(); (event.shiftKey ? last : first).focus();
    }
  });
  window.addEventListener("beforeunload", event => {
    persistDrafts();
    if (pending().length) { event.preventDefault(); event.returnValue = ""; }
  });
  refresh().then(() => {
    if (pending().length) showNotice("已恢复 " + pending().length + " 题未保存草稿。", "info");
    else root.querySelector("#sw2-save-label").textContent = "项目记录已同步";
  }).catch(error => showNotice("读取失败：" + friendlyError(error), "error"));
})();
