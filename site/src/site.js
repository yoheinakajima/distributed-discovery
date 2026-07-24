document.documentElement.classList.add("js");

const menu = document.querySelector(".nav-menu");
if (menu) {
  const mobile = window.matchMedia("(max-width: 760px)");
  const syncMenu = () => {
    if (mobile.matches) menu.removeAttribute("open");
    else menu.setAttribute("open", "");
  };
  syncMenu();
  mobile.addEventListener("change", syncMenu);
}

document.querySelectorAll("[data-research-catalog]").forEach((catalog) => {
  const search = catalog.querySelector("#study-search");
  const status = catalog.querySelector("#study-status");
  const program = catalog.querySelector("#study-program");
  const family = catalog.querySelector("#study-family");
  const evidence = catalog.querySelector("#study-evidence");
  const cards = Array.from(catalog.querySelectorAll("[data-study-card]"));
  const buttons = Array.from(catalog.querySelectorAll("[data-study-filter]"));
  if (!search || !status || !cards.length || !buttons.length) return;
  let activeFilter = "all";
  const render = () => {
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach((card) => {
      const categories = (card.dataset.category || "").split(" ");
      const matchesFilter = activeFilter === "all" || categories.includes(activeFilter);
      const matchesQuery = !query || (card.dataset.search || "").includes(query);
      const matchesProgram = !program || program.value === "all" || card.dataset.program === program.value;
      const matchesFamily = !family || family.value === "all" || card.dataset.family === family.value;
      const matchesEvidence = !evidence || evidence.value === "all" || card.dataset.evidence === evidence.value;
      const show = matchesFilter && matchesQuery && matchesProgram && matchesFamily && matchesEvidence;
      card.hidden = !show;
      if (show) visible += 1;
    });
    status.textContent = `${visible} ${visible === 1 ? "study" : "studies"} shown`;
  };
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.studyFilter || "all";
      buttons.forEach((candidate) => {
        candidate.setAttribute("aria-pressed", String(candidate === button));
      });
      render();
    });
  });
  search.addEventListener("input", render);
  [program, family, evidence].filter(Boolean).forEach((control) => control.addEventListener("change", render));
  render();
});

document.querySelectorAll("[data-output-lab]").forEach((lab) => {
  const kind = lab.dataset.outputLab;
  const controls = Array.from(lab.querySelectorAll("select[data-filter-key]"));
  const outputs = Array.from(lab.querySelectorAll("[data-output-key]"));
  const status = lab.querySelector("[data-output-status]");
  const rows = Array.from(document.querySelectorAll(`[data-output-row="${kind}"]`));
  if (!kind || !controls.length || !outputs.length || !status || !rows.length) return;
  const reset = lab.querySelector("[data-lab-reset]");
  const initialValues = new Map(controls.map((control) => [control, control.value]));
  const params = new URLSearchParams(window.location.search);
  controls.forEach((control) => {
    const requested = params.get(control.dataset.filterKey);
    if (requested && Array.from(control.options).some((option) => option.value === requested)) {
      control.value = requested;
    }
  });
  const render = () => {
    if (kind === "coverage") {
      const fixture = lab.querySelector("#coverage-fixture");
      const rule = lab.querySelector("#coverage-rule");
      const manual = lab.querySelector("#coverage-selection");
      const manualContainer = lab.querySelector("[data-manual-control]");
      if (fixture && rule && manual && manualContainer) {
        const enabled = rule.value === "manual-selection";
        manualContainer.hidden = !enabled;
        manual.disabled = !enabled;
        const available = Array.from(manual.options).filter((option) => rows.some((row) =>
          row.dataset.fixture === fixture.value && row.dataset.rule === "manual-selection" &&
          row.dataset.selection === option.value));
        Array.from(manual.options).forEach((option) => {
          option.hidden = !available.includes(option);
          option.disabled = !available.includes(option);
        });
        if (enabled && !available.includes(manual.options[manual.selectedIndex]) && available.length) {
          manual.value = available[0].value;
        }
      }
    }
    if (kind === "mechanisms") {
      const family = lab.querySelector("#mechanisms-family");
      const regime = lab.querySelector("#mechanisms-regime");
      const mechanism = lab.querySelector("#mechanisms-row");
      const tie = lab.querySelector("#mechanisms-tie");
      const constrain = (control, predicate) => {
        const available = Array.from(control.options).filter((option) => rows.some((row) =>
          predicate(row, option.value)));
        Array.from(control.options).forEach((option) => {
          option.hidden = !available.includes(option);
          option.disabled = !available.includes(option);
        });
        if (!available.includes(control.options[control.selectedIndex]) && available.length) {
          control.value = available[0].value;
        }
      };
      if (family && regime && mechanism && tie) {
        constrain(regime, (row, value) => row.dataset.family === family.value && row.dataset.regime === value);
        constrain(mechanism, (row, value) => row.dataset.family === family.value &&
          row.dataset.regime === regime.value && row.dataset.mechanism === value);
        constrain(tie, (row, value) => row.dataset.family === family.value &&
          row.dataset.regime === regime.value && row.dataset.mechanism === mechanism.value &&
          row.dataset.tieRole === value);
      }
    }
    if (kind === "evidence-acquisition") {
      const agents = lab.querySelector("#acquisition-agents");
      const accuracy = lab.querySelector("#acquisition-accuracy");
      const cost = lab.querySelector("#acquisition-cost");
      if (agents && accuracy && cost) {
        const available = Array.from(cost.options).filter((option) => rows.some((row) =>
          row.dataset.agents === agents.value && row.dataset.accuracy === accuracy.value &&
          row.dataset.cost === option.value));
        Array.from(cost.options).forEach((option) => {
          option.hidden = !available.includes(option);
          option.disabled = !available.includes(option);
        });
        if (!available.includes(cost.options[cost.selectedIndex]) && available.length) {
          cost.value = available[0].value;
        }
      }
    }
    controls.forEach((control) => {
      const limitingId = control.dataset.limitBy;
      if (!limitingId) return;
      const limitingControl = document.getElementById(limitingId);
      if (!limitingControl) return;
      const limit = Number(limitingControl.value);
      const options = Array.from(control.options);
      options.forEach((option) => {
        const unavailable = Number(option.value) > limit;
        option.hidden = unavailable;
        option.disabled = unavailable;
      });
      if (Number(control.value) > limit) {
        const firstAvailable = options.find((option) => !option.disabled);
        if (firstAvailable) control.value = firstAvailable.value;
      }
    });
    const activeControls = controls.filter((control) => !control.disabled);
    const selected = rows.find((row) => activeControls.every((control) =>
      row.getAttribute(`data-${control.dataset.filterKey}`) === control.value));
    rows.forEach((row) => { row.hidden = row !== selected; });
    if (!selected) {
      outputs.forEach((output) => { output.textContent = "not registered"; });
      status.textContent = "No exact registered row matches this selection.";
      return;
    }
    outputs.forEach((output) => {
      output.textContent = selected.getAttribute(`data-${output.dataset.outputKey}`) || "not applicable";
    });
    Array.from(lab.querySelectorAll("[data-exact-metric]")).forEach((metric) => {
      const display = metric.querySelector("strong")?.textContent || "not applicable";
      const exact = metric.querySelector("code")?.textContent || "not applicable";
      metric.setAttribute("aria-label", `${metric.dataset.metricLabel}: ${display}; exact ${exact}.`);
    });
    if (kind === "threshold") {
      const threshold = activeControls.find((control) => control.dataset.filterKey === "threshold")?.value;
      Array.from(lab.querySelectorAll("[data-threshold-point]")).forEach((point) => {
        point.classList.toggle("selected", point.dataset.thresholdPoint === threshold);
      });
    }
    Array.from(lab.querySelectorAll("[data-output-bar-key]")).forEach((bar) => {
      const value = Number(selected.getAttribute(`data-${bar.dataset.outputBarKey}`) || 0);
      bar.style.setProperty("--bar-value", `${Math.max(0, Math.min(100, value))}%`);
    });
    const selection = activeControls.map((control) => {
      const option = control.options[control.selectedIndex];
      return `${control.previousElementSibling?.textContent || control.dataset.filterKey}: ${option.textContent}`;
    }).join("; ");
    status.textContent = `Showing one exact ${kind.replace(/-/g, " ")} row — ${selection}.`;
    const url = new URL(window.location.href);
    controls.forEach((control) => {
      if (control.disabled) url.searchParams.delete(control.dataset.filterKey);
      else url.searchParams.set(control.dataset.filterKey, control.value);
    });
    window.history.replaceState({}, "", url);
  };
  controls.forEach((control) => control.addEventListener("change", render));
  if (reset) reset.addEventListener("click", () => {
    controls.forEach((control) => { control.value = initialValues.get(control); });
    render();
  });
  render();
});

document.querySelectorAll("[data-copy-exact]").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = document.getElementById(button.dataset.copyTarget || "");
    if (!target) return;
    await navigator.clipboard.writeText(target.textContent || "");
    button.textContent = "Copied";
  });
});

document.querySelectorAll("[data-atlas-lab]").forEach((lab) => {
  const filters = Array.from(lab.querySelectorAll("select[data-atlas-filter]"));
  const architecture = lab.querySelector("#atlas-architecture");
  const status = lab.querySelector("[data-atlas-status]");
  const reset = lab.querySelector("[data-lab-reset]");
  const takeaway = lab.querySelector("[data-atlas-takeaway]");
  const rows = Array.from(document.querySelectorAll("[data-atlas-architecture]"));
  const validity = Array.from(document.querySelectorAll("[data-atlas-validity]"));
  const points = Array.from(lab.querySelectorAll("[data-atlas-point]"));
  const outputs = Array.from(lab.querySelectorAll("[data-output-key]"));
  if (!filters.length || !architecture || !status || !rows.length || !validity.length) return;
  const initial = { architecture: architecture.value, filters: filters.map((control) => control.value) };
  const params = new URLSearchParams(window.location.search);
  const requestedArchitecture = params.get("architecture");
  if (requestedArchitecture && Array.from(architecture.options).some((option) => option.value === requestedArchitecture)) {
    architecture.value = requestedArchitecture;
  }
  const matchesFilters = (row) => filters.every((control) =>
    row.getAttribute(`data-${control.dataset.atlasFilter}`) === control.value);
  const syncFilters = (row) => filters.forEach((control) => {
    control.value = row.getAttribute(`data-${control.dataset.atlasFilter}`) || control.value;
  });
  const render = (fromArchitecture = false) => {
    if (fromArchitecture && architecture.value !== "custom") {
      const named = rows.find((row) => row.dataset.atlasArchitecture === architecture.value);
      if (named) syncFilters(named);
    }
    const validityRow = validity.find(matchesFilters);
    const selected = rows.find(matchesFilters);
    if (!validityRow || validityRow.dataset.valid !== "true" || !selected) {
      architecture.value = "custom";
      status.textContent = `Not a registered coherent architecture: ${validityRow?.dataset.reason || "combination is outside the registry"}.`;
      outputs.forEach((output) => { output.textContent = "not applicable"; });
      points.forEach((point) => point.classList.remove("selected"));
      if (takeaway) takeaway.textContent = "Invalid combinations remain visible as registered rejections; choose a coherent row to compare outcomes.";
    } else {
      architecture.value = selected.dataset.atlasArchitecture;
      outputs.forEach((output) => {
        output.textContent = selected.getAttribute(`data-${output.dataset.outputKey}`) || "not applicable";
      });
      points.forEach((point) => point.classList.toggle("selected", point.dataset.atlasPoint === architecture.value));
      status.textContent = `Showing coherent architecture ${architecture.value}: ${validityRow.dataset.reason}.`;
      if (takeaway) takeaway.textContent = "Coherent architectures expose tradeoffs; the selected row is compared within the declared Pareto objectives.";
    }
    const url = new URL(window.location.href);
    url.searchParams.set("architecture", architecture.value);
    filters.forEach((control) => url.searchParams.set(control.dataset.atlasFilter, control.value));
    window.history.replaceState({}, "", url);
  };
  architecture.addEventListener("change", () => render(true));
  filters.forEach((control) => control.addEventListener("change", () => render(false)));
  points.forEach((point) => point.addEventListener("click", () => {
    architecture.value = point.dataset.atlasPoint;
    render(true);
  }));
  if (reset) reset.addEventListener("click", () => {
    architecture.value = initial.architecture;
    filters.forEach((control, index) => { control.value = initial.filters[index]; });
    render(true);
  });
  render(architecture.value !== "custom");
});

document.querySelectorAll("[data-benchmark-lab]").forEach((lab) => {
  const select = lab.querySelector("select");
  const status = lab.querySelector("#benchmark-status");
  const reset = lab.querySelector("[data-table-lab-reset]");
  const rows = Array.from(document.querySelectorAll("tr[data-task]"));
  if (!select || !status) return;
  const requested = new URLSearchParams(window.location.search).get("task");
  if (requested && Array.from(select.options).some((option) => option.value === requested)) select.value = requested;
  const render = () => {
    let visible = 0;
    let first = null;
    rows.forEach((row) => {
      const show = select.value === "all" || row.dataset.task === select.value;
      row.hidden = !show;
      if (show) { visible += 1; if (!first) first = row; }
    });
    status.textContent = `Showing ${visible} exact compatible row${visible === 1 ? "" : "s"}.`;
    const cells = first ? Array.from(first.cells).map((cell) => cell.textContent.trim()) : [];
    const values = { count: String(visible), task: select.value === "all" ? "All tasks" : select.value, strategy: cells[1] || "—", vector: cells[2] || "—" };
    lab.querySelectorAll("[data-benchmark-output]").forEach((output) => { output.textContent = values[output.dataset.benchmarkOutput] || "—"; });
    const url = new URL(window.location.href);
    url.searchParams.set("task", select.value);
    window.history.replaceState({}, "", url);
  };
  select.addEventListener("change", render);
  if (reset) reset.addEventListener("click", () => { select.value = "all"; render(); });
  render();
});

document.querySelectorAll("[data-experiment-lab]").forEach((lab) => {
  const select = lab.querySelector("select");
  const status = lab.querySelector("#experiment-status");
  const reset = lab.querySelector("[data-table-lab-reset]");
  const rows = Array.from(document.querySelectorAll("tr[data-power-scenario]"));
  if (!select || !status) return;
  const requested = new URLSearchParams(window.location.search).get("scenario");
  if (requested && Array.from(select.options).some((option) => option.value === requested)) select.value = requested;
  const render = () => {
    let visible = 0;
    let first = null;
    rows.forEach((row) => {
      const show = select.value === "all" || row.dataset.powerScenario === select.value;
      row.hidden = !show;
      if (show) { visible += 1; if (!first) first = row; }
    });
    status.textContent = `Showing ${visible} synthetic power row${visible === 1 ? "" : "s"}.`;
    const cells = first ? Array.from(first.cells).map((cell) => cell.textContent.trim()) : [];
    const values = { count: String(visible), scenario: select.value === "all" ? "All scenarios" : select.value, power: cells[4] || "—", mde: cells[5] || "—" };
    lab.querySelectorAll("[data-experiment-output]").forEach((output) => { output.textContent = values[output.dataset.experimentOutput] || "—"; });
    const url = new URL(window.location.href);
    url.searchParams.set("scenario", select.value);
    window.history.replaceState({}, "", url);
  };
  select.addEventListener("change", render);
  if (reset) reset.addEventListener("click", () => { select.value = "all"; render(); });
  render();
});

document.querySelectorAll("[data-attention-lab]").forEach(async (lab) => {
  const n = lab.querySelector("#attention-n");
  const p = lab.querySelector("#attention-p");
  const q = lab.querySelector("#attention-q");
  const k = lab.querySelector("#attention-k");
  const reward = lab.querySelector("#attention-reward");
  const status = lab.querySelector("#attention-status");
  const reset = lab.querySelector("[data-table-lab-reset]");
  const takeaway = lab.querySelector("[data-attention-takeaway]");
  if (!n || !p || !q || !k || !reward || !status) return;
  let registeredCells = [];
  try {
    const response = await fetch("../data/attention/census.json");
    const payload = await response.json();
    registeredCells = payload.cells || [];
  } catch (_error) {
    status.textContent = "The local attention census could not be loaded; the representative exact fallback remains below.";
    return;
  }
  const render = () => {
    const validCounts = Array.from(k.options).filter((option) => Number(option.value) <= Number(n.value));
    Array.from(k.options).forEach((option) => { option.hidden = Number(option.value) > Number(n.value); });
    if (!validCounts.some((option) => option.value === k.value)) k.value = validCounts[0].value;
    const selectedCell = registeredCells.find((cell) => String(cell.agents) === n.value &&
      String(cell.private_accuracy) === p.value && String(cell.shared_accuracy) === q.value);
    const selected = selectedCell?.profiles?.find((profile) => String(profile.attenders) === k.value);
    if (!selectedCell || !selected) {
      status.textContent = "No registered exact attention profile matches this selection.";
      return;
    }
    const rewardResult = selected.rewards?.[reward.value];
    const equilibriumRegistry = selectedCell.reward_equilibria?.[reward.value];
    const licensed = reward.value === "public-reader-license";
    const equilibrium = licensed
      ? (equilibriumRegistry?.binding_implemented_counts || []).includes(Number(k.value)) ? "binding implementation" : "no"
      : (equilibriumRegistry?.weak || []).includes(Number(k.value)) ? "weak" : "no";
    status.textContent = "Showing one exact attention profile selected from local JSON. Ignoring roles do not receive the public clue.";
    const values = {
      discovery: selected.discovery,
      attending: licensed ? "not applicable" : rewardResult?.attending ?? "—",
      ignoring: licensed ? "not applicable" : rewardResult?.ignoring ?? "—",
      optimum: selectedCell.social_optima.includes(Number(k.value)) ? "yes" : "no",
      equilibrium,
      wedge: selected.attention_wedge ?? "—",
    };
    lab.querySelectorAll("[data-attention-output]").forEach((output) => { output.textContent = values[output.dataset.attentionOutput] || "—"; });
    if (takeaway) takeaway.textContent = values.optimum === "yes" ? "This reader count is socially optimal in the selected registered cell; its reward equilibrium is reported separately." : "This reader count is not socially optimal in the selected registered cell; compare its incentive wedge and equilibrium status.";
    const url = new URL(window.location.href);
    [["n", n], ["p", p], ["q", q], ["k", k], ["reward", reward]].forEach(([key, control]) => url.searchParams.set(key, control.value));
    window.history.replaceState({}, "", url);
  };
  [n, p, q, k, reward].forEach((control) => control.addEventListener("change", render));
  n.value = "4";
  p.value = "1/2";
  q.value = "3/4";
  k.value = "1";
  reward.value = "equal-split";
  const params = new URLSearchParams(window.location.search);
  [["n", n], ["p", p], ["q", q], ["k", k], ["reward", reward]].forEach(([key, control]) => {
    const value = params.get(key);
    if (value && Array.from(control.options).some((option) => option.value === value)) control.value = value;
  });
  if (reset) reset.addEventListener("click", () => {
    n.value = "4"; p.value = "1/2"; q.value = "3/4"; k.value = "1"; reward.value = "equal-split"; render();
  });
  render();
});

document.querySelectorAll("[data-audience-lab]").forEach((lab) => {
  const n = lab.querySelector("#audience-n");
  const p = lab.querySelector("#audience-p");
  const q = lab.querySelector("#audience-q");
  const use = lab.querySelector("#audience-use");
  const g = lab.querySelector("#audience-g");
  const m = lab.querySelector("#audience-m");
  const mechanism = lab.querySelector("#audience-mechanism");
  const status = lab.querySelector("#audience-status");
  const reset = lab.querySelector("[data-table-lab-reset]");
  const takeaway = lab.querySelector("[data-audience-takeaway]");
  const bindingRows = Array.from(document.querySelectorAll("tr[data-audience-row]"));
  const voluntaryRows = Array.from(document.querySelectorAll("tr[data-voluntary-row]"));
  const garblingRows = Array.from(document.querySelectorAll("tr[data-garbling-row]"));
  const mechanismRows = Array.from(document.querySelectorAll("tr[data-mechanism-row]"));
  const bindingSection = document.querySelector("[data-binding-section]");
  const voluntarySection = document.querySelector("[data-voluntary-section]");
  if (!n || !p || !q || !use || !g || !m || !mechanism || !status) return;
  const render = () => {
    let bindingVisible = 0;
    let voluntaryVisible = 0;
    let garblingVisible = 0;
    let mechanismVisible = 0;
    bindingRows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.m === m.value && use.value === "binding";
      row.hidden = !show;
      if (show) bindingVisible += 1;
    });
    voluntaryRows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.m === m.value && use.value === "voluntary";
      row.hidden = !show;
      if (show) voluntaryVisible += 1;
    });
    garblingRows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.g === g.value && row.dataset.m === m.value;
      row.hidden = !show;
      if (show) garblingVisible += 1;
    });
    mechanismRows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.mechanism === mechanism.value;
      row.hidden = !show;
      if (show) mechanismVisible += 1;
    });
    if (bindingSection) bindingSection.hidden = use.value !== "binding";
    if (voluntarySection) voluntarySection.hidden = use.value !== "voluntary";
    status.textContent = `Showing ${bindingVisible} binding row, ${voluntaryVisible} voluntary profile${voluntaryVisible === 1 ? "" : "s"}, ${garblingVisible} feasible garbling row${garblingVisible === 1 ? "" : "s"}, and ${mechanismVisible} mechanism row. A zero garbling count means g>q or audience zero is outside the positive-audience garbling registry.`;
    const primary = (use.value === "binding" ? bindingRows : voluntaryRows).find((row) => !row.hidden);
    const primaryCells = primary ? Array.from(primary.cells).map((cell) => cell.textContent.trim()) : [];
    const mechanismRow = mechanismRows.find((row) => !row.hidden);
    const mechanismCells = mechanismRow ? Array.from(mechanismRow.cells).map((cell) => cell.textContent.trim()) : [];
    const garblingRow = garblingRows.find((row) => !row.hidden);
    const garblingCells = garblingRow ? Array.from(garblingRow.cells).map((cell) => cell.textContent.trim()) : [];
    const values = use.value === "binding"
      ? { discovery: primaryCells[4], equilibrium: `Optimal: ${primaryCells[8] || "—"}`, implementation: mechanismCells[8], budget: mechanismCells[7] || mechanismCells[6], institution: "Binding access", garbling: garblingCells[6] }
      : { discovery: primaryCells[5], equilibrium: primaryCells[6], implementation: primaryCells[8], budget: mechanismCells[7] || mechanismCells[6], institution: "Voluntary use", garbling: garblingCells[6] };
    lab.querySelectorAll("[data-audience-output]").forEach((output) => { output.textContent = values[output.dataset.audienceOutput] || "—"; });
    if (takeaway) takeaway.textContent = use.value === "binding" ? "Binding access assigns the reader count directly; optimality and mechanism implementation are separate outputs." : "Voluntary access does not guarantee voluntary use; equilibrium readers and the binding optimum can differ.";
    const url = new URL(window.location.href);
    [["n", n], ["p", p], ["q", q], ["use", use], ["g", g], ["m", m], ["mechanism", mechanism]].forEach(([key, control]) => url.searchParams.set(key, control.value));
    window.history.replaceState({}, "", url);
  };
  [n, p, q, use, g, m, mechanism].forEach((control) => control.addEventListener("change", render));
  n.value = "2";
  p.value = "1/3";
  q.value = "1/2";
  use.value = "binding";
  g.value = "1/3";
  m.value = "1";
  mechanism.value = "binding_exclusive_delivery";
  const params = new URLSearchParams(window.location.search);
  [["n", n], ["p", p], ["q", q], ["use", use], ["g", g], ["m", m], ["mechanism", mechanism]].forEach(([key, control]) => {
    const value = params.get(key);
    if (value && Array.from(control.options).some((option) => option.value === value)) control.value = value;
  });
  if (reset) reset.addEventListener("click", () => {
    n.value = "2"; p.value = "1/3"; q.value = "1/2"; use.value = "binding"; g.value = "1/3"; m.value = "1"; mechanism.value = "binding_exclusive_delivery"; render();
  });
  render();
});

document.querySelectorAll("[data-conditional-lab]").forEach((lab) => {
  const n = lab.querySelector("#conditional-n");
  const p = lab.querySelector("#conditional-p");
  const q = lab.querySelector("#conditional-q");
  const policy = lab.querySelector("#conditional-policy");
  const status = lab.querySelector("#conditional-status");
  const reset = lab.querySelector("[data-table-lab-reset]");
  const rows = Array.from(document.querySelectorAll("tr[data-conditional-row]"));
  if (!n || !p || !q || !policy || !status) return;
  const render = () => {
    const compatible = Array.from(policy.options).filter((option) => option.dataset.n === n.value);
    Array.from(policy.options).forEach((option) => { option.hidden = option.dataset.n !== n.value; });
    if (!compatible.some((option) => option.value === policy.value)) policy.value = compatible[0].value;
    let visible = 0;
    let selected = null;
    rows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.profile === policy.value;
      row.hidden = !show;
      if (show) { visible += 1; selected = row; }
    });
    status.textContent = `Showing ${visible} exact registered profile. Every role observes both clues.`;
    const cells = selected ? Array.from(selected.cells).map((cell) => cell.textContent.trim()) : [];
    const values = { private: cells[3], public: cells[4], "contrarian-count": cells[5], discovery: cells[6], equilibrium: cells[8], optimal: cells[9], contrarian: cells[10] };
    lab.querySelectorAll("[data-conditional-output]").forEach((output) => { output.textContent = values[output.dataset.conditionalOutput] || "—"; });
    const url = new URL(window.location.href);
    [["n", n], ["p", p], ["q", q], ["profile", policy]].forEach(([key, control]) => url.searchParams.set(key, control.value));
    window.history.replaceState({}, "", url);
  };
  [n, p, q, policy].forEach((control) => control.addEventListener("change", render));
  n.value = "2";
  p.value = "1/3";
  q.value = "1/2";
  const params = new URLSearchParams(window.location.search);
  [["n", n], ["p", p], ["q", q], ["profile", policy]].forEach(([key, control]) => {
    const value = params.get(key);
    if (value && Array.from(control.options).some((option) => option.value === value)) control.value = value;
  });
  if (reset) reset.addEventListener("click", () => { n.value = "2"; p.value = "1/3"; q.value = "1/2"; render(); });
  render();
});

