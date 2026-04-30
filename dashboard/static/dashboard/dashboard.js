document.querySelectorAll('.device-card').forEach(card => {
    const deviceId = card.dataset.deviceId;
    const tbody = card.querySelector('.sensor-table tbody');

    const ws = new WebSocket(`ws://${window.location.host}/ws/device/${deviceId}/`);

    ws.onopen = () => console.log(`✅ WS connected for ${deviceId}`);

    ws.onmessage = (e) => {
        const d = JSON.parse(e.data);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${d.timestamp}</td>
            <td>${d.temperature ?? '-'}</td>
            <td>${d.humidity ?? '-'}</td>
            <td>${d.distance ?? '-'}</td>
            <td>${d.sensor_type}</td>
        `;

        if (d.sensor_type === 'motion' || (d.distance !== null && d.distance < 50)) {
            row.classList.add('alert-row');
        }

        tbody.insertBefore(row, tbody.firstChild);
        if (tbody.rows.length > 10) {
            tbody.deleteRow(tbody.rows.length - 1);
        }
    };

    ws.onerror = (e) => console.error(`❌ WS error for ${deviceId}`, e);
    ws.onclose = () => console.log(`🔌 WS closed for ${deviceId}`);
});


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


document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", async (e) => {
        if (!e.target.classList.contains("cmd-btn")) return;

        const deviceId = e.target.dataset.deviceId;
        const input = document.querySelector(`.command-input[data-device-id="${deviceId}"]`);
        const command = input.value.trim();

        if (!command) {
            alert("Please enter a command.");
            return;
        }

        try {
            const response = await fetch(`/api/device/${deviceId}/command/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ command }),
            });

            if (!response.ok) {
                alert("Failed to send command.");
                return;
            }

            const data = await response.json();
            console.log(`📨 Command sent:`, data);
            input.value = '';
            alert(`✅ Command "${command}" sent! ID: ${data.id}`);

        } catch (err) {
            console.error(err);
            alert("Error sending command.");
        }
    });
});

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

