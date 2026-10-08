(() => {
  const chartInstances = {};
  const colors = {
    low: '#1b8f70',
    medium: '#d68b1f',
    high: '#c64c53',
    positive: '#337d61',
    neutral: '#718096',
    negative: '#c64c53',
    ink: '#173a4a',
    grid: '#dfe8e8',
  };

  const updateMetric = (id, value) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  };

  const createOrUpdate = (id, config) => {
    const canvas = document.getElementById(id);
    if (!canvas || typeof Chart === 'undefined') return;
    if (chartInstances[id]) chartInstances[id].destroy();
    chartInstances[id] = new Chart(canvas, config);
  };

  const render = (data) => {
    updateMetric('metric-total', data.total);
    updateMetric('metric-low', data.risk_counts.Baixo);
    updateMetric('metric-medium', data.risk_counts['Médio']);
    updateMetric('metric-high', data.risk_counts.Alto);

    const sharedDoughnut = {
      type: 'doughnut',
      options: { responsive: true, maintainAspectRatio: false, cutout: '67%', plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, usePointStyle: true, padding: 18 } } } },
    };
    createOrUpdate('riskChart', {
      ...sharedDoughnut,
      data: { labels: ['Baixo risco', 'Médio risco', 'Alto risco'], datasets: [{ data: [data.risk_counts.Baixo, data.risk_counts['Médio'], data.risk_counts.Alto], backgroundColor: [colors.low, colors.medium, colors.high], borderWidth: 0 }] },
    });
    createOrUpdate('polarityChart', {
      ...sharedDoughnut,
      data: { labels: ['Positiva', 'Neutra', 'Negativa'], datasets: [{ data: [data.polarity_counts.positive, data.polarity_counts.neutral, data.polarity_counts.negative], backgroundColor: [colors.positive, colors.neutral, colors.negative], borderWidth: 0 }] },
    });
    createOrUpdate('courseChart', {
      type: 'bar',
      data: { labels: data.course_distribution.courses, datasets: [
        { label: 'Baixo', data: data.course_distribution.series.Baixo, backgroundColor: colors.low, borderRadius: 4 },
        { label: 'Médio', data: data.course_distribution.series['Médio'], backgroundColor: colors.medium, borderRadius: 4 },
        { label: 'Alto', data: data.course_distribution.series.Alto, backgroundColor: colors.high, borderRadius: 4 },
      ] },
      options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, grid: { color: colors.grid } } }, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, usePointStyle: true, padding: 18 } } } },
    });
    createOrUpdate('semesterChart', {
      type: 'line',
      data: { labels: data.semester_distribution.labels.map((value) => `${value}º`), datasets: [{ label: 'Registros', data: data.semester_distribution.values, borderColor: colors.ink, backgroundColor: 'rgba(23, 58, 74, .12)', fill: true, tension: .35, pointRadius: 4, pointBackgroundColor: colors.ink }] },
      options: { responsive: true, maintainAspectRatio: false, scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: colors.grid } } }, plugins: { legend: { display: false } } },
    });
  };

  if (window.dashboardConfig) {
    render(window.dashboardConfig);
    window.setInterval(async () => {
      try {
        const response = await fetch('/api/dashboard', { headers: { Accept: 'application/json' } });
        if (response.ok) render(await response.json());
      } catch (_) {
        // The dashboard remains usable with the most recently rendered aggregates.
      }
    }, 30000);
  }
})();
