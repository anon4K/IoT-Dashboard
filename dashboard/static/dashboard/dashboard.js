function refreshSensorData() {
    document.querySelectorAll('.device-card').forEach(card => {
        const deviceId = card.dataset.deviceId;
        const table = card.querySelector('.sensor-table');

        fetch(`/api/device/${deviceId}/data/latest/`)
            .then(res => res.json())
            .then(data => {
                let rows = `
                    <tr>
                        <th>Time</th>
                        <th>Temp</th>
                        <th>Humidity</th>
                        <th>Distance</th>
                        <th>Sensor</th>
                    </tr>
                `;

                data.forEach(item => {
                    rows += `
                        <tr>
                            <td>${new Date(item.timestamp).toLocaleTimeString()}</td>
                            <td>${item.temperature}</td>
                            <td>${item.humidity}</td>
                            <td>${item.distance}</td>
                            <td>${item.sensor_type}</td>
                        </tr>
                    `;
                });

                table.innerHTML = rows;
            });
    });
}

setInterval(refreshSensorData, 3000);

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
