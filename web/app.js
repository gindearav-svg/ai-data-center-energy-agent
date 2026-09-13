const form = document.querySelector("#query-form");
const button = document.querySelector("#submit-button");
const status = document.querySelector("#status");
const results = document.querySelector("#results");

const scenarioForm = document.querySelector("#scenario-form");
const scenarioButton = document.querySelector("#scenario-button");
const scenarioStatus = document.querySelector("#scenario-status");
const scenarioResults = document.querySelector("#scenario-results");

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
    `${number.format(
      summary.recommended_annual_emissions_metric_tons_co2e
    )} metric tons CO₂e`
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

  // Model-generated wording is displayed as text, never interpreted as HTML.
  setText("#raw-answer", data.model_draft ?? "");
  setText(
    "#answer-source",
    "Decision figures and rationale are assembled from analysis tools. " +
      "The expandable model draft has not been fully verified."
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

function displayScenarioResults(data) {
  const regions = data.regional_results;

  if (!regions.length) {
    throw new Error("The comparison returned no regions.");
  }

  const winner = regions.find(
    (region) => region.region === data.recommendation.region
  );

  if (!winner) {
    throw new Error("The recommended region is missing from the results.");
  }

  const cheapest = regions.reduce((best, region) =>
    region.estimated_annual_wholesale_cost_usd <
    best.estimated_annual_wholesale_cost_usd
      ? region
      : best
  );

  const mostStable = regions.reduce((best, region) =>
    region.price_risk_score > best.price_risk_score ? region : best
  );

  const scenarioName = data.scenario.replaceAll("_", " ");
  setText(
    "#scenario-winner",
    `${winner.region} ranks first for the ${scenarioName} scenario`
  );
  setText(
    "#scenario-weights",
    `Weights: cost ${number.format(data.weights.cost * 100)}%, ` +
      `carbon ${number.format(data.weights.carbon * 100)}%, ` +
      `price risk ${number.format(data.weights.price_risk * 100)}%.`
  );

  const costPremium =
    winner.estimated_annual_wholesale_cost_usd -
    cheapest.estimated_annual_wholesale_cost_usd;

  const costExplanation =
    costPremium > 0
      ? `${cheapest.region} costs ${money.format(costPremium)} less per year.`
      : `${winner.region} has the lowest estimated annual wholesale cost.`;

  setText(
    "#scenario-summary",
    `${winner.region} scores ${winner.overall_score} / 100. ` +
      `${costExplanation} ${mostStable.region} has the highest relative ` +
      `price-stability score (${mostStable.price_risk_score} / 100).`
  );

  const rows = document.querySelector("#scenario-rows");
  rows.replaceChildren();

  for (const region of regions) {
    const row = document.createElement("tr");
    const values = [
      region.rank,
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

  const sameEmissions = regions.every(
    (region) =>
      Math.abs(
        region.estimated_annual_emissions_metric_tons_co2e -
          regions[0].estimated_annual_emissions_metric_tons_co2e
      ) < 0.001
  );

  setText(
    "#scenario-limitation",
    (sameEmissions
      ? "All listed regions have the same modeled emissions. The " +
        "carbon-focused ranking does not establish that its winner " +
        "has a cleaner local electricity supply. "
      : "") +
      "Price-stability scores compare these candidates; they do not " +
      "measure grid uptime or imply zero volatility. Costs are " +
      "wholesale electricity estimates, not final electricity bills."
  );

  scenarioResults.hidden = false;
}

// These are two separate listeners. Neither is nested inside the other.
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

scenarioForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  scenarioResults.hidden = true;
  scenarioStatus.classList.remove("error");
  scenarioStatus.textContent = "Comparing regions...";
  scenarioButton.disabled = true;

  try {
    const response = await fetch("/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        it_load_mw: Number(
          document.querySelector("#scenario-it-load").value
        ),
        pue: Number(document.querySelector("#scenario-pue").value),
        utilization: Number(
          document.querySelector("#scenario-utilization").value
        ),
        scenario: document.querySelector("#scenario-choice").value,
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

    displayScenarioResults(data);
    scenarioStatus.textContent = "Comparison complete.";
  } catch (error) {
    scenarioStatus.classList.add("error");
    scenarioStatus.textContent = `Comparison failed: ${error.message}`;
  } finally {
    scenarioButton.disabled = false;
  }
});