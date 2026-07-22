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
      const show = matchesFilter && matchesQuery;
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
  render();
});

document.querySelectorAll("[data-lab]").forEach((lab) => {
  const slider = lab.querySelector("input[type=range]");
  const output = lab.querySelector("output");
  const note = lab.querySelector("#lab-note");
  if (!slider || !output || !note) return;
  const name = lab.dataset.lab.replace(/-/g, " ");
  const render = () => {
    output.textContent = slider.value;
    note.textContent = `${name}: precomputed fixture scenario ${slider.value} of ${slider.max}. This control changes no evidence or claim status.`;
  };
  slider.addEventListener("input", render);
  render();
});

document.querySelectorAll("[data-output-lab]").forEach((lab) => {
  const kind = lab.dataset.outputLab;
  const controls = Array.from(lab.querySelectorAll("select[data-filter-key]"));
  const outputs = Array.from(lab.querySelectorAll("[data-output-key]"));
  const status = lab.querySelector("[data-output-status]");
  const rows = Array.from(document.querySelectorAll(`[data-output-row="${kind}"]`));
  if (!kind || !controls.length || !outputs.length || !status || !rows.length) return;
  const render = () => {
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
    const selected = rows.find((row) => controls.every((control) =>
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
    const selection = controls.map((control) => {
      const option = control.options[control.selectedIndex];
      return `${control.previousElementSibling?.textContent || control.dataset.filterKey}: ${option.textContent}`;
    }).join("; ");
    status.textContent = `Showing one exact ${kind.replace(/-/g, " ")} row — ${selection}.`;
  };
  controls.forEach((control) => control.addEventListener("change", render));
  render();
});

document.querySelectorAll("[data-benchmark-lab]").forEach((lab) => {
  const select = lab.querySelector("select");
  const status = lab.querySelector("#benchmark-status");
  const rows = Array.from(document.querySelectorAll("tr[data-task]"));
  if (!select || !status) return;
  const render = () => {
    let visible = 0;
    rows.forEach((row) => {
      const show = select.value === "all" || row.dataset.task === select.value;
      row.hidden = !show;
      if (show) visible += 1;
    });
    status.textContent = `Showing ${visible} exact compatible row${visible === 1 ? "" : "s"}.`;
  };
  select.addEventListener("change", render);
  render();
});

document.querySelectorAll("[data-experiment-lab]").forEach((lab) => {
  const select = lab.querySelector("select");
  const status = lab.querySelector("#experiment-status");
  const rows = Array.from(document.querySelectorAll("tr[data-power-scenario]"));
  if (!select || !status) return;
  const render = () => {
    let visible = 0;
    rows.forEach((row) => {
      const show = select.value === "all" || row.dataset.powerScenario === select.value;
      row.hidden = !show;
      if (show) visible += 1;
    });
    status.textContent = `Showing ${visible} synthetic power row${visible === 1 ? "" : "s"}.`;
  };
  select.addEventListener("change", render);
  render();
});

document.querySelectorAll("[data-attention-lab]").forEach((lab) => {
  const n = lab.querySelector("#attention-n");
  const p = lab.querySelector("#attention-p");
  const q = lab.querySelector("#attention-q");
  const k = lab.querySelector("#attention-k");
  const reward = lab.querySelector("#attention-reward");
  const status = lab.querySelector("#attention-status");
  const rows = Array.from(document.querySelectorAll("tr[data-attention-row]"));
  if (!n || !p || !q || !k || !reward || !status) return;
  const render = () => {
    const validCounts = Array.from(k.options).filter((option) => Number(option.value) <= Number(n.value));
    Array.from(k.options).forEach((option) => { option.hidden = Number(option.value) > Number(n.value); });
    if (!validCounts.some((option) => option.value === k.value)) k.value = validCounts[0].value;
    let visible = 0;
    rows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.k === k.value &&
        row.dataset.reward === reward.value;
      row.hidden = !show;
      if (show) visible += 1;
    });
    status.textContent = `Showing ${visible} exact attention profile and reward row. Ignoring roles do not receive the public clue.`;
  };
  [n, p, q, k, reward].forEach((control) => control.addEventListener("change", render));
  n.value = "4";
  p.value = "1/2";
  q.value = "3/4";
  k.value = "1";
  reward.value = "equal-split";
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
  };
  [n, p, q, use, g, m, mechanism].forEach((control) => control.addEventListener("change", render));
  n.value = "2";
  p.value = "1/3";
  q.value = "1/2";
  use.value = "binding";
  g.value = "1/3";
  m.value = "1";
  mechanism.value = "binding_exclusive_delivery";
  render();
});

document.querySelectorAll("[data-conditional-lab]").forEach((lab) => {
  const n = lab.querySelector("#conditional-n");
  const p = lab.querySelector("#conditional-p");
  const q = lab.querySelector("#conditional-q");
  const policy = lab.querySelector("#conditional-policy");
  const status = lab.querySelector("#conditional-status");
  const rows = Array.from(document.querySelectorAll("tr[data-conditional-row]"));
  if (!n || !p || !q || !policy || !status) return;
  const render = () => {
    const compatible = Array.from(policy.options).filter((option) => option.dataset.n === n.value);
    Array.from(policy.options).forEach((option) => { option.hidden = option.dataset.n !== n.value; });
    if (!compatible.some((option) => option.value === policy.value)) policy.value = compatible[0].value;
    let visible = 0;
    rows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.profile === policy.value;
      row.hidden = !show;
      if (show) visible += 1;
    });
    status.textContent = `Showing ${visible} exact registered profile. Every role observes both clues.`;
  };
  [n, p, q, policy].forEach((control) => control.addEventListener("change", render));
  n.value = "2";
  p.value = "1/3";
  q.value = "1/2";
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
