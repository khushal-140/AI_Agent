/* AI Travel Agent front-end: chat, trip sidebar, tool activity. */

const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const typing = document.getElementById("typing");
const tripDetails = document.getElementById("tripDetails");
const toolActivity = document.getElementById("toolActivity");
const itineraryBtn = document.getElementById("itineraryBtn");
const resetBtn = document.getElementById("resetBtn");

const TOOL_ICONS = {
  weather: "🌤️",
  budget: "💰",
  hotel: "🏨",
  flight: "✈️",
  maps: "🗺️",
  currency: "💱",
};

const FIELD_LABELS = {
  name: "Name",
  destination: "Destination",
  origin: "Origin",
  days: "Days",
  budget: "Budget",
  travelers: "Travelers",
  transport: "Transport",
};

/* ---------- helpers ---------- */

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatReply(text) {
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\n/g, "<br>");
  return html;
}

function formatMoney(value) {
  const number = Number(value);
  if (!isFinite(number)) return "—";
  return "₹" + number.toLocaleString("en-IN");
}

function appendMessage(role, html, extraClass) {
  const div = document.createElement("div");
  div.className = `msg ${role}${extraClass ? " " + extraClass : ""}`;
  div.innerHTML = html;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setBusy(busy) {
  typing.classList.toggle("hidden", !busy);
  messageInput.disabled = busy;
  sendBtn.disabled = busy;
}

/* ---------- sidebar ---------- */

function updateTripDetails(memory) {
  if (!memory) return;
  tripDetails.innerHTML = "";
  for (const [field, label] of Object.entries(FIELD_LABELS)) {
    const li = document.createElement("li");
    const name = document.createElement("span");
    name.textContent = label;
    const value = document.createElement("span");
    let display = memory[field];
    if (field === "budget" && display) display = formatMoney(display);
    value.textContent = display ?? "—";
    li.appendChild(name);
    li.appendChild(value);
    tripDetails.appendChild(li);
  }
}

function renderToolActivity(activity) {
  toolActivity.innerHTML = "";
  if (!activity || activity.length === 0) {
    toolActivity.innerHTML =
      '<p class="muted">No tools were needed for this request.</p>';
    return;
  }
  for (const item of activity) {
    const chip = document.createElement("div");
    chip.className = `tool-chip ${item.status === "success" ? "ok" : "fail"}`;
    const icon = TOOL_ICONS[item.tool] || "🔧";
    const label = document.createElement("span");
    label.innerHTML = `${icon} <strong>${escapeHtml(item.tool)}</strong>`;
    const status = document.createElement("span");
    status.className = "tool-status";
    status.textContent = item.status === "success" ? "✓ done" : "✗ failed";
    chip.appendChild(label);
    chip.appendChild(status);
    if (item.error) {
      const error = document.createElement("small");
      error.textContent = item.error;
      chip.appendChild(error);
    }
    toolActivity.appendChild(chip);
  }
}

/* ---------- chat ---------- */

async function sendMessage(text) {
  appendMessage("user", escapeHtml(text));
  setBusy(true);
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await response.json();
    setBusy(false);

    if (data.memory) updateTripDetails(data.memory);
    renderToolActivity(data.tool_activity || []);

    if (data.status === "complete") {
      appendMessage("ai", formatReply(data.reply || "Your plan is ready!"));
      itineraryBtn.classList.remove("hidden");
    } else if (data.status === "need_info") {
      appendMessage("ai", formatReply(data.reply || ""));
    } else {
      appendMessage(
        "ai",
        formatReply(data.reply || "Something went wrong. Please try again."),
        "error"
      );
    }
  } catch (error) {
    setBusy(false);
    appendMessage(
      "ai",
      "⚠️ Network error — please check your connection and try again.",
      "error"
    );
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;
  messageInput.value = "";
  sendMessage(text);
});

resetBtn.addEventListener("click", async () => {
  try {
    await fetch("/reset", { method: "POST" });
  } finally {
    location.reload();
  }
});

/* ---------- welcome message ---------- */

appendMessage(
  "ai",
  "Hi! I'm your <strong>AI Travel Agent</strong> 🌏 Tell me about your trip — " +
    "for example: <em>“I am Khushal and I want to visit Goa for 4 days with my " +
    "family. Our budget is ₹30,000 and we are 4 people travelling by flight.”</em>"
);
