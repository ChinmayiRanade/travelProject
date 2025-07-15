// Simple form handling
document.getElementById('travelForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const loading = document.getElementById('loading');
    const form = this;
    
    // Get values from the form
    const destination = document.getElementById("destination").value;
    const duration = document.getElementById("duration").value;
    const budget = document.getElementById("budget").value;
    const travelers = document.getElementById("travelers").value;

    // Store them in an object
    const formData = {
        destination: destination,
        duration: parseInt(duration),
        budget: parseFloat(budget),
        travelers: travelers
    };

    // Show loading
    loading.style.display = 'block';
    form.style.display = 'none';

    console.log("Making api call")
    // Make API call
    plan_new_trip(formData)
    
    // Simulate API call
    setTimeout(() => {
        loading.style.display = 'none';
        form.style.display = 'block';
        form.reset();
        alert('Travel plan created successfully!');
    }, 2000);
});

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
        if (response.error) {
            alert("Error: " + response.error);
        } else {
            alert("🎉 Itinerary created!\n" + response.itinerary);
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert("Something went wrong while creating the travel plan.");
    });
}

function view_saved_plan(id) {
    fetch(`/api/view_plan/${id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(res => res.json())
    .then(response => {
        if (response.error) {
            alert("Error: " + response.error);
        } else {
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert("Something went wrong while creating the travel plan.");
    });
}


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
                        const attractionsHTML = detail.attractions.slice(0, 5).map(
                            a => `<span class="landmark-tag">${a.name}</span>`
                        ).join("");

                        const planCard = `
                            <div class="plan-card">
                                <div class="plan-header">
                                    <div class="plan-destination">
                                        <i class="fas fa-map-marker-alt"></i>
                                        ${detail.destination}
                                    </div>
                                    <div class="plan-rating">
                                        <i class="fas fa-star"></i>
                                        <span>${averageRating(detail.attractions)}</span>
                                    </div>
                                </div>
                                <div class="plan-details">
                                    <div class="plan-detail">
                                        <i class="fas fa-calendar-alt"></i>
                                        <span>${detail.num_attractions} days</span>
                                    </div>
                                    <div class="plan-detail">
                                        <i class="fas fa-dollar-sign"></i>
                                        <span>~$${estimateBudget(detail.attractions)}</span>
                                    </div>
                                    <div class="plan-detail">
                                        <i class="fas fa-users"></i>
                                        <span>—</span>
                                    </div>
                                    <div class="plan-detail">
                                        <i class="fas fa-map-signs"></i>
                                        <span>${detail.attractions.length} places to visit</span>
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

                        plansGrid.insertAdjacentHTML("beforeend", planCard);
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
    // Fake estimate per attraction. You can replace with real logic.
    const ticketCost = 20;
    return attractions.length * ticketCost;
}
