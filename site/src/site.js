document.documentElement.classList.add("js");

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

document.querySelectorAll("[data-audience-lab]").forEach((lab) => {
  const n = lab.querySelector("#audience-n");
  const p = lab.querySelector("#audience-p");
  const q = lab.querySelector("#audience-q");
  const g = lab.querySelector("#audience-g");
  const m = lab.querySelector("#audience-m");
  const status = lab.querySelector("#audience-status");
  const bindingRows = Array.from(document.querySelectorAll("tr[data-audience-row]"));
  const garblingRows = Array.from(document.querySelectorAll("tr[data-garbling-row]"));
  if (!n || !p || !q || !g || !m || !status) return;
  const render = () => {
    let bindingVisible = 0;
    let garblingVisible = 0;
    bindingRows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.m === m.value;
      row.hidden = !show;
      if (show) bindingVisible += 1;
    });
    garblingRows.forEach((row) => {
      const show = row.dataset.n === n.value && row.dataset.p === p.value &&
        row.dataset.q === q.value && row.dataset.g === g.value && row.dataset.m === m.value;
      row.hidden = !show;
      if (show) garblingVisible += 1;
    });
    status.textContent = `Showing ${bindingVisible} binding row and ${garblingVisible} feasible garbling row${garblingVisible === 1 ? "" : "s"}. A zero garbling count means g>q or audience zero is outside the positive-audience garbling registry.`;
  };
  [n, p, q, g, m].forEach((control) => control.addEventListener("change", render));
  n.value = "2";
  p.value = "1/3";
  q.value = "1/2";
  g.value = "1/3";
  m.value = "1";
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
