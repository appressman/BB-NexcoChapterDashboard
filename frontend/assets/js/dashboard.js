// neXco Chapter Dashboard JavaScript

const DashboardState = {
    data: null,
    selectedMonth: null,
    chart: null,
    isRefreshing: false
};

// Data Loading
async function loadDashboardData() {
    // Add cache-busting parameter for manual refresh
    const cacheBuster = DashboardState.isRefreshing ? `?_=${Date.now()}` : '';
    const response = await fetch(`data.json${cacheBuster}`);
    if (!response.ok) {
        throw new Error(`Failed to load data: ${response.status}`);
    }
    return response.json();
}

// Manual Refresh
async function refreshDashboard() {
    if (DashboardState.isRefreshing) return;

    const refreshBtn = document.getElementById("refresh-btn");
    const refreshIcon = refreshBtn.querySelector(".refresh-icon");

    try {
        DashboardState.isRefreshing = true;
        refreshBtn.disabled = true;
        refreshIcon.classList.add("spinning");

        // Reload data
        DashboardState.data = await loadDashboardData();

        // Update UI
        updatePageTitle();
        checkStaleData();

        // Re-initialize month selector (preserving current selection if valid)
        const currentMonth = DashboardState.selectedMonth;
        initMonthSelector();

        // Try to stay on the same month if it's still available
        if (currentMonth && DashboardState.data.available_months.includes(currentMonth)) {
            DashboardState.selectedMonth = currentMonth;
            if (supportsMonthInput()) {
                document.getElementById("month-picker").value = currentMonth;
            } else {
                const [year, month] = currentMonth.split("-");
                document.getElementById("year-select").value = year;
                document.getElementById("month-select").value = month;
            }
            renderForMonth(currentMonth);
        }

        // Re-render static widgets
        renderFollowUpWidget();
        renderOpenSeats();

        // Show success feedback
        showRefreshSuccess();

    } catch (error) {
        showError("Failed to refresh dashboard data. Please try again.");
        console.error("Refresh error:", error);
    } finally {
        DashboardState.isRefreshing = false;
        refreshBtn.disabled = false;
        refreshIcon.classList.remove("spinning");
    }
}

function showRefreshSuccess() {
    const notice = document.getElementById("status-notice");
    notice.textContent = "Dashboard data refreshed successfully!";
    notice.classList.remove("error", "hidden");
    notice.classList.add("success");

    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (notice.classList.contains("success")) {
            notice.classList.add("hidden");
            notice.classList.remove("success");
        }
    }, 3000);
}

// Initialization
async function initDashboard() {
    try {
        DashboardState.data = await loadDashboardData();
        updatePageTitle();
        checkStaleData();
        initChart();
        initMonthSelector();
        initTableFilters();
        initRefreshButton();
        renderFollowUpWidget();
        renderOpenSeats();
    } catch (error) {
        showError("Failed to load dashboard data. Please try again later.");
        console.error("Dashboard initialization error:", error);
    }
}

function initRefreshButton() {
    const refreshBtn = document.getElementById("refresh-btn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", refreshDashboard);
    }
}

function updatePageTitle() {
    document.getElementById("page-title").textContent = DashboardState.data.metadata.page_title;
    document.title = DashboardState.data.metadata.page_title;
}

function formatLastUpdated(isoString) {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat("en-US", {
        timeZone: "America/New_York",
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true
    }).format(date) + " ET";
}

function checkStaleData() {
    const lastUpdated = new Date(DashboardState.data.metadata.last_updated);
    const now = new Date();
    const daysDiff = (now - lastUpdated) / (1000 * 60 * 60 * 24);

    const warning = document.getElementById("stale-warning");
    if (daysDiff > 8) {
        warning.textContent = "Data may be stale (last updated more than 8 days ago)";
        warning.classList.remove("hidden");
    } else {
        warning.classList.add("hidden");
    }

    document.getElementById("last-updated").textContent =
        "Last updated: " + formatLastUpdated(DashboardState.data.metadata.last_updated);
}