document.querySelectorAll("[data-incremental-lab]").forEach((lab) => {
  const mode = lab.querySelector("#incremental-mode");
  const targets = lab.querySelector("#incremental-targets");
  const agents = lab.querySelector("#incremental-agents");
  const accuracy = lab.querySelector("#incremental-accuracy");
  const channel = lab.querySelector("#incremental-channel");
  const step = lab.querySelector("#incremental-step");
  const comparison = lab.querySelector("#incremental-comparison");
  const status = lab.querySelector("#incremental-status");
  const pointControls = Array.from(lab.querySelectorAll("[data-point-control]"));
  const channelControls = Array.from(lab.querySelectorAll("[data-channel-control]"));
  const outputs = Array.from(lab.querySelectorAll("[data-incremental-output]"));
  const chart = lab.querySelector("[data-incremental-chart]");
  const chartPoints = Array.from(lab.querySelectorAll("[data-profile-point]"));
  const comparisonOutput = lab.querySelector("[data-incremental-comparison]");
  const rows = Array.from(document.querySelectorAll("tr[data-incremental-row]"));
  if (!mode || !targets || !agents || !accuracy || !channel || !step ||
      !comparison || !status || !chart || !comparisonOutput || !rows.length) return;

  const fraction = (value) => {
    const parts = value.split("/").map(Number);
    return parts.length === 2 ? parts[0] / parts[1] : parts[0];
  };
  const setControlGroup = (controls, enabled) => {
    controls.forEach((container) => {
      container.hidden = !enabled;
      const control = container.querySelector("select");
      if (control) control.disabled = !enabled;
    });
  };
  const constrainAccuracy = () => {
    const available = Array.from(accuracy.options).filter((option) =>
      (option.dataset.targets || "").split(",").includes(targets.value));
    Array.from(accuracy.options).forEach((option) => {
      const enabled = available.includes(option);
      option.hidden = !enabled;
      option.disabled = !enabled;
    });
    if (!available.includes(accuracy.options[accuracy.selectedIndex])) accuracy.value = available[0].value;
  };
  const constrainStep = () => {
    const maximum = mode.value === "channel" ? 2 : Number(agents.value) - 1;
    const available = Array.from(step.options).filter((option) => Number(option.value) <= maximum);
    Array.from(step.options).forEach((option) => {
      const enabled = available.includes(option);
      option.hidden = !enabled;
      option.disabled = !enabled;
    });
    if (!available.includes(step.options[step.selectedIndex])) step.value = available[0].value;
  };
  const rowFor = (channelId = channel.value) => rows.find((row) => {
    if (row.dataset.mode !== mode.value || row.dataset.blockSize !== step.value) return false;
    if (mode.value === "channel") return row.dataset.channel === channelId;
    return row.dataset.targets === targets.value && row.dataset.agents === agents.value &&
      row.dataset.accuracy === accuracy.value;
  });
  const constrainComparison = (selected) => {
    const selectedAccuracy = selected?.dataset.accuracy;
    const available = Array.from(comparison.options).filter((option) =>
      option.value === "none" ||
      (option.dataset.accuracy === selectedAccuracy && option.value !== channel.value));
    Array.from(comparison.options).forEach((option) => {
      const enabled = available.includes(option);
      option.hidden = !enabled;
      option.disabled = !enabled;
    });
    if (!available.includes(comparison.options[comparison.selectedIndex])) {
      comparison.value = available.find((option) => option.value !== "none")?.value || "none";
    }
  };
  const render = () => {
    const channelMode = mode.value === "channel";
    setControlGroup(pointControls, !channelMode);
    setControlGroup(channelControls, channelMode);
    if (!channelMode) constrainAccuracy();
    constrainStep();
    const selected = rowFor();
    if (channelMode) constrainComparison(selected);
    rows.forEach((row) => { row.hidden = row !== selected; });
    if (!selected) {
      outputs.forEach((output) => { output.textContent = "not registered"; });
      status.textContent = "No exact registered transition matches this selection.";
      return;
    }
    outputs.forEach((output) => {
      output.textContent = selected.getAttribute(`data-${output.dataset.incrementalOutput}`) || "not applicable";
    });
    const profile = (selected.dataset.discoveryProfile || "").split("|");
    chartPoints.forEach((point, index) => {
      const value = profile[index];
      point.hidden = !value;
      point.classList.toggle("selected", index + 1 === Number(step.value));
      point.classList.toggle("next", index + 1 === Number(step.value) + 1);
      if (!value) return;
      const label = point.querySelector("[data-profile-value]");
      const bar = point.querySelector("[data-profile-bar]");
      if (label) label.textContent = value;
      if (bar) bar.style.setProperty("--profile-value", `${fraction(value) * 100}%`);
    });
    chart.setAttribute("aria-label", `Exact discovery profile ${profile.join(", ")}; selected transition s=${step.value} to s=${Number(step.value) + 1}.`);
    const source = channelMode
      ? channel.options[channel.selectedIndex].textContent
      : `M=${targets.value}, N=${agents.value}, p=${accuracy.value}`;
    status.textContent = `Showing ${source}, s=${step.value}→${Number(step.value) + 1}; net increment ${selected.dataset.netIncrement} (${selected.dataset.sign}).`;
    if (channelMode && comparison.value !== "none") {
      const compared = rowFor(comparison.value);
      const name = comparison.options[comparison.selectedIndex].textContent;
      comparisonOutput.textContent = compared
        ? `${name}: ${compared.dataset.groupDiscovery} → ${compared.dataset.nextGroupDiscovery}; net ${compared.dataset.netIncrement} (${compared.dataset.sign}).`
        : "No same-accuracy comparison is registered for this step.";
    } else {
      comparisonOutput.textContent = channelMode
        ? "No distinct same-accuracy comparison is registered for this channel."
        : "Switch to registered channels to compare the same-accuracy noisy point and guaranteed shortlist.";
    }
  };
  [mode, targets, agents, accuracy, channel, step, comparison].forEach((control) =>
    control.addEventListener("change", render));
  render();
});

document.querySelectorAll("[data-frontier-lab]").forEach((lab) => {
  const family = lab.querySelector("#frontier-family");
  const targets = lab.querySelector("#frontier-targets");
  const agents = lab.querySelector("#frontier-agents");
  const parameter = lab.querySelector("#frontier-parameter");
  const step = lab.querySelector("#frontier-step");
  const budget = lab.querySelector("#frontier-budget");
  const status = lab.querySelector("#frontier-status");
  const reset = lab.querySelector("[data-frontier-reset]");
  const rows = Array.from(document.querySelectorAll("tr[data-frontier-row]"));
  if (!family || !targets || !agents || !parameter || !step || !budget || !status || !rows.length) return;

  const defaults = {
    family: "symmetric-noisy-point", targets: "4", agents: "3",
    channel: "point-m4-p1of2", step: "1", budget: "1",
  };
  const fraction = (value) => {
    const parts = String(value).split("/").map(Number);
    return parts.length === 2 ? parts[0] / parts[1] : parts[0];
  };
  const percentage = (value) => {
    if (!value || value === "zero-error") return "not applicable";
    const rendered = (fraction(value) * 100).toFixed(1).replace(/\.0$/, "");
    return `${rendered}%`;
  };
  const profile = (row, key) => (row.getAttribute(`data-${key}`) || "").split("|").filter(Boolean);
  const constrainParameters = () => {
    const available = Array.from(parameter.options).filter((option) =>
      option.dataset.family === family.value && option.dataset.targets === targets.value);
    Array.from(parameter.options).forEach((option) => {
      const enabled = available.includes(option);
      option.hidden = !enabled;
      option.disabled = !enabled;
    });
    if (!available.includes(parameter.options[parameter.selectedIndex]) && available.length) {
      parameter.value = available[0].value;
    }
  };
  const constrainIndexed = (control, maximum) => {
    const available = Array.from(control.options).filter((option) => Number(option.value) <= maximum);
    Array.from(control.options).forEach((option) => {
      const enabled = available.includes(option);
      option.hidden = !enabled;
      option.disabled = !enabled;
    });
    if (!available.includes(control.options[control.selectedIndex]) && available.length) {
      control.value = available[0].value;
    }
  };
  const setMetric = (key, exact) => {
    const metric = lab.querySelector(`[data-frontier-output="${key}"]`);
    if (!metric) return;
    const primary = metric.querySelector("strong");
    const secondary = metric.querySelector("code");
    if (primary) primary.textContent = percentage(exact);
    if (secondary) secondary.textContent = exact || "not applicable";
    metric.setAttribute("aria-label", `${metric.querySelector("span")?.textContent}: ${percentage(exact)}; exact ${exact || "not applicable"}.`);
  };
  const drawProfile = (kind, values, selectedIndex, recoveryIndex = null) => {
    const chart = lab.querySelector(`[data-frontier-chart="${kind}"]`);
    if (!chart) return;
    const points = Array.from(chart.querySelectorAll("[data-frontier-point]"));
    points.forEach((point, index) => {
      const exact = values[index];
      point.hidden = !exact;
      point.classList.toggle("selected", index + 1 === selectedIndex);
      point.classList.toggle("next", recoveryIndex !== null && index + 1 === recoveryIndex);
      if (!exact) return;
      const value = point.querySelector("[data-frontier-value]");
      const bar = point.querySelector("[data-frontier-bar]");
      if (value) value.textContent = `${percentage(exact)} · ${exact}`;
      if (bar) bar.style.setProperty("--profile-value", `${Math.max(0, Math.min(100, fraction(exact) * 100))}%`);
    });
    chart.setAttribute("aria-label", `${kind} exact profile: ${values.join(", ")}; selected index ${selectedIndex}.`);
  };
  const render = () => {
    constrainParameters();
    constrainIndexed(step, Number(agents.value) - 1);
    constrainIndexed(budget, Math.min(Number(targets.value), Number(agents.value)));
    const selected = rows.find((row) => row.dataset.channel === parameter.value && row.dataset.agents === agents.value);
    rows.forEach((row) => { row.hidden = row !== selected; });
    if (!selected) {
      status.textContent = "No exact registered scenario matches this selection.";
      return;
    }
    const pooled = profile(selected, "pooled-profile");
    const discovery = profile(selected, "discovery-profile");
    const increments = profile(selected, "increment-profile");
    const ratios = profile(selected, "ratio-profile");
    const budgets = profile(selected, "budget-profile");
    const stepIndex = Number(step.value) - 1;
    const budgetIndex = Number(budget.value) - 1;
    const threshold = selected.dataset.threshold;
    setMetric("q", selected.dataset.q);
    setMetric("private", selected.dataset.private);
    setMetric("pooled", pooled[stepIndex]);
    setMetric("discovery", discovery[stepIndex]);
    setMetric("increment", increments[stepIndex]);
    setMetric("ratio", ratios[stepIndex]);
    setMetric("threshold", threshold);
    setMetric("budget-value", budgets[budgetIndex]);
    ["recovery-budget", "sharing-class", "full-class"].forEach((key) => {
      const output = lab.querySelector(`[data-frontier-text="${key}"]`);
      if (output) output.textContent = selected.getAttribute(`data-${key}`) || "not applicable";
    });
    drawProfile("discovery", discovery, Number(step.value));
    drawProfile("pooled", pooled, Number(step.value));
    drawProfile("budget", budgets, Number(budget.value), Number(selected.dataset.recoveryBudget));
    const thresholdText = lab.querySelector("[data-frontier-threshold]");
    if (thresholdText) thresholdText.textContent = `At s=${step.value}, ρ=${ratios[stepIndex]} versus 1−q=${threshold}; increment ${increments[stepIndex]}.`;
    const recoveryText = lab.querySelector("[data-frontier-recovery]");
    if (recoveryText) recoveryText.textContent = `Selected L=${budget.value}; the first budget recovering P_N is L*=${selected.dataset.recoveryBudget}.`;
    const label = parameter.options[parameter.selectedIndex].textContent;
    status.textContent = `Showing ${label}, M=${targets.value}, N=${agents.value}, s=${step.value}→${Number(step.value) + 1}, L=${budget.value}: ${selected.dataset.sharingClass}; ${selected.dataset.fullClass}.`;
    const url = new URL(window.location.href);
    [["family", family], ["m", targets], ["n", agents], ["channel", parameter], ["s", step], ["l", budget]].forEach(([key, control]) => url.searchParams.set(key, control.value));
    window.history.replaceState({}, "", url);
  };
  const params = new URLSearchParams(window.location.search);
  family.value = defaults.family;
  targets.value = defaults.targets;
  agents.value = defaults.agents;
  parameter.value = defaults.channel;
  step.value = defaults.step;
  budget.value = defaults.budget;
  [["family", family], ["m", targets], ["n", agents], ["channel", parameter], ["s", step], ["l", budget]].forEach(([key, control]) => {
    const requested = params.get(key);
    if (requested && Array.from(control.options).some((option) => option.value === requested)) control.value = requested;
  });
  [family, targets, agents, parameter, step, budget].forEach((control) => control.addEventListener("change", render));
  if (reset) reset.addEventListener("click", () => {
    family.value = defaults.family;
    targets.value = defaults.targets;
    agents.value = defaults.agents;
    parameter.value = defaults.channel;
    step.value = defaults.step;
    budget.value = defaults.budget;
    render();
  });
  render();
});

