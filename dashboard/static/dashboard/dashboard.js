// ---- WebSocket live updates ----
document.querySelectorAll('.device-card').forEach(card => {
    const deviceId = card.dataset.deviceId;
    const tbody = card.querySelector('.sensor-table tbody');

    const ws = new WebSocket(`ws://${window.location.host}/ws/device/${deviceId}/`);

    ws.onopen = () => console.log(`✅ WS connected for ${deviceId}`);

    ws.onmessage = (e) => {
        const d = JSON.parse(e.data);

        // Build a new row from the incoming data
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${d.timestamp}</td>
            <td>${d.temperature ?? '-'}</td>
            <td>${d.humidity ?? '-'}</td>
            <td>${d.distance ?? '-'}</td>
            <td>${d.sensor_type}</td>
        `;

        // Highlight alert rows
        if (d.sensor_type === 'motion' || (d.distance !== null && d.distance < 50)) {
            row.classList.add('alert-row');
        }

        // Prepend new row at the top, keep max 10 rows
        tbody.insertBefore(row, tbody.firstChild);
        if (tbody.rows.length > 10) {
            tbody.deleteRow(tbody.rows.length - 1);
        }
    };

    ws.onerror = (e) => console.error(`❌ WS error for ${deviceId}`, e);
    ws.onclose = () => console.log(`🔌 WS closed for ${deviceId}`);
});


// ---- Arm / Disarm button ----
document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", async (e) => {
        if (!e.target.classList.contains("arm-btn")) return;

        const btn = e.target;
        const deviceId = btn.dataset.deviceId;

        try {
            const response = await fetch(`/api/device/${deviceId}/toggle/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                },
            });

            if (!response.ok) {
                alert("Failed to toggle device");
                return;
            }

            location.reload();

        } catch (err) {
            console.error(err);
            alert("Error toggling device");
        }
    });
});

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}