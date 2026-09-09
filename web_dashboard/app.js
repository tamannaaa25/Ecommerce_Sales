/**
 * Simple, Humanized E-Commerce Dashboard Controller
 * Connects to user dataset (48 orders, 8 customers, INR ₹)
 */

document.addEventListener('DOMContentLoaded', () => {
  const data = window.ANALYTICS_DATA;
  if (!data) {
    console.error('Analytics data not loaded!');
    return;
  }

  // State Management
  const state = {
    selectedYear: 'ALL',
    selectedRegion: 'ALL',
    selectedCategory: 'ALL'
  };

  // Chart instances
  let monthlyTrendChart = null;
  let categoryShareChart = null;
  let regionalBarChart = null;

  // Currency & Number Formatters (Indian Rupees)
  const formatCurrency = (val) => '₹' + Math.round(val).toLocaleString('en-IN');
  const formatNumber = (val) => new Intl.NumberFormat('en-IN').format(val);

  // Filter Data
  function getFilteredGranularSales() {
    return data.granular_sales.filter(item => {
      const matchMonth = state.selectedYear === 'ALL' || item.year_month === state.selectedYear;
      const matchRegion = state.selectedRegion === 'ALL' || item.region === state.selectedRegion;
      const matchCategory = state.selectedCategory === 'ALL' || item.category === state.selectedCategory;
      return matchMonth && matchRegion && matchCategory;
    });
  }

  // Update Top KPI Cards
  function updateKPIs() {
    const filtered = getFilteredGranularSales();

    let totalRevenue = 0;
    let totalOrders = 0;
    let totalUnits = 0;

    filtered.forEach(row => {
      totalRevenue += row.revenue;
      totalOrders += row.orders;
      totalUnits += row.units_sold;
    });

    const aov = totalOrders > 0 ? (totalRevenue / totalOrders) : 0;

    document.getElementById('kpi-revenue').textContent = formatCurrency(totalRevenue);
    document.getElementById('kpi-orders').textContent = formatNumber(totalOrders);
    document.getElementById('kpi-aov').textContent = formatCurrency(aov);
    document.getElementById('kpi-units').textContent = formatNumber(totalUnits);
  }

  // 1. Monthly Revenue & Orders Chart
  function renderMonthlyTrendChart() {
    const filtered = getFilteredGranularSales();

    const monthlyMap = {};
    filtered.forEach(item => {
      if (!monthlyMap[item.year_month]) {
        monthlyMap[item.year_month] = { revenue: 0, orders: 0 };
      }
      monthlyMap[item.year_month].revenue += item.revenue;
      monthlyMap[item.year_month].orders += item.orders;
    });

    const sortedMonths = Object.keys(monthlyMap).sort();
    const displayLabels = sortedMonths.map(m => m === '2026-01' ? 'January 2026' : 'February 2026');
    const revenueValues = sortedMonths.map(m => monthlyMap[m].revenue);
    const orderValues = sortedMonths.map(m => monthlyMap[m].orders);

    const ctx = document.getElementById('monthlyTrendCanvas').getContext('2d');
    if (monthlyTrendChart) monthlyTrendChart.destroy();

    monthlyTrendChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: displayLabels,
        datasets: [
          {
            label: 'Sales Revenue',
            data: revenueValues,
            backgroundColor: '#3B82F6',
            borderRadius: 6,
            yAxisID: 'y',
            order: 2
          },
          {
            label: 'Order Count',
            data: orderValues,
            type: 'line',
            borderColor: '#F59E0B',
            backgroundColor: '#F59E0B',
            pointRadius: 5,
            borderWidth: 2,
            tension: 0.2,
            yAxisID: 'y1',
            order: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: '#475569', font: { size: 12, weight: '500' } }
          },
          tooltip: {
            backgroundColor: '#0F172A',
            padding: 10,
            callbacks: {
              label: (ctx) => ctx.dataset.label.includes('Revenue') ? ` Revenue: ${formatCurrency(ctx.parsed.y)}` : ` Orders: ${ctx.parsed.y}`
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#475569', font: { weight: '500' } }
          },
          y: {
            grid: { color: '#F1F5F9' },
            ticks: {
              color: '#64748B',
              callback: (val) => val >= 100000 ? `₹${(val / 100000).toFixed(1)}L` : `₹${val}`
            }
          },
          y1: {
            position: 'right',
            grid: { display: false },
            ticks: { color: '#D97706', stepSize: 5 }
          }
        }
      }
    });
  }

  // 2. Category Share (Doughnut)
  function renderCategoryShareChart() {
    const filtered = getFilteredGranularSales();

    const catMap = {};
    filtered.forEach(item => {
      catMap[item.category] = (catMap[item.category] || 0) + item.revenue;
    });

    const labels = Object.keys(catMap);
    const dataValues = labels.map(l => catMap[l]);

    const ctx = document.getElementById('categoryShareCanvas').getContext('2d');
    if (categoryShareChart) categoryShareChart.destroy();

    categoryShareChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: dataValues,
          backgroundColor: ['#2563EB', '#F59E0B', '#8B5CF6'],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#475569', font: { size: 12 }, boxWidth: 12 }
          },
          tooltip: {
            backgroundColor: '#0F172A',
            padding: 10,
            callbacks: {
              label: function(ctx) {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                return ` ${ctx.label}: ${formatCurrency(ctx.parsed)} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  // 3. Regional Bar Chart
  function renderRegionalChart() {
    const filtered = getFilteredGranularSales();

    const regMap = {};
    filtered.forEach(item => {
      regMap[item.region] = (regMap[item.region] || 0) + item.revenue;
    });

    const sortedRegions = Object.keys(regMap).sort((a, b) => regMap[b] - regMap[a]);
    const values = sortedRegions.map(r => regMap[r]);

    const ctx = document.getElementById('regionalBarCanvas').getContext('2d');
    if (regionalBarChart) regionalBarChart.destroy();

    regionalBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: sortedRegions,
        datasets: [{
          label: 'Regional Revenue',
          data: values,
          backgroundColor: '#3B82F6',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0F172A',
            callbacks: {
              label: (ctx) => ` Revenue: ${formatCurrency(ctx.parsed.x)}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: '#F1F5F9' },
            ticks: {
              color: '#64748B',
              callback: (val) => val >= 100000 ? `₹${(val / 100000).toFixed(1)}L` : `₹${val}`
            }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#0F172A', font: { weight: '600' } }
          }
        }
      }
    });
  }

  // 4. Products Table
  function populateProductsTable() {
    const tbody = document.getElementById('productsTableBody');
    tbody.innerHTML = '';

    const prods = data.top_products || [];

    prods.forEach((p, idx) => {
      const tr = document.createElement('tr');
      const badgeClass = p.category === 'Electronics' ? 'badge-electronics' : p.category === 'Furniture' ? 'badge-furniture' : 'badge-clothing';

      tr.innerHTML = `
        <td><span class="rank-pill ${idx < 3 ? 'top' : ''}">${idx + 1}</span></td>
        <td class="product-name">${p.product}</td>
        <td><span class="pill-badge ${badgeClass}">${p.category}</span></td>
        <td>${p.units_sold} units</td>
        <td>${formatCurrency(p.unit_price)}</td>
        <td class="revenue-text">${formatCurrency(p.revenue)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // 5. Customers Table
  function populateCustomersTable() {
    const tbody = document.getElementById('customersTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const custs = data.top_customers || [];
    custs.forEach((c) => {
      const tr = document.createElement('tr');
      const isTop = c.total_spend > 200000;
      const badgeText = isTop ? 'Top Buyer' : 'Repeat Buyer';
      const badgeClass = isTop ? 'badge-electronics' : 'badge-clothing';

      tr.innerHTML = `
        <td class="customer-name">${c.customer}</td>
        <td>${c.region}</td>
        <td>${c.total_orders} orders</td>
        <td>${c.total_quantity} items</td>
        <td>${formatCurrency(c.aov)}</td>
        <td class="revenue-text">${formatCurrency(c.total_spend)}</td>
        <td><span class="pill-badge ${badgeClass}">${badgeText}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  // 6. Customer Summary Cards
  function populateCustomerCards() {
    const container = document.getElementById('rfmCardsContainer');
    if (!container) return;
    container.innerHTML = '';

    const summaryCards = [
      { title: 'Top 3 Buyers (Aarav, Isha, Sanya)', amount: '₹11.2 Lakhs', sub: 'Drives 78% of company revenue' },
      { title: 'Mid-Tier (Kabir, Rohan, Diya)', amount: '₹2.2 Lakhs', sub: 'Furniture & Clothing orders' },
      { title: 'Entry Repeat (Arjun, Meera)', amount: '₹95,700', sub: 'Shoes & Headphones orders' }
    ];

    summaryCards.forEach(c => {
      const div = document.createElement('div');
      div.className = 'tier-card';
      div.innerHTML = `
        <div class="tier-card-title">${c.title}</div>
        <div class="tier-card-amount">${c.amount}</div>
        <div class="tier-card-sub">${c.sub}</div>
      `;
      container.appendChild(div);
    });
  }

  // Master Render
  function renderAll() {
    updateKPIs();
    renderMonthlyTrendChart();
    renderCategoryShareChart();
    renderRegionalChart();
    populateProductsTable();
    populateCustomersTable();
    populateCustomerCards();
  }

  // Event Listeners for Filters
  document.querySelectorAll('#yearFilter .pill-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('#yearFilter .pill-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.selectedYear = e.target.dataset.value;
      renderAll();
    });
  });

  const regionSelect = document.getElementById('regionSelect');
  if (regionSelect) {
    regionSelect.addEventListener('change', (e) => {
      state.selectedRegion = e.target.value;
      renderAll();
    });
  }

  const categorySelect = document.getElementById('categorySelect');
  if (categorySelect) {
    categorySelect.addEventListener('change', (e) => {
      state.selectedCategory = e.target.value;
      renderAll();
    });
  }

  const resetBtn = document.getElementById('resetFiltersBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      state.selectedYear = 'ALL';
      state.selectedRegion = 'ALL';
      state.selectedCategory = 'ALL';

      document.querySelectorAll('#yearFilter .pill-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.value === 'ALL');
      });
      if (regionSelect) regionSelect.value = 'ALL';
      if (categorySelect) categorySelect.value = 'ALL';

      renderAll();
    });
  }

  // Tab Navigation
  document.querySelectorAll('.tab-btn').forEach(tab => {
    tab.addEventListener('click', (e) => {
      document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      e.target.classList.add('active');
      const targetContent = document.getElementById(e.target.dataset.target);
      if (targetContent) targetContent.classList.add('active');
    });
  });

  // Initial Run
  renderAll();
});