function showError(message) {
    const notice = document.getElementById("status-notice");
    notice.textContent = message;
    notice.classList.add("error");
    notice.classList.remove("hidden", "success");
}

// Month Selector
function supportsMonthInput() {
    const input = document.createElement("input");
    input.setAttribute("type", "month");
    return input.type === "month";
}

function initMonthSelector() {
    const availableMonths = DashboardState.data.available_months;

    if (!availableMonths || availableMonths.length === 0) {
        showError("No historical meeting data available");
        return;
    }

    DashboardState.selectedMonth = availableMonths[0];

    // Always use custom dropdowns for consistent UX across browsers
    initFallbackDropdowns(availableMonths);

    renderForMonth(DashboardState.selectedMonth);
}

function initNativeMonthPicker(availableMonths) {
    const picker = document.getElementById("month-picker");
    document.getElementById("month-fallback").classList.add("hidden");

    const years = [...new Set(availableMonths.map(m => m.split("-")[0]))];
    picker.min = `${Math.min(...years)}-01`;
    picker.max = availableMonths[0];
    picker.value = DashboardState.selectedMonth;

    picker.addEventListener("change", handleMonthChange);
}

function initFallbackDropdowns(availableMonths) {
    document.getElementById("month-picker").classList.add("hidden");
    document.getElementById("month-fallback").classList.remove("hidden");

    const monthSelect = document.getElementById("month-select");
    const yearSelect = document.getElementById("year-select");

    // Clear existing options
    monthSelect.innerHTML = "";
    yearSelect.innerHTML = "";

    const monthNames = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"];
    monthNames.forEach((name, i) => {
        const opt = document.createElement("option");
        opt.value = String(i + 1).padStart(2, "0");
        opt.textContent = name;
        monthSelect.appendChild(opt);
    });

    // Get years from available data only (not arbitrary range)
    const yearsWithData = [...new Set(availableMonths.map(m => m.split("-")[0]))].sort((a, b) => b - a);
    yearsWithData.forEach(year => {
        const opt = document.createElement("option");
        opt.value = year;
        opt.textContent = year;
        yearSelect.appendChild(opt);
    });

    const [year, month] = DashboardState.selectedMonth.split("-");
    yearSelect.value = year;
    monthSelect.value = month;

    monthSelect.addEventListener("change", handleFallbackChange);
    yearSelect.addEventListener("change", handleFallbackChange);
}

function handleFallbackChange() {
    const month = document.getElementById("month-select").value;
    const year = document.getElementById("year-select").value;
    handleMonthChange({ target: { value: `${year}-${month}` }});
}

function handleMonthChange(event) {
    const selectedMonth = event.target.value;
    const availableMonths = DashboardState.data.available_months;

    if (!availableMonths.includes(selectedMonth)) {
        const validMonth = availableMonths[0];
        DashboardState.selectedMonth = validMonth;

        const notice = document.getElementById("status-notice");
        notice.textContent = `No historical meetings in ${formatMonthDisplay(selectedMonth)} — showing ${formatMonthDisplay(validMonth)} instead.`;
        notice.classList.remove("hidden", "success");

        if (supportsMonthInput()) {
            document.getElementById("month-picker").value = validMonth;
        } else {
            const [year, month] = validMonth.split("-");
            document.getElementById("year-select").value = year;
            document.getElementById("month-select").value = month;
        }
    } else {
        DashboardState.selectedMonth = selectedMonth;
        document.getElementById("status-notice").classList.add("hidden");
    }

    renderForMonth(DashboardState.selectedMonth);
}

function formatMonthDisplay(monthKey) {
    const [year, month] = monthKey.split("-");
    const date = new Date(year, parseInt(month) - 1, 1);
    return new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric" }).format(date);
}

