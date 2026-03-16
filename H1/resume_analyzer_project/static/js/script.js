document.addEventListener('DOMContentLoaded', function () {
    // Determine if we're on the results page by checking for the JSON data element
    const dataElement = document.getElementById('results-data');
    if (!dataElement) return;

    let candidatesList = [];
    try {
        candidatesList = JSON.parse(dataElement.textContent);
    } catch (e) {
        console.error("Error parsing results data:", e);
        return;
    }

    if (!Array.isArray(candidatesList) || candidatesList.length === 0) {
        return;
    }

    // Prepare data for the Leaderboard Chart (Bar Chart)
    const leaderboardCanvas = document.getElementById('leaderboardChart');
    if (leaderboardCanvas) {
        const lbCtx = leaderboardCanvas.getContext('2d');

        // Take top 10 for drawing so it doesn't get squished if huge dataset
        const displayData = candidatesList.slice(0, 10);

        const labels = displayData.map(c => c.name);
        const scores = displayData.map(c => c.score);
        const colors = displayData.map(c => {
            if (c.score >= 85) return '#16a34a'; // strong hire green
            if (c.score >= 70) return '#2563eb'; // hire blue
            if (c.score >= 50) return '#ca8a04'; // consider yellow
            return '#dc2626'; // not recommended red
        });

        new Chart(lbCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Match Score %',
                    data: scores,
                    backgroundColor: colors,
                    borderRadius: 4,
                    barThickness: 'flex',
                    maxBarThickness: 40
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: '#f3f4f6'
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            callback: function (value, index, values) {
                                // Truncate long names for chart x-axis
                                const name = labels[index];
                                return name.split(' ')[0]; // Only show first name
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.raw + '% Match';
                            }
                        }
                    }
                }
            }
        });
    }

    // Recommendation Distribution Pie Chart
    const recCanvas = document.getElementById('recommendationPieChart');
    if (recCanvas) {
        const recCtx = recCanvas.getContext('2d');

        // Aggregate statistics
        let counts = {
            'Strong Hire': 0,
            'Hire': 0,
            'Consider': 0,
            'Not Recommended': 0
        };

        candidatesList.forEach(c => {
            if (counts[c.recommendation] !== undefined) {
                counts[c.recommendation]++;
            }
        });

        new Chart(recCtx, {
            type: 'doughnut',
            data: {
                labels: ['Strong Hire', 'Hire', 'Consider', 'Not Recommended'],
                datasets: [{
                    data: [
                        counts['Strong Hire'],
                        counts['Hire'],
                        counts['Consider'],
                        counts['Not Recommended']
                    ],
                    backgroundColor: ['#22c55e', '#3b82f6', '#eab308', '#ef4444'],
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            font: { family: "'Inter', sans-serif", size: 10 }
                        }
                    }
                }
            }
        });
    }
});
