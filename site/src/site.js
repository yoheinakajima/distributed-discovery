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