document.querySelectorAll("[data-coordination-lab]").forEach((lab) => {
  const accuracy = lab.querySelector("#coordination-accuracy");
  const dependence = lab.querySelector("#coordination-dependence");
  const regime = lab.querySelector("#coordination-regime");
  const baseline = lab.querySelector("#coordination-baseline");
  const status = lab.querySelector("#coordination-status");
  const reset = lab.querySelector("[data-coordination-reset]");
  const rows = Array.from(document.querySelectorAll("tr[data-coordination-row]"));
  if (!accuracy || !dependence || !regime || !baseline || !status || !rows.length) return;
  const fraction = (value) => {
    const parts = String(value).split("/").map(Number);
    return parts.length === 2 ? parts[0] / parts[1] : parts[0];
  };
  const percentage = (value) => `${(fraction(value) * 100).toFixed(1).replace(/\.0$/, "")}%`;
  const setMetric = (key, exact) => {
    const card = lab.querySelector(`[data-coordination-output="${key}"]`);
    if (!card) return;
    const strong = card.querySelector("strong");
    const code = card.querySelector("code");
    if (strong) strong.textContent = percentage(exact);
    if (code) code.textContent = exact;
  };
  const selectedRow = () => rows.find((row) =>
    row.dataset.accuracy === accuracy.value && row.dataset.dependence === dependence.value);
  const render = () => {
    const selected = selectedRow();
    rows.forEach((row) => { row.hidden = row !== selected; });
    if (!selected) {
      status.textContent = "No exact registered cell matches this selection.";
      return;
    }
    const prefix = regime.value;
    const discovery = selected.getAttribute(`data-${prefix}-discovery`);
    setMetric("strategy", selected.dataset.privateR);
    setMetric("posterior", selected.dataset.agreementPosterior);
    setMetric("shared-action", selected.dataset.sharedX);
    setMetric("discovery", discovery);
    setMetric("payoff", selected.getAttribute(`data-${prefix}-payoff`));
    setMetric("collision", selected.getAttribute(`data-${prefix}-collision`));
    setMetric("diversity", selected.getAttribute(`data-${prefix}-diversity`));
    setMetric("quality", selected.getAttribute(`data-${prefix}-quality`));
    setMetric("gap", selected.getAttribute(`data-${prefix}-gap`));
    const gain = prefix === baseline.value
      ? "0"
      : selected.getAttribute(`data-${prefix}-minus-${baseline.value}`);
    setMetric("gain", gain);
    ["private-regime", "shared-regime"].forEach((key) => {
      const target = lab.querySelector(`[data-coordination-text="${key}"]`);
      if (target) target.textContent = selected.getAttribute(`data-${key}`);
    });
    const sameAccuracy = rows.filter((row) => row.dataset.accuracy === accuracy.value);
    const points = Array.from(lab.querySelectorAll("[data-coordination-point]"));
    points.forEach((point) => {
      const row = sameAccuracy.find((candidate) => candidate.dataset.dependence === point.dataset.rho);
      if (!row) return;
      const privateValue = row.dataset.privateDiscovery;
      const sharedValue = row.dataset.sharedDiscovery;
      point.classList.toggle("selected", point.dataset.rho === dependence.value);
      const privateBar = point.querySelector("[data-coordination-private-bar]");
      const sharedBar = point.querySelector("[data-coordination-shared-bar]");
      const value = point.querySelector("[data-coordination-value]");
      if (privateBar) privateBar.style.setProperty("--profile-value", percentage(privateValue));
      if (sharedBar) sharedBar.style.setProperty("--profile-value", percentage(sharedValue));
      if (value) value.textContent = `P ${percentage(privateValue)} · S ${percentage(sharedValue)}`;
    });
    const chart = lab.querySelector("[data-coordination-chart]");
    if (chart) chart.setAttribute("aria-label", `Private and shared exact discovery across registered rho values for p=${accuracy.value}.`);
    const summary = lab.querySelector("[data-coordination-regime-summary]");
    if (summary) summary.textContent = `Private: ${selected.dataset.privateRegime}; shared agreement: ${selected.dataset.sharedRegime}; selected gain ${percentage(selected.dataset.selectedGain)}; gap to V2 ${percentage(selected.getAttribute(`data-${prefix}-gap`))}.`;
    status.textContent = `p=${accuracy.value}, rho=${dependence.value}, ${regime.value} regime versus ${baseline.value} baseline; selected sharing class ${selected.dataset.gainClass}.`;
  };
  [accuracy, dependence, regime, baseline].forEach((control) => control.addEventListener("change", render));
  if (reset) reset.addEventListener("click", () => {
    accuracy.value = "3/5";
    dependence.value = "1/2";
    regime.value = "private";
    baseline.value = "direct";
    render();
  });
  render();
});

document.querySelectorAll("[data-treasure-module]").forEach((module) => {
  const choice = module.querySelector("[data-treasure-choice]");
  const output = module.querySelector("[data-treasure-output]");
  if (!choice || !output) return;
  const render = () => {
    const option = choice.options[choice.selectedIndex];
    output.textContent = option?.dataset.outcome || "No registered implication.";
  };
  choice.addEventListener("change", render);
  render();
});
