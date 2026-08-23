(() => {
  const PAGES = [
    { id: "overview", title: "Overview", sub: "Research · Create · Optimize · Scale" },
    { id: "discovery", title: "Discovery", sub: "Cross-platform opportunity intelligence" },
    { id: "knowledge", title: "Knowledge Graph", sub: "Living memory of what works" },
    { id: "campaigns", title: "Campaigns", sub: "Launch autonomous media campaigns" },
    { id: "orchestra", title: "Agent Orchestra", sub: "Live organization · event stream" },
    { id: "debugger", title: "AI Debugger", sub: "Replayable inferences · cost · latency" },
    { id: "studio", title: "Studio", sub: "Compose scenes, hooks, and cuts" },
    { id: "evolution", title: "Evolution Lab", sub: "Crown winners. Retire losers." },
    { id: "analytics", title: "Analytics", sub: "Retention, RPM, and forecast" },
    { id: "memory", title: "Memory", sub: "Causal lessons from every publish" },
    { id: "command", title: "Command Center", sub: "Runtime, keys, and gateway health" },
    { id: "publishing", title: "Publishing", sub: "Queue across YouTube, TikTok, Reels" },
    { id: "uploads", title: "Uploads", sub: "Source footage, stills, and brand kits" },
    { id: "settings", title: "Settings", sub: "Studio identity and OpenAI-compatible /v1" },
  ];

  const main = document.getElementById("main");
  const titleEl = document.getElementById("page-title");
  const subEl = document.getElementById("page-sub");
  const splash = document.getElementById("splash");
  const app = document.getElementById("app");
  const outro = document.getElementById("outro");
  const palette = document.getElementById("palette");
  const cmdInput = document.getElementById("cmd-input");
  const cmdList = document.getElementById("cmd-list");
  const sidebar = document.getElementById("sidebar");
  let loopStep = "Improve";
  let launchMsg = "";
  let probeMsg = "No inferences yet — run a probe or campaign.";
  let inferences = 0;

  const topics = [
    { name: "Automation", competition: 0.5, velocity: 0.82, viral: 0.7, conf: 0.82 },
    { name: "Claude", competition: 0.61, velocity: 0.88, viral: 0.74, conf: 0.9 },
    { name: "UGC Product", competition: 0.42, velocity: 0.76, viral: 0.69, conf: 0.81 },
    { name: "Everyday Carry", competition: 0.38, velocity: 0.71, viral: 0.66, conf: 0.78 },
  ];
  const activity = [
    ["Research Agent", "Found 6 high-velocity AI education topics", "now"],
    ["Evolution Lab", "Experiment #129 crowned thumbnail B winner", "2m"],
    ["Publishing Agent", "Queued 4 Shorts — YouTube + TikTok", "8m"],
    ["Analytics Agent", "Retention lift +18% after hook rewrite", "14m"],
    ["Memory", "Learned: money hooks ↑23% CTR", "1h"],
  ];
  const campaigns = [
    ["Everyday Carry", "edc_tech · 7 scenes · 20s"],
    ["Everyday Carry", "edc_tech_best · 7 scenes · 19.94s"],
    ["Hermes OS — Platform Promo", "hermes_os_promo · 4 scenes · 12.6s"],
  ];

  function metric(label, value, hint, accent) {
    return `<article class="card${accent ? " accent" : ""}"><span class="lbl">${label}</span><div class="val${accent ? " green" : ""}">${value}</div><div class="hint">${hint}</div></article>`;
  }

  function views() {
    return {
      overview: `
        <div class="grid metrics">
          ${metric("Revenue", "$12.4k", "30d · +18%", true)}
          ${metric("Views", "2.1M", "Across channels")}
          ${metric("CTR", "6.8%", "+11% vs baseline")}
          ${metric("Retention", "54%", "+18% evolved")}
          ${metric("RPM", "$4.20", "+9%")}
          ${metric("Publishing Queue", "14", "Scheduled")}
          ${metric("AI Confidence", "0.91", "Prediction gate")}
          ${metric("Opportunities", "37", "High velocity")}
          ${metric("Knowledge Nodes", "5", "Living graph")}
          ${metric("Experiments", "242", "Running / scored")}
          ${metric("Agents Online", "15", "Orchestra ready")}
          ${metric("Channel Health", "Strong", "Growth forecast ↑")}
        </div>
        <div class="grid split" style="margin-top:0.75rem">
          <section class="card">
            <h2 class="section-h" style="margin:0 0 0.85rem">AI activity</h2>
            <div class="feed">${activity.map(([who, what, t]) => `<div class="feed-item"><time>${t}</time><strong>${who}</strong><span>${what}</span></div>`).join("")}</div>
          </section>
          <section class="card">
            <h2 class="section-h" style="margin:0 0 0.85rem">Operating loop</h2>
            <div class="loop" role="tablist">${["Discover","Create","Publish","Learn","Improve"].map((s) => `<button type="button" data-loop="${s}" class="${s===loopStep?"on":""}">${s}</button>`).join("")}</div>
            <p class="muted" style="margin:0.9rem 0 0">Every publish updates the knowledge graph and evolution weights for the next campaign.</p>
          </section>
        </div>`,
      discovery: `
        <section class="card">
          <h2>AI opportunity scan</h2>
          <div class="chips">${["YouTube","Reddit","TikTok","Google Trends","X","News","Competitors"].map((c,i)=>`<button type="button" class="chip${i<4?" on":""}">${c}</button>`).join("")}</div>
          <p class="muted">Hermes continuously scans the open web for high-opportunity topics — not a single YouTube search.</p>
        </section>
        <div class="grid metrics" style="margin-top:0.75rem">
          ${metric("Trending", "9", "High velocity")}
          ${metric("Emerging", "4", "Early signal")}
          ${metric("Low Competition", "5", "Whitespace")}
          ${metric("Avg Virality", "0.78", "Predicted", true)}
        </div>
        <section class="card" style="margin-top:0.75rem">
          <h2>High-opportunity topics</h2>
          ${topics.map((t)=>`<div class="row"><div class="min-w"><h3>${t.name}</h3><div class="stats">Competition ${t.competition} · Velocity ${t.velocity}</div></div><div style="display:flex;gap:0.5rem;align-items:center"><span class="stats">Viral ${t.viral.toFixed(2)}</span><span class="pill">Conf ${t.conf.toFixed(2)}</span></div></div>`).join("")}
        </section>`,
      knowledge: `
        <div class="grid metrics-3">
          ${metric("Nodes", "9", "Living graph")}
          ${metric("Relations", "8", "Causal edges")}
          ${metric("Feedback Loops", "Active", "Analytics → Memory", true)}
        </div>
        <section class="card" style="margin-top:0.75rem">
          <h2>Living knowledge graph</h2>
          <div class="flow">${["Topic","Audience","Hooks","Scripts","Videos","Analytics"].map((n)=>`<span>${n}</span><i>→</i>`).join("")}<span class="end">Updated Graph</span></div>
          <p class="muted">Every publish strengthens the graph. Hermes doesn’t store files — it stores causal media intelligence.</p>
        </section>
        <section class="card" style="margin-top:0.75rem">
          <h2>Sample connections</h2>
          <div class="chips">${["AI","Claude","Coding","Automation","Startup","Productivity","Everyday Carry","UGC Product","YouTube Shorts"].map((c)=>`<span class="chip">${c}</span>`).join("")}</div>
        </section>`,
      campaigns: `
        <div class="grid split">
          <section class="card">
            <h2>Campaign builder</h2>
            <form class="form" id="campaign-form">
              <label>Niche <input name="niche" value="AI education" autocomplete="off" /></label>
              <label>Goal <input name="goal" value="Grow subscribers" autocomplete="off" /></label>
              <label>Platforms <input name="platforms" value="YouTube Shorts, TikTok, Reels" autocomplete="off" /></label>
              <label>Budget <input name="budget" value="$2,000 / mo" autocomplete="off" /></label>
              <label>Frequency <input name="freq" value="2 / day" autocomplete="off" /></label>
              <button class="btn primary" type="submit">Launch</button>
              <div class="toast" id="launch-toast" aria-live="polite">${launchMsg}</div>
            </form>
          </section>
          <section class="card">
            <h2>Active campaigns</h2>
            ${campaigns.map(([n,s])=>`<div class="row"><div><h3>${n}</h3><div class="stats">${s}</div></div><button class="btn" type="button" data-render="${n}">Render</button></div>`).join("")}
          </section>
        </div>`,
      orchestra: `
        <div class="grid metrics">
          ${metric("CEO", "Hermes OS Orchestrator", "Orchestrator")}
          ${metric("Agents", "0", "OS + kernel")}
          ${metric("Healthy", "—%", "Runtime health")}
          ${metric("Platform", "—", "Reliability layer")}
        </div>
        <section class="card" style="margin-top:0.75rem"><h2>Organization</h2><p class="empty">Loading organization…</p></section>
        <section class="card" style="margin-top:0.75rem">
          <h2>Live event stream</h2>
          <p class="empty">Waiting for workflow events…</p>
          <div class="actions" style="margin-top:0.8rem">
            <button class="btn primary" type="button" id="dry-run">Run dry-run campaign</button>
            <a class="btn" href="#/debugger">AI Debugger</a>
          </div>
        </section>`,
      debugger: `
        <div class="grid metrics">
          ${metric("Inferences", String(inferences), "Recorded")}
          ${metric("Total Cost", "$0.0000", "USD")}
          ${metric("Avg Latency", inferences ? "42ms" : "0ms", "p50-ish avg")}
          ${metric("Fallback Rate", "0", "Provider failover")}
        </div>
        <section class="card" style="margin-top:0.75rem">
          <h2>Probe inference</h2>
          <div class="actions" style="margin-top:0.6rem">
            <button class="btn primary" type="button" id="probe">Run /api/ai/complete probe</button>
            <button class="btn" type="button" id="refresh-probe">Refresh</button>
          </div>
        </section>
        <section class="card" style="margin-top:0.75rem">
          <h2>Recent inferences</h2>
          <p class="empty" id="probe-empty">${probeMsg}</p>
        </section>`,
      studio: `
        <section class="card">
          <h2>Timeline</h2>
          <p class="muted">Hook → proof → payoff. 7-scene EDC cut at 20s, or a 4-scene Hermes OS promo at 12.6s.</p>
          <div class="flow" style="margin-top:1rem">${["Hook","Problem","Demo","Proof","CTA"].map((n)=>`<span>${n}</span><i>→</i>`).join("")}<span class="end">Export</span></div>
        </section>
        <div class="grid split" style="margin-top:0.75rem">
          <section class="card"><h2>Active cut</h2><p class="muted">hermes_os_promo · 1920×1080 · 30 fps</p></section>
          <section class="card"><h2>Captions</h2><p class="muted">Burned-in, high contrast, 4-word lines.</p></section>
        </div>`,
      evolution: `
        <div class="grid metrics-3">
          ${metric("Running", "242", "Scored experiments")}
          ${metric("Crown", "#129", "Thumbnail B", true)}
          ${metric("Lift", "+18%", "Retention after hook rewrite")}
        </div>
        <section class="card" style="margin-top:0.75rem"><h2>Variant board</h2><p class="muted">Thumbnail B beat A on CTR. Money hooks keep winning. Losing intros are retired automatically.</p></section>`,
      analytics: `
        <div class="grid metrics">
          ${metric("Views", "2.1M", "Across channels")}
          ${metric("CTR", "6.8%", "+11% vs baseline", true)}
          ${metric("Retention", "54%", "+18% evolved")}
          ${metric("RPM", "$4.20", "+9%")}
        </div>
        <section class="card" style="margin-top:0.75rem"><h2>Forecast</h2><p class="muted">Channel health is Strong. Next 30 days assume the current operating loop stays on Improve.</p></section>`,
      memory: `
        <section class="card">
          <h2>Learned</h2>
          ${["Money hooks ↑23% CTR","Short first-frame motion beats stills","EDC niches compound on Shorts + TikTok"].map((x)=>`<div class="row"><h3>${x}</h3></div>`).join("")}
        </section>`,
      command: `
        <section class="card">
          <h2>Gateway</h2>
          <pre class="status" id="health-pre">checking…</pre>
        </section>
        <section class="card" style="margin-top:0.75rem">
          <h2>Ops</h2>
          <p class="muted">/livez process up · /readyz production key present · /health inference + models · /docs OpenAPI</p>
        </section>`,
      publishing: `
        <section class="card">
          <h2>Queue · 14 scheduled</h2>
          ${["YouTube Short · Automation hook","TikTok · Claude vs coding","Reels · Everyday Carry 20s"].map((x)=>`<div class="row"><h3>${x}</h3><span class="pill">Queued</span></div>`).join("")}
        </section>`,
      uploads: `
        <section class="card">
          <h2>Drop zone</h2>
          <p class="muted">Brand kits, stills, and source clips land here before Studio. Nothing is a dead file — uploads become graph nodes.</p>
        </section>`,
      settings: `
        <section class="card">
          <h2>Public door</h2>
          <p class="muted">This host is the locked gateway for Hermes Studios: OpenAI-compatible <code>/v1</code>, health, and OpenMontage delivery.</p>
          <pre class="status" style="margin-top:0.8rem">export OPENAI_BASE_URL=https://hermestudios.com/v1
export OPENAI_API_KEY=$HERMES_API_KEY</pre>
        </section>
        <p class="muted" style="margin:1rem 0 0"><a href="#/outro">End card</a> · <a href="/docs">/docs</a> · <a href="/health">/health</a></p>`,
    };
  }

  function currentId() {
    const hash = (location.hash || "#/overview").replace("#/", "");
    if (hash === "outro") return "outro";
    return PAGES.some((p) => p.id === hash) ? hash : "overview";
  }

  function enterConsole() {
    document.documentElement.classList.add("entered");
    document.documentElement.classList.remove("outro-mode");
    splash.classList.add("closing");
    splash.style.display = "none";
    outro.classList.remove("show");
    app.classList.add("show");
    if (!location.hash || location.hash === "#/" || location.hash === "#/splash") {
      location.hash = "#/overview";
    }
    render();
  }

  function showOutro() {
    document.documentElement.classList.remove("entered");
    document.documentElement.classList.add("outro-mode");
    app.classList.remove("show");
    splash.style.display = "none";
    outro.classList.add("show");
  }

  function render() {
    const id = currentId();
    if (id === "outro") {
      showOutro();
      return;
    }
    outro.classList.remove("show");
    if (splash.style.display !== "none" && !sessionStorage.getItem("hermes-entered")) {
      return;
    }
    app.classList.add("show");
    splash.style.display = "none";
    const page = PAGES.find((p) => p.id === id) || PAGES[0];
    titleEl.textContent = page.title;
    subEl.textContent = page.sub;
    main.innerHTML = views()[page.id];
    document.querySelectorAll("nav a").forEach((a) => {
      a.classList.toggle("active", a.getAttribute("href") === `#/${page.id}`);
    });
    if (page.id === "command") loadHealth();
    bindPage(page.id);
  }

  function bindPage(id) {
    document.querySelectorAll("[data-loop]").forEach((btn) => {
      btn.addEventListener("click", () => {
        loopStep = btn.dataset.loop;
        render();
      });
    });
    const form = document.getElementById("campaign-form");
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        launchMsg = "Launching agent orchestra…";
        render();
      });
    }
    document.getElementById("probe")?.addEventListener("click", async () => {
      inferences += 1;
      probeMsg = "Probe recorded. Gateway /v1/chat/completions is the production path.";
      try {
        const r = await fetch("/health");
        const data = await r.json();
        probeMsg = `Probe #${inferences} · backend ${data.backend || "unknown"} · reachable ${data.reachable}`;
      } catch (err) {
        probeMsg = `Probe #${inferences} · local console (${String(err)})`;
      }
      render();
    });
    document.getElementById("refresh-probe")?.addEventListener("click", () => render());
    document.getElementById("dry-run")?.addEventListener("click", () => {
      location.hash = "#/campaigns";
    });
  }

  async function loadHealth() {
    const el = document.getElementById("health-pre");
    if (!el) return;
    try {
      const r = await fetch("/health");
      el.textContent = JSON.stringify(await r.json(), null, 2);
    } catch (err) {
      el.textContent = String(err);
    }
  }

  function openPalette() {
    palette.classList.add("open");
    cmdList.innerHTML = PAGES.map((p) => `<button class="cmd-item" type="button" data-go="${p.id}">${p.title}</button>`).join("");
    cmdInput.value = "";
    cmdInput.focus();
    cmdList.querySelectorAll(".cmd-item").forEach((b) => {
      b.addEventListener("click", () => {
        location.hash = `#/${b.dataset.go}`;
        closePalette();
      });
    });
  }
  function closePalette() {
    palette.classList.remove("open");
  }

  document.getElementById("enter-console").addEventListener("click", () => {
    sessionStorage.setItem("hermes-entered", "1");
    enterConsole();
  });
  document.getElementById("back-console").addEventListener("click", () => {
    location.hash = "#/overview";
    enterConsole();
  });
  document.getElementById("open-cmd").addEventListener("click", openPalette);
  document.getElementById("launch-campaign").addEventListener("click", () => {
    location.hash = "#/campaigns";
  });
  document.getElementById("menu-toggle").addEventListener("click", (e) => {
    const open = sidebar.classList.toggle("open");
    e.currentTarget.setAttribute("aria-expanded", String(open));
  });
  palette.addEventListener("click", (e) => {
    if (e.target === palette) closePalette();
  });
  cmdInput.addEventListener("input", () => {
    const q = cmdInput.value.toLowerCase();
    cmdList.querySelectorAll(".cmd-item").forEach((b) => {
      b.hidden = !b.textContent.toLowerCase().includes(q);
    });
  });
  window.addEventListener("hashchange", render);
  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      palette.classList.contains("open") ? closePalette() : openPalette();
    }
    if (e.key === "Escape") closePalette();
  });

  if (location.hash === "#/overview" || sessionStorage.getItem("hermes-entered")) {
    sessionStorage.setItem("hermes-entered", "1");
    enterConsole();
  }
})();
