function generateCode() {
    let code = 'TC-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    document.getElementById('track_code').value = code;
}

// JavaScript function to display flash messages as a pop-up
document.addEventListener("DOMContentLoaded", function() {
    const popup = document.querySelector(".popup");
    if (popup && popup.textContent.trim()) {
        popup.style.display = "block"; // Show the popup
        setTimeout(() => {
            popup.style.display = "none"; // Hide after 3 seconds
        }, 3000); // 3000 ms = 3 seconds
    }
});

document.getElementById('clear-btn').addEventListener('click', function() {
    window.location.href = "{{ url_for('auth.doc_tracker') }}";
});

document.getElementById('clear-btn').addEventListener('click', function() {
    window.location.href = clearUrl;
});

// Define the order for sorting statuses
const statusOrder = { "Pending": 1, "Transfer": 2, "Completed": 3 };

// Filter rows based on the selected status
function filterRows(filterValue) {
    const rows = document.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const status = row.querySelector(".status")?.textContent.trim() || "";
        row.style.display = (filterValue === "all" || status === filterValue) ? "" : "none"; // Show/hide rows
    });
}

// Sort rows based on the status column
function sortTableByStatus() {
    const rows = Array.from(document.querySelectorAll("tbody tr"));
    const tbody = document.querySelector("tbody");

    // Sort rows based on status order
    const sortedRows = rows.sort((a, b) => {
        const statusA = a.querySelector(".status")?.textContent.trim() || "";
        const statusB = b.querySelector(".status")?.textContent.trim() || "";
        return (statusOrder[statusA] || Infinity) - (statusOrder[statusB] || Infinity);
    });

    // Append sorted rows back to the table body
    sortedRows.forEach(row => tbody.appendChild(row));
}

// Combine filtering and sorting into one function
function filterAndSort() {
    const filterValue = document.getElementById("statusFilter").value;
    filterRows(filterValue); // Apply filtering
    sortTableByStatus(); // Apply sorting
}

// Trigger the default sorting when the page loads
window.onload = () => {
    sortTableByStatus(); // Sort the table by default
};

document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.getElementById('date_time');
    const today = new Date();

    // Format the date to YYYY-MM-DD
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const dd = String(today.getDate()).padStart(2, '0');

    dateInput.value = `${yyyy}-${mm}-${dd}`; // Set the current date
});
