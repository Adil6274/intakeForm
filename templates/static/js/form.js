document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("intakeForm");
    const steps = Array.from(document.querySelectorAll(".form-step"));
    const nextButtons = document.querySelectorAll(".btn-next");
    const prevButtons = document.querySelectorAll(".btn-prev");
    const progressFill = document.getElementById("progressFill");
    const stepIndicators = document.querySelectorAll(".step-indicator");
    const addProjectBtn = document.getElementById("addProjectBtn");
    const projectsContainer = document.getElementById("projectsContainer");

    let currentStep = 0;

    function updateStep(direction) {
        steps[currentStep].classList.remove("active");
        if (direction === "next") currentStep++;
        if (direction === "prev") currentStep--;
        if (currentStep < 0) currentStep = 0;
        if (currentStep >= steps.length) currentStep = steps.length - 1;
        steps[currentStep].classList.add("active");
        updateProgress();
    }

    function updateProgress() {
        const percent = ((currentStep + 1) / steps.length) * 100;
        progressFill.style.width = `${percent}%`;
        stepIndicators.forEach((el, idx) => {
            el.classList.toggle("active", idx === currentStep);
        });
    }

    nextButtons.forEach(btn => {
        btn.addEventListener("click", () => updateStep("next"));
    });
    prevButtons.forEach(btn => {
        btn.addEventListener("click", () => updateStep("prev"));
    });

    updateProgress();

    // Add more project cards
    if (addProjectBtn && projectsContainer) {
        addProjectBtn.addEventListener("click", () => {
            const count = projectsContainer.querySelectorAll(".project-card").length;
            const card = document.createElement("div");
            card.className = "project-card";
            card.innerHTML = `
                <div class="grid-2">
                    <div class="form-group">
                        <label>Project Title *</label>
                        <input type="text" name="projectTitle[]" required>
                    </div>
                    <div class="form-group">
                        <label>Your Role</label>
                        <input type="text" name="projectRole[]" placeholder="e.g. Lead Developer, Data Analyst">
                    </div>
                </div>
                <div class="form-group">
                    <label>Project Description *</label>
                    <textarea name="projectDesc[]" required></textarea>
                </div>
                <div class="grid-2">
                    <div class="form-group">
                        <label>Tech Stack</label>
                        <input type="text" name="projectTech[]" placeholder="React, Flask, PostgreSQL, Power BI">
                    </div>
                    <div class="form-group">
                        <label>Results / Impact</label>
                        <textarea name="projectResults[]" placeholder="e.g. +15% revenue, -40% processing time"></textarea>
                    </div>
                </div>
                <div class="grid-2">
                    <div class="form-group">
                        <label>Live URL / Demo</label>
                        <input type="url" name="projectUrl[]" placeholder="https://">
                    </div>
                    <div class="form-group">
                        <label>Upload Screenshots</label>
                        <input type="file" name="projectFiles_${count}" multiple>
                    </div>
                </div>
            `;
            projectsContainer.appendChild(card);
        });
    }

    // Optional: simple required-field check before final submit
    form.addEventListener("submit", (e) => {
        // Let HTML required handle most validation
    });
});
