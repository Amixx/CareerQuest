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
    alert("Unable to load jobs data. Please try again later.");
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
                    ? "See Results"
                    : "Next"
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
  matchedJobs = jobs.map((job) => {
    let matchScore = 0;
    let totalFactors = 0;

    for (const field in answers) {
      if (job[field] !== undefined) {
        // Calculate how close the job is to the user's preference
        // Lower difference means better match
        const difference = Math.abs(job[field] - answers[field]);
        const maxPossibleDifference = 10; // Scale is 0-10
        const factorScore = 100 - difference * 10; // Convert to percentage

        matchScore += factorScore;
        totalFactors++;
      }
    }

    // Calculate average match score if we have factors to consider
    const finalScore =
      totalFactors > 0 ? Math.round(matchScore / totalFactors) : 0;

    return {
      ...job,
      matchScore: finalScore,
    };
  });

  // Sort jobs by match score (highest first)
  matchedJobs.sort((a, b) => b.matchScore - a.matchScore);

  // Only keep the top matches (e.g., top 5)
  matchedJobs = matchedJobs.slice(0, 5);
}

// Show results screen with matched jobs
function showResults() {
  questionScreen.classList.remove("active");
  resultsScreen.classList.add("active");

  let jobMatchesHTML = "";

  if (matchedJobs.length === 0) {
    jobMatchesHTML =
      "<p>No matching jobs found. Try adjusting your preferences.</p>";
  } else {
    matchedJobs.forEach((job) => {
      jobMatchesHTML += `
                <div class="job-match">
                    <div class="match-header">
                        <h3>${job.title}</h3>
                        <div class="match-score">${job.matchScore}% Match</div>
                    </div>
                    <div class="match-company">${job.company}</div>
                    <div class="match-location">${job.location}</div>
                    ${
                      job.salary
                        ? `<div class="match-salary">Salary: ${job.salary}</div>`
                        : ""
                    }
                    
                    <div class="match-details">
                        <button class="btn btn-outline job-details-btn" data-jobid="${
                          job.id
                        }">View Details</button>
                        ${
                          job.url
                            ? `<a href="${job.url}" target="_blank" class="btn btn-primary">Apply Now</a>`
                            : ""
                        }
                    </div>
                    
                    <div class="job-full-details" id="details-${
                      job.id
                    }" style="display: none;">
                        ${
                          job.description
                            ? `
                            <h4>Job Description</h4>
                            <p>${job.description}</p>
                        `
                            : ""
                        }
                        
                        ${
                          job.requirements
                            ? `
                            <h4>Requirements</h4>
                            <p>${job.requirements}</p>
                        `
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
        this.textContent = "Hide Details";
      } else {
        detailsSection.style.display = "none";
        this.textContent = "View Details";
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
