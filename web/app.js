const form = document.querySelector("#query-form");
const button = document.querySelector("#submit-button");
const status = document.querySelector("#status");
const results = document.querySelector("#results");

const number = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function setText(selector, value) {
  document.querySelector(selector).textContent = value;
}

function displayResults(data) {
  const summary = data.grounded_summary;

  setText("#region", summary.recommended_region);
  setText("#facility-load", `${number.format(summary.facility_load_mw)} MW`);
  setText("#annual-energy", `${number.format(summary.annual_energy_mwh)} MWh`);
  setText("#annual-cost", money.format(summary.recommended_annual_cost_usd));
  setText(
    "#emissions",
    `${number.format(summary.recommended_annual_emissions_metric_tons_co2e)} metric tons CO₂e`
  );
  setText(
    "#overall-score",
    `${summary.recommended_overall_score} / 100`
  );

  const rows = document.querySelector("#regional-rows");
  rows.replaceChildren();

  for (const region of summary.regional_results) {
    const row = document.createElement("tr");
    const values = [
      region.region,
      money.format(region.estimated_annual_wholesale_cost_usd),
      `${number.format(
        region.estimated_annual_emissions_metric_tons_co2e
      )} metric tons CO₂e`,
      `${region.price_risk_score} / 100`,
      `${region.overall_score} / 100`,
    ];

    for (const value of values) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }

    rows.appendChild(row);
  }

  // Display as text, not HTML: model-generated output must not run code.
  const recommended = summary.regional_results.find(
  (region) => region.region === summary.recommended_region
);
const cheapest = summary.regional_results.find(
  (region) => region.region === summary.cheapest_region
);

const tradeoff =
  summary.recommended_cost_premium_usd > 0
    ? `${summary.cheapest_region} costs ${money.format(
        summary.recommended_cost_premium_usd
      )} less annually. ${summary.recommended_region} scores ${
        recommended.price_risk_score
      } / 100 for relative price stability, compared with ${
        cheapest.price_risk_score
      } / 100 for ${summary.cheapest_region}.`
    : `${summary.recommended_region} also has the lowest estimated annual wholesale cost.`;

setText(
  "#answer",
  `${summary.recommended_region} ranks first in the ${summary.scenario.replaceAll(
    "_",
    " "
  )} scenario with an overall score of ${
    summary.recommended_overall_score
  } / 100. ${tradeoff} These stability scores compare the listed regions; they do not measure absolute volatility.`
);

setText("#raw-answer", data.answer);
  setText(
  "#answer-source",
  `Decision figures come from analysis tools. Agent answer source: ${data.answer_source}. Core numerical checks passed: ${data.grounded}.`
);

  const limitations = document.querySelector("#limitations");
  limitations.replaceChildren();

  for (const limitation of summary.limitations) {
    const item = document.createElement("li");
    item.textContent = limitation;
    limitations.appendChild(item);
  }

  results.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  results.hidden = true;
  status.classList.remove("error");
  status.textContent =
    "Analyzing regions. The local model may take a few minutes...";
  button.disabled = true;

  try {
    const response = await fetch("/agent/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: document.querySelector("#message").value,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : `Request failed with status ${response.status}.`
      );
    }

    displayResults(data);
    status.textContent = "Analysis complete.";
  } catch (error) {
    status.classList.add("error");
    status.textContent = `Analysis failed: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});