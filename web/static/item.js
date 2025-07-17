// Form submission: triggers new trip planning
document.getElementById('travelForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const loading = document.getElementById('loading');
    const form = this;

    const destination = document.getElementById("destination").value;
    const duration = document.getElementById("duration").value;
    const budget = document.getElementById("budget").value;
    const travelers = document.getElementById("travelers").value;

    const formData = {
        destination: destination,
        duration: parseInt(duration),
        budget: parseFloat(budget),
        travelers: travelers
    };

    loading.style.display = 'block';
    form.style.display = 'none';

    plan_new_trip(formData);
});

// Show currency preview when typing destination
document.getElementById('destination').addEventListener('input', debounce(function(e) {
    const destination = e.target.value.trim();
    if (destination.length > 2) {
        showCurrencyPreview(destination);
    } else {
        hideDestinationPreview();
    }
}, 300));

function showCurrencyPreview(destination) {
    const existingPreview = document.querySelector('.destination-preview');
    if (existingPreview) existingPreview.remove();

    const destinationGroup = document.getElementById('destination').closest('.form-group');
    const preview = document.createElement('div');
    preview.className = 'destination-preview';
    preview.innerHTML = `
        <div class="preview-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Loading exchange rate...</span>
        </div>
    `;
    destinationGroup.appendChild(preview);

    fetch(`/api/exchange_rate/${encodeURIComponent(destination)}`)
        .then(r => r.json())
        .then(exchangeData => {
            if (exchangeData.error) {
                preview.innerHTML = '<span class="error">Exchange rate unavailable</span>';
            } else {
                preview.innerHTML = `
                    <div class="compact-exchange">
                        <div class="exchange-icon">
                            <i class="fas fa-exchange-alt"></i>
                        </div>
                        <span class="exchange-rate">${exchangeData.rate}</span>
                        <span class="currency-bubble">${exchangeData.currency}</span>
                    </div>
                `;
            }
        })
        .catch(err => {
            console.error('Error fetching exchange rate:', err);
            preview.innerHTML = '<span class="error">Exchange rate unavailable</span>';
        });
}

function hideDestinationPreview() {
    const preview = document.querySelector('.destination-preview');
    if (preview) {
        preview.remove();
    }
}

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Plan new trip, show only the generated itinerary (no weather/currency alert)
function plan_new_trip(data) {
    fetch('/api/plan_new_trip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(response => {
            const loading = document.getElementById('loading');
            const form = document.getElementById('travelForm');
            loading.style.display = 'none';
            form.style.display = 'block';

            if (response.error) {
                alert("Error: " + response.error);
            } else {
                form.reset();
                hideDestinationPreview();

                const plansGrid = document.getElementById("plansGrid");
                const itineraryCard = document.createElement("div");
                itineraryCard.className = "plan-card";
                itineraryCard.innerHTML = `
                    <div class="plan-header">
                        <div class="plan-destination">
                            <i class="fas fa-map-marker-alt"></i>
                            ${response.destination}
                        </div>
                    </div>
                    <div class="plan-details itinerary-content">
                        ${response.itinerary.replace(/\n/g, "<br>")}
                    </div>
                `;

                plansGrid.insertBefore(itineraryCard, plansGrid.firstChild);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            const loading = document.getElementById('loading');
            const form = document.getElementById('travelForm');
            loading.style.display = 'none';
            form.style.display = 'block';
            alert("Something went wrong while creating the travel plan.");
        });
}

function view_saved_plan(id) {
    fetch(`/api/view_plan/${id}`)
        .then(res => res.json())
        .then(response => {
            if (response.error) {
                alert("Error: " + response.error);
            } else {
                console.log("Plan details:", response);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert("Something went wrong while retrieving the travel plan.");
        });
}

function createPlanCard(detail) {
    const attractions = detail.attractions || [];
    const attractionsHTML = attractions.slice(0, 5).map(
        a => `<span class="landmark-tag">${a.name}</span>`
    ).join("");

    const planCard = `
        <div class="plan-card" data-plan-id="${detail.plan_id}">
            <div class="plan-header">
                <div class="plan-destination">
                    <i class="fas fa-map-marker-alt"></i>
                    ${detail.destination}
                </div>
                <div class="plan-rating">
                    <i class="fas fa-star"></i>
                    <span>${averageRating(attractions)}</span>
                </div>
            </div>
            <div class="plan-details">
                <div class="plan-detail">
                    <i class="fas fa-calendar-alt"></i>
                    <span>${detail.num_attractions} places</span>
                </div>
                <div class="plan-detail">
                    <i class="fas fa-dollar-sign"></i>
                    <span>~$${estimateBudget(attractions)}</span>
                </div>
                <div class="plan-detail">
                    <i class="fas fa-map-signs"></i>
                    <span>${attractions.length} attractions</span>
                </div>
            </div>
            <div class="plan-landmarks">
                <div class="landmarks-title">Top Attractions:</div>
                <div class="landmarks-list">
                    ${attractionsHTML}
                </div>
            </div>
        </div>
    `;
    document.getElementById("plansGrid").insertAdjacentHTML("beforeend", planCard);
}

document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/view_all_plans')
        .then(res => res.json())
        .then(plans => {
            const plansGrid = document.getElementById("plansGrid");
            plansGrid.innerHTML = "";

            if (!Array.isArray(plans) || plans.length === 0) {
                plansGrid.innerHTML = "<p>No saved travel plans found.</p>";
                return;
            }

            plans.forEach(plan => {
                fetch(`/api/view_plan/${plan.id}`)
                    .then(res => res.json())
                    .then(detail => {
                        createPlanCard(detail);
                    })
                    .catch(error => {
                        console.error("Error loading plan details:", error);
                    });
            });
        })
        .catch(error => {
            console.error("Error loading plans:", error);
            document.getElementById("plansGrid").innerHTML = "<p>Error loading travel plans.</p>";
        });
});

function averageRating(attractions) {
    if (!attractions || attractions.length === 0) return "—";
    const avg = attractions.reduce((sum, a) => sum + parseFloat(a.rating || 0), 0) / attractions.length;
    return avg.toFixed(1);
}

function estimateBudget(attractions) {
    const ticketCost = 20;
    return attractions.length * ticketCost;
}
