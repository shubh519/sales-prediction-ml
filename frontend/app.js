const fileInput = document.getElementById("csvFile");
const inspectBtn = document.getElementById("inspectBtn");
const forecastBtn = document.getElementById("forecastBtn");
const inspectStatus = document.getElementById("inspectStatus");
const columnOptions = document.getElementById("columnOptions");
const dateSelect = document.getElementById("dateColumn");
const salesSelect = document.getElementById("salesColumn");
let latestResult = null;
let chart = null;

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  document.getElementById("fileLabel").textContent = file ? file.name : "Choose a CSV file";
  inspectBtn.disabled = !file;
  columnOptions.classList.add("hidden");
  document.getElementById("results").classList.add("hidden");
  inspectStatus.textContent = "";
});

function setMessage(message, error=false) {
  inspectStatus.textContent = message;
  inspectStatus.classList.toggle("error", error);
}
function addOptions(select, columns, selected) {
  select.innerHTML = "";
  columns.forEach(column => {
    const option = document.createElement("option");
    option.value = column;
    option.textContent = column;
    option.selected = column === selected;
    select.appendChild(option);
  });
}
async function parseResponse(response) {
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Request failed.");
  return data;
}
inspectBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  inspectBtn.disabled = true;
  setMessage("Inspecting CSV…");
  try {
    const form = new FormData(); form.append("file", file);
    const data = await parseResponse(await fetch("/api/inspect", {method:"POST", body:form}));
    addOptions(dateSelect, data.columns, data.suggested_date_column);
    addOptions(salesSelect, data.columns, data.suggested_sales_column);
    columnOptions.classList.remove("hidden");
    setMessage(`Found ${data.rows.toLocaleString()} rows and ${data.columns.length} columns. Confirm the suggested fields.`);
  } catch (err) {
    setMessage(err.message, true);
  } finally { inspectBtn.disabled = false; }
});
forecastBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  forecastBtn.disabled = true;
  forecastBtn.textContent = "Training model…";
  setMessage("Training and evaluating the model…");
  try {
    const form = new FormData();
    form.append("file", file);
    form.append("date_column", dateSelect.value);
    form.append("sales_column", salesSelect.value);
    form.append("periods", document.getElementById("periods").value);
    latestResult = await parseResponse(await fetch("/api/forecast", {method:"POST", body:form}));
    renderResults(latestResult);
    setMessage("Forecast generated successfully.");
    document.getElementById("results").classList.remove("hidden");
    document.getElementById("results").scrollIntoView({behavior:"smooth", block:"start"});
  } catch (err) {
    setMessage(err.message, true);
  } finally {
    forecastBtn.disabled = false;
    forecastBtn.innerHTML = 'Train and forecast <span>→</span>';
  }
});
function fmt(value) {
  return value === null || value === undefined || !Number.isFinite(Number(value))
    ? "N/A" : Number(value).toLocaleString(undefined, {maximumFractionDigits:2});
}
function renderResults(result) {
  document.getElementById("mae").textContent = fmt(result.metrics.mae);
  document.getElementById("rmse").textContent = fmt(result.metrics.rmse);
  document.getElementById("r2").textContent = fmt(result.metrics.r2);
  document.getElementById("observations").textContent = result.observations;
  document.getElementById("modelLabel").textContent = result.model;
  document.getElementById("limitations").textContent = result.limitations.join(" ");
  const tbody = document.getElementById("forecastRows");
  tbody.innerHTML = "";
  result.forecast.forEach(row => {
    const tr = document.createElement("tr");
    const month = document.createElement("td"); month.textContent = row.month;
    const value = document.createElement("td"); value.textContent = fmt(row.predicted_sales);
    tr.append(month, value); tbody.appendChild(tr);
  });
  const labels = [...result.history.map(x=>x.month), ...result.forecast.map(x=>x.month)];
  const actual = [...result.history.map(x=>x.sales), ...result.forecast.map(()=>null)];
  const predicted = [...result.history.map(()=>null), ...result.forecast.map(x=>x.predicted_sales)];
  const ctx = document.getElementById("salesChart").getContext("2d");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type:"line",
    data:{labels, datasets:[
      {label:"Historical sales", data:actual, borderColor:"#3158d4", backgroundColor:"rgba(49,88,212,.10)", fill:true, tension:.25, pointRadius:2, spanGaps:false},
      {label:"Forecast", data:predicted, borderColor:"#17a68a", backgroundColor:"rgba(23,166,138,.08)", borderDash:[6,4], fill:false, tension:.25, pointRadius:3, spanGaps:false}
    ]},
    options:{responsive:true, maintainAspectRatio:false, interaction:{mode:"index", intersect:false},
      plugins:{legend:{position:"bottom"}, tooltip:{callbacks:{label:(context)=>`${context.dataset.label}: ${fmt(context.raw)}`}}},
      scales:{x:{grid:{display:false},ticks:{maxTicksLimit:12}},y:{beginAtZero:true, title:{display:true,text:"Sales"}}}}
  });
}
document.getElementById("downloadBtn").addEventListener("click", () => {
  if (!latestResult) return;
  const rows = [["month","predicted_sales"], ...latestResult.forecast.map(x=>[x.month,x.predicted_sales])];
  const csv = rows.map(row=>row.map(v=>`"${String(v).replaceAll('"','""')}"`).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob([csv], {type:"text/csv;charset=utf-8;"}));
  const a = document.createElement("a"); a.href=url; a.download="sales_forecast.csv"; a.click(); URL.revokeObjectURL(url);
});
