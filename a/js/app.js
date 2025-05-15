// Job Matcher Application

// State management
let currentQuestionIndex = 0;
let answers = {};
let jobs = [];
let matchedJobs = [];

// DOM Elements
const welcomeScreen = document.getElementById("welcome-screen");
const questionScreen = document.getElementById("question-screen");
const resultsScreen = document.getElementById("results-screen");
const questionContainer = document.getElementById("question-container");
const progressBar = document.getElementById("progress");
const jobMatchesContainer = document.getElementById("job-matches");
const startButton = document.getElementById("start-btn");
const startOverButton = document.getElementById("start-over-btn");

// Event Listeners
startButton.addEventListener("click", startQuestionnaire);
startOverButton.addEventListener("click", resetApplication);

// Initialize application
async function initApp() {
  try {
    const response = await fetch("data/jobs.json");
    if (!response.ok) {
      throw new Error("Failed to load jobs data");
    }
    jobs = await response.json();
    console.log("Jobs data loaded successfully:", jobs.length, "jobs found");
  } catch (error) {
    console.error("Error loading jobs data:", error);
    // Display error message to user
    alert("Nevarēja ielādēt darbu datus.");
  }
}

// Start the questionnaire
function startQuestionnaire() {
  welcomeScreen.classList.remove("active");
  questionScreen.classList.add("active");
  displayCurrentQuestion();
}

// Display the current question
function displayCurrentQuestion() {
  const question = questions[currentQuestionIndex];
  const progress = (currentQuestionIndex / questions.length) * 100;
  progressBar.style.width = progress + "%";

  let questionHTML = "";

  if (question.type === "scale") {
    questionHTML = `
            <div class="question">
                <h3>${question.text}</h3>
                <div class="scale-container">
                    <div class="scale-label">
                        <span>${question.minLabel}</span>
                        <span>${question.maxLabel}</span>
                    </div>
                    <input type="range" class="slider" id="q${question.id}" 
                        min="${question.min}" max="${question.max}" value="${
      answers[question.field] || 5
    }">
                    <div class="value-display"><span id="value-q${
                      question.id
                    }">${answers[question.field] || 5}</span></div>
                </div>
            </div>
        `;
  } else if (question.type === "multiple") {
    const optionsHTML = question.options
      .map(
        (option) => `
            <div class="option">
                <input type="radio" id="option-${option.value}" name="q${
          question.id
        }" value="${option.value}" 
                    ${
                      answers[question.field] === option.value ? "checked" : ""
                    }>
                <label for="option-${option.value}">${option.text}</label>
            </div>
        `
      )
      .join("");

    questionHTML = `
            <div class="question">
                <h3>${question.text}</h3>
                <div class="options-container">
                    ${optionsHTML}
                </div>
            </div>
        `;
  }

  // Add navigation buttons
  questionHTML += `
        <div class="question-nav">
            ${
              currentQuestionIndex > 0
                ? '<button class="btn btn-secondary" id="prev-btn">Previous</button>'
                : "<div></div>"
            }
            <button class="btn btn-primary" id="next-btn">
                ${
                  currentQuestionIndex === questions.length - 1
                    ? "Skatīt rezultātus"
                    : "Nākamais"
                }
            </button>
        </div>
    `;

  questionContainer.innerHTML = questionHTML;

  // Add event listeners for this question
  if (question.type === "scale") {
    const slider = document.getElementById(`q${question.id}`);
    const valueDisplay = document.getElementById(`value-q${question.id}`);

    slider.addEventListener("input", function () {
      valueDisplay.textContent = this.value;
    });
  }

  // Add event listeners for navigation
  const nextButton = document.getElementById("next-btn");
  nextButton.addEventListener("click", handleNextQuestion);

  const prevButton = document.getElementById("prev-btn");
  if (prevButton) {
    prevButton.addEventListener("click", handlePrevQuestion);
  }
}

// Handle next button click
function handleNextQuestion() {
  saveCurrentAnswer();

  if (currentQuestionIndex < questions.length - 1) {
    currentQuestionIndex++;
    displayCurrentQuestion();
  } else {
    calculateMatches();
    showResults();
  }
}

// Handle previous button click
function handlePrevQuestion() {
  saveCurrentAnswer();

  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    displayCurrentQuestion();
  }
}

// Save the current answer
function saveCurrentAnswer() {
  const question = questions[currentQuestionIndex];

  if (question.type === "scale") {
    const slider = document.getElementById(`q${question.id}`);
    answers[question.field] = parseInt(slider.value);
  } else if (question.type === "multiple") {
    const selectedOption = document.querySelector(
      `input[name="q${question.id}"]:checked`
    );
    if (selectedOption) {
      answers[question.field] = parseInt(selectedOption.value);
    }
  }
}

// Calculate job matches based on user answers
function calculateMatches() {
  // Define weights for different factors (can be adjusted)
  const weights = {
    teamwork_preference: 0.8,
    learning_opportunity: 1.0,
    experience_required: 1.0,
    work_environment: 1.0,
    stress_level: 0.8,
    creativity_required: 0.8,
    company_size: 0.6,
    remote_preference: 0.9,
    career_growth: 0.8,
    project_type: 0.7,
  };

  matchedJobs = jobs.map((job) => {
    let weightedScore = 0;
    let totalWeight = 0;

    for (const field in answers) {
      if (job[field] !== undefined) {
        // Calculate match percentage (0-100)
        // Lower difference means better match
        const userValue = answers[field];
        const jobValue = job[field];
        const maxPossibleDifference = 10; // Scale is 0-10

        // Calculate how well they match (100% = perfect match, 0% = completely opposite)
        const difference = Math.abs(jobValue - userValue);
        const factorScore = 100 - difference * 10; // Convert to percentage

        // Apply weight for this factor
        const weight = weights[field] || 1.0;
        weightedScore += factorScore * weight;
        totalWeight += weight;
      }
    }

    // Calculate weighted average match score
    const finalScore =
      totalWeight > 0 ? Math.round(weightedScore / totalWeight) : 0;

    return {
      ...job,
      matchScore: finalScore,
    };
  });

  // Sort jobs by match score (highest first)
  matchedJobs.sort((a, b) => b.matchScore - a.matchScore);

  // Only keep the top matches (e.g., top 10)
  matchedJobs = matchedJobs.slice(0, 10);
}

// Show results screen with matched jobs
function showResults() {
  questionScreen.classList.remove("active");
  resultsScreen.classList.add("active");

  let jobMatchesHTML = "";

  if (matchedJobs.length === 0) {
    jobMatchesHTML = "<p>Netika atrasts neviens piemērots darbs.</p>";
  } else {
    matchedJobs.forEach((job) => {
      // Format salary if available
      let salaryText = "";
      if (job.salary_min > 0 || job.salary_max > 0) {
        if (job.salary_min > 0 && job.salary_max > 0) {
          salaryText = `${job.salary_min} - ${job.salary_max} €`;
        } else if (job.salary_min > 0) {
          salaryText = `No mazāk kā ${job.salary_min} €`;
        } else if (job.salary_max > 0) {
          salaryText = `Līdz ${job.salary_max} €`;
        }
      }

      // Create match explanation based on answers
      const matchFactors = [];
      if (Math.abs(job.work_environment - answers.work_environment) <= 2) {
        matchFactors.push("Darba vide");
      }
      if (
        Math.abs(job.experience_required - answers.experience_required) <= 2
      ) {
        matchFactors.push("Pieredzes prasības");
      }
      if (answers.creativity_required > 7 && job.creativity_required >= 7) {
        matchFactors.push("Radoša darba iespējas");
      }
      if (answers.career_growth > 7 && job.career_growth >= 7) {
        matchFactors.push("Karjeras izaugsme");
      }

      const matchReason =
        matchFactors.length > 0
          ? `<div class="match-reason">Laba sakritība: ${matchFactors.join(
              ", "
            )}</div>`
          : "";

      jobMatchesHTML += `
        <div class="job-match">
            <div class="match-header">
                <h3>${job.title}</h3>
                <div class="match-score">${job.matchScore}% sakritiība</div>
            </div>
            <div class="match-company">${job.company}</div>
            <div class="match-location">${job.location}</div>
            ${
              salaryText
                ? `<div class="match-salary">Alga: ${salaryText}</div>`
                : ""
            }
            ${matchReason}
            
            <div class="match-details">
                <button class="btn btn-outline job-details-btn" data-jobid="${
                  job.id
                }">Skatīt aprakstu</button>
                ${
                  job.url
                    ? `<a href="${job.url}" target="_blank" class="btn btn-primary">Pieteikties</a>`
                    : ""
                }
            </div>
            
            <div class="job-full-details" id="details-${
              job.id
            }" style="display: none;">
                ${
                  job.description
                    ? `<h4>Darba apraksts</h4><p>${job.description}</p>`
                    : ""
                }
                ${
                  job.requirements
                    ? `<h4>Prasības</h4><p>${job.requirements}</p>`
                    : ""
                }
                ${
                  job.responsibilities
                    ? `<h4>Pienākumi</h4><p>${job.responsibilities}</p>`
                    : ""
                }
                ${
                  job.benefits
                    ? `<h4>Priekšrocības</h4><p>${job.benefits}</p>`
                    : ""
                }
                ${
                  job.deadline
                    ? `<p><strong>Pieteikšanās termiņš:</strong> ${job.deadline}</p>`
                    : ""
                }
            </div>
        </div>
      `;
    });
  }

  jobMatchesContainer.innerHTML = jobMatchesHTML;

  // Add event listeners for job detail buttons
  const detailButtons = document.querySelectorAll(".job-details-btn");
  detailButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const jobId = this.getAttribute("data-jobid");
      const detailsSection = document.getElementById(`details-${jobId}`);

      if (detailsSection.style.display === "none") {
        detailsSection.style.display = "block";
        this.textContent = "Paslēpt aprakstu";
      } else {
        detailsSection.style.display = "none";
        this.textContent = "Parādīt aprakstu";
      }
    });
  });
}

// Reset application to start over
function resetApplication() {
  currentQuestionIndex = 0;
  answers = {};
  matchedJobs = [];

  resultsScreen.classList.remove("active");
  welcomeScreen.classList.add("active");
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", initApp);