// Chart
function initChart() {
    const ctx = document.getElementById("attendance-chart").getContext("2d");

    DashboardState.chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: [],
            datasets: [
                { label: "Attended", data: [], backgroundColor: "#d0a848", stack: "stack0" },
                { label: "No-Show", data: [], backgroundColor: "#9ca3af", stack: "stack0" }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        afterBody: function(tooltipItems) {
                            const dataIndex = tooltipItems[0]?.dataIndex;
                            if (dataIndex === undefined) return "";
                            const attended = DashboardState.chart.data.datasets[0].data[dataIndex] || 0;
                            const noShow = DashboardState.chart.data.datasets[1].data[dataIndex] || 0;
                            return `Attended: ${attended}, No-Show: ${noShow}`;
                        }
                    }
                }
            },
            scales: {
                x: { stacked: true, grid: { display: false } },
                y: { stacked: true, beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
}

function updateChart(monthKey) {
    const meetings = DashboardState.data.meetings.filter(m => m.month_key === monthKey);
    meetings.sort((a, b) => new Date(b.date) - new Date(a.date));

    const labels = meetings.map(m => m.display_date);
    const attendedData = meetings.map(m => m.attended_count);
    const noShowData = meetings.map(m => m.no_show_count);

    DashboardState.chart.data.labels = labels;
    DashboardState.chart.data.datasets[0].data = attendedData;
    DashboardState.chart.data.datasets[1].data = noShowData;
    DashboardState.chart.update();
}

// Tables
function renderGuestTable(tableId, guests, filterId) {
    const table = document.getElementById(tableId);
    const headers = ["Guest Name", "Company", "Email", "Referring Member", "Who's Following Up", "Meeting Date", "Notes"];

    let html = "<thead><tr>";
    headers.forEach(h => html += `<th>${h}</th>`);
    html += "</tr></thead><tbody>";

    guests.forEach(guest => {
        const nameWithBadge = guest.flags && guest.flags.includes("missing_guest_tracker")
            ? `${guest.name} <span class="badge warning">Missing in Guest Tracker</span>`
            : guest.name;

        html += "<tr>";
        html += `<td>${nameWithBadge}</td>`;
        html += `<td>${escapeHtml(guest.company || "")}</td>`;
        html += `<td>${escapeHtml(guest.email || "")}</td>`;
        html += `<td>${escapeHtml(guest.referring_member || "")}</td>`;
        html += `<td>${escapeHtml(guest.following_up || "")}</td>`;
        html += `<td>${guest.display_date}</td>`;
        html += `<td>${escapeHtml(guest.notes || "")}</td>`;
        html += "</tr>";
    });

    html += "</tbody>";
    table.innerHTML = html;
    table.dataset.guests = JSON.stringify(guests);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function initTableFilters() {
    const filterConfigs = [
        { filterId: "attended-filter", tableId: "attended-table" },
        { filterId: "no-show-filter", tableId: "no-show-table" },
        { filterId: "without-rsvp-filter", tableId: "without-rsvp-table" }
    ];

    filterConfigs.forEach(({ filterId, tableId }) => {
        const filter = document.getElementById(filterId);
        filter.addEventListener("input", () => handleFilter(filterId, tableId));
    });
}

function handleFilter(filterId, tableId) {
    const filterValue = document.getElementById(filterId).value;
    const table = document.getElementById(tableId);
    const guests = JSON.parse(table.dataset.guests || "[]");
    const filtered = filterGuests(guests, filterValue);
    renderFilteredTable(tableId, filtered);
}

function filterGuests(guests, query) {
    if (!query.trim()) return guests;
    const terms = parseFilterTerms(query);
    return guests.filter(guest => {
        const searchText = [guest.name, guest.following_up, guest.display_date, guest.referring_member].join(" ").toLowerCase();
        return terms.every(term => searchText.includes(term.toLowerCase()));
    });
}

function parseFilterTerms(query) {
    const terms = [];
    const regex = /["'"]([^"'"]+)["'"]|(\S+)/g;
    let match;
    while ((match = regex.exec(query)) !== null) {
        terms.push(match[1] || match[2]);
    }
    return terms;
}

function renderFilteredTable(tableId, guests) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    let html = "";
    guests.forEach(guest => {
        const nameWithBadge = guest.flags && guest.flags.includes("missing_guest_tracker")
            ? `${guest.name} <span class="badge warning">Missing in Guest Tracker</span>`
            : guest.name;

        html += "<tr>";
        html += `<td>${nameWithBadge}</td>`;
        html += `<td>${escapeHtml(guest.company || "")}</td>`;
        html += `<td>${escapeHtml(guest.email || "")}</td>`;
        html += `<td>${escapeHtml(guest.referring_member || "")}</td>`;
        html += `<td>${escapeHtml(guest.following_up || "")}</td>`;
        html += `<td>${guest.display_date}</td>`;
        html += `<td>${escapeHtml(guest.notes || "")}</td>`;
        html += "</tr>";
    });

    tbody.innerHTML = html;
}

// Widgets
function renderRsvpCounts(monthKey) {
    const list = document.getElementById("rsvp-counts-list");
    const meetings = DashboardState.data.meetings.filter(m => m.month_key === monthKey);
    meetings.sort((a, b) => new Date(b.date) - new Date(a.date));

    let html = "";
    meetings.forEach(meeting => {
        html += `<li><strong>${meeting.display_date}</strong>: ${meeting.rsvp_count} RSVPs</li>`;
    });

    if (meetings.length === 0) {
        html = "<li>No meetings in selected month</li>";
    }

    list.innerHTML = html;
}

function renderFollowUpWidget() {
    const list = document.getElementById("followup-list");
    const counts = DashboardState.data.follow_up_counts || [];

    let html = "";
    counts.forEach(item => {
        let className = "";
        if (item.is_section_header) {
            // Render as a section header
            html += `<li class="section-header"><strong>${escapeHtml(item.name)}</strong> (${item.count} total)</li>`;
        } else {
            if (item.is_special) className = "special";
            if (item.is_raw_token) className = "raw-token";
            html += `<li class="${className}"><strong>${escapeHtml(item.name)}</strong>: ${item.count}</li>`;
        }
    });

    if (counts.length === 0) {
        html = "<li>No follow-up data available</li>";
    }

    list.innerHTML = html;
}

function renderOpenSeats() {
    const table = document.getElementById("open-seats-table");
    const seats = DashboardState.data.open_seats || [];

    if (seats.length === 0) {
        table.innerHTML = "<tr><td>No open seats data available</td></tr>";
        return;
    }

    const headers = Object.keys(seats[0]);
    let html = "<thead><tr>";
    headers.forEach(h => html += `<th>${escapeHtml(h)}</th>`);
    html += "</tr></thead><tbody>";

    seats.forEach(row => {
        html += "<tr>";
        headers.forEach(h => html += `<td>${escapeHtml(row[h] || "")}</td>`);
        html += "</tr>";
    });

    html += "</tbody>";
    table.innerHTML = html;
}

function renderGuestTables(monthKey) {
    const guests = DashboardState.data.guests || { attended: [], no_show: [], without_rsvp: [] };
    const filterByMonth = (list) => (list || []).filter(g => g.meeting_date && g.meeting_date.substring(0, 7) === monthKey);

    renderGuestTable("attended-table", filterByMonth(guests.attended), "attended-filter");
    renderGuestTable("no-show-table", filterByMonth(guests.no_show), "no-show-filter");
    renderGuestTable("without-rsvp-table", filterByMonth(guests.without_rsvp), "without-rsvp-filter");
}

function renderForMonth(monthKey) {
    updateChart(monthKey);
    renderRsvpCounts(monthKey);
    renderGuestTables(monthKey);
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", initDashboard);
