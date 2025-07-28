
// Form submission: triggers new trip planning
document.getElementById('travelForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const loading = document.getElementById('loading');
    const travelForm = document.getElementById("travelForm");
    const form = this;

    const destination = document.getElementById("destination").value;
    const duration = document.getElementById("duration").value;
    const budget = document.getElementById("budget").value;
    // const travelers = document.getElementById("travelers").value;

    const formData = {
        destination: destination,
        duration: parseInt(duration),
        budget: parseFloat(budget),
   
    };

    loading.style.display = 'flex';
    travelForm.style.display = "none";
    form.style.display = 'none';

    await plan_new_trip(formData)
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

document.getElementById("duration").addEventListener("input", function () {
    const max = 5;
    const val = parseInt(this.value, 10);
    if (val > max) {
        alert("Maximum duration is 5 days.");
        // this.value = max; // optional: auto-correct the value
    }
});

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
async function plan_new_trip(data) {
    fetch('/api/plan_new_trip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(response => {
            const loading = document.getElementById("loading");
            const form = document.getElementById("travelForm");
            loading.style.display = 'none';
            form.style.display = 'block';

            if (response.error) {
                alert("Error: " + response.error);
            } else {
                const itinerarySection = document.getElementById("itinerarySection");
                const itineraryContent = document.getElementById("itineraryContent");

                itineraryContent.innerHTML = formatItinerary(response.itinerary);
                itinerarySection.style.display = "block";
                scrollToItinerary()
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

// Create saved plan card — no weather or currency
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

// On page load: display all saved plans (with no weather or currency)
document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/view_all_plans')
        .then(res => res.json())
        .then(plans => {
            const plansGrid = document.getElementById("plansGrid");
            plansGrid.innerHTML = ""; // Clear placeholder content

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

function formatItinerary(itinerary) {
    // Replace **text** with <strong>text</strong>
    let formatted = itinerary.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Split by days and format each day
    const days = formatted.split(/(?=\*\*Day \d+:)/);
    
    let formattedHtml = '';
    
    days.forEach((day, index) => {
        if (day.trim()) {
            if (index === 0) {
                // First part (introduction)
                let intro = day.replace(/\n/g, '<br>');
                // Convert * to bullet points in intro
                intro = intro.replace(/^\* /gm, '• ');
                formattedHtml += `<div class="itinerary-intro">${intro}</div>`;
            } else {
                // Day sections
                let dayContent = day.replace(/\n/g, '<br>');
                // Convert * to bullet points in day content
                dayContent = dayContent.replace(/^\* /gm, '• ');
                formattedHtml += `<div class="itinerary-day">${dayContent}</div>`;
            }
        }
    });
    
    return formattedHtml;
}

function scrollToItinerary() {
    const section = document.getElementById("itinerarySection");
    if (section) {
      section.scrollIntoView({ behavior: "smooth" });
    }
  }