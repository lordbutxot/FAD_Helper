// Simple table sorting for FAD_Helper tables
// Usage: add class 'sortable' to your <table>, and 'sortable-col' to <th> you want sortable
// Optionally, add data-sort-key to <th> for custom sort keys

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('table.sortable').forEach(function(table) {
        table.querySelectorAll('th.sortable-col').forEach(function(header, colIndex) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, colIndex, header);
            });
        });
    });
});

function sortTable(table, colIndex, header) {
    var tbody = table.tBodies[0];
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var asc = !header.classList.contains('sorted-asc');
    // Remove sort classes from all headers
    table.querySelectorAll('th').forEach(function(th) {
        th.classList.remove('sorted-asc', 'sorted-desc');
    });
    header.classList.add(asc ? 'sorted-asc' : 'sorted-desc');
    rows.sort(function(a, b) {
        var aKey = getSortKey(a.cells[colIndex]);
        var bKey = getSortKey(b.cells[colIndex]);
        if (!isNaN(parseFloat(aKey)) && !isNaN(parseFloat(bKey))) {
            return asc ? aKey - bKey : bKey - aKey;
        }
        return asc ? aKey.localeCompare(bKey) : bKey.localeCompare(aKey);
    });
    rows.forEach(function(row) { tbody.appendChild(row); });
}

function getSortKey(cell) {
    var key = cell.getAttribute('data-sort-key');
    if (key !== null) return key;
    // Prefer textContent, fallback to innerText
    return (cell.textContent || cell.innerText).trim().toLowerCase();
}
