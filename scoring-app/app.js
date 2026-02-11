// Global state
let rawPapers = [];
let manualPapers = [];
let currentIndex = 0;
let currentDate = '';
let classifications = [];

// DOM elements
const dateSelect = document.getElementById('dateSelect');
const loadBtn = document.getElementById('loadBtn');
const paperDisplay = document.getElementById('paperDisplay');
const paperTitle = document.getElementById('paperTitle');
const paperAbstract = document.getElementById('paperAbstract');
const analysedBadge = document.getElementById('analysedBadge');
const analysedStatus = document.getElementById('analysedStatus');
const currentScore = document.getElementById('currentScore');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const message = document.getElementById('message');
const paperCount = document.getElementById('paperCount');
const analysedCount = document.getElementById('analysedCount');
const currentIndexSpan = document.getElementById('currentIndex');
const scoreButtons = document.querySelectorAll('.score-btn');
const classificationSelect = document.getElementById('classificationSelect');

// Initialize
async function init() {
    await Promise.all([loadAvailableDates(), loadClassifications()]);
    setupEventListeners();
}

// Load classification categories from the server
async function loadClassifications() {
    try {
        const response = await fetch('/api/classifications');
        classifications = await response.json();

        // Populate dropdown (keep "unassigned" as first option)
        classifications.forEach(cls => {
            const option = document.createElement('option');
            option.value = cls;
            option.textContent = cls;
            classificationSelect.appendChild(option);
        });
    } catch (error) {
        showMessage('Error loading classifications: ' + error.message, 'error');
    }
}

// Load available dates from the server
async function loadAvailableDates() {
    try {
        const response = await fetch('/api/dates');
        const dates = await response.json();

        dateSelect.innerHTML = '<option value="">Select a date...</option>';
        dates.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = date;
            dateSelect.appendChild(option);
        });
    } catch (error) {
        showMessage('Error loading dates: ' + error.message, 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    loadBtn.addEventListener('click', loadPapers);
    prevBtn.addEventListener('click', showPreviousPaper);
    nextBtn.addEventListener('click', showNextPaper);

    scoreButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const score = parseInt(btn.dataset.score);
            setScore(score);
        });
    });

    classificationSelect.addEventListener('change', () => {
        setClassification(classificationSelect.value);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (!paperDisplay.style.display || paperDisplay.style.display === 'none') return;

        if (e.key === 'ArrowLeft') {
            showPreviousPaper();
        } else if (e.key === 'ArrowRight') {
            showNextPaper();
        } else if (e.key === '0') {
            setScore(0);
        } else if (e.key === '1') {
            setScore(1);
        } else if (e.key === '2') {
            setScore(2);
        }
    });
}

// Load papers for selected date
async function loadPapers() {
    const selectedDate = dateSelect.value;
    if (!selectedDate) {
        showMessage('Please select a date', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/papers/${selectedDate}`);
        const data = await response.json();

        rawPapers = data.raw;
        manualPapers = data.manual;
        currentDate = selectedDate;
        currentIndex = 0;

        paperDisplay.style.display = 'block';
        showPaper(currentIndex);
        updateStats();
        showMessage(`Loaded ${rawPapers.length} papers for ${selectedDate}`, 'success');

        setTimeout(() => {
            message.style.display = 'none';
        }, 3000);
    } catch (error) {
        showMessage('Error loading papers: ' + error.message, 'error');
    }
}

// Show paper at given index
function showPaper(index) {
    if (index < 0 || index >= rawPapers.length) return;

    currentIndex = index;
    const raw = rawPapers[index];
    const manual = manualPapers[index];

    paperTitle.textContent = raw.title;
    paperAbstract.textContent = raw.abstract || 'No abstract available';

    // Update analysed badge
    const isAnalysed = manual.analysed === true;
    analysedBadge.className = 'analysed-badge ' + (isAnalysed ? 'analysed' : 'not-analysed');
    analysedStatus.textContent = isAnalysed ? 'Analysed' : 'Not Analysed';

    // Update score display
    currentScore.textContent = `Current score: ${manual.score}`;
    updateScoreButtons(manual.score);

    // Update classification dropdown
    classificationSelect.value = manual.classification || 'unassigned';

    // Update navigation buttons
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === rawPapers.length - 1;

    // Update current index display
    currentIndexSpan.textContent = `Current: ${index + 1}/${rawPapers.length}`;
}

// Update score button states
function updateScoreButtons(score) {
    scoreButtons.forEach(btn => {
        if (parseInt(btn.dataset.score) === score) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Set score for current paper
async function setScore(score) {
    try {
        const pmid = rawPapers[currentIndex].pmid;

        const response = await fetch('/api/score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: currentDate,
                pmid: pmid,
                score: score
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save score');
        }

        // Update local state
        manualPapers[currentIndex].score = score;
        manualPapers[currentIndex].analysed = true;
        rawPapers[currentIndex].analysed = true;

        // Update display
        currentScore.textContent = `Current score: ${score}`;
        updateScoreButtons(score);
        analysedBadge.className = 'analysed-badge analysed';
        analysedStatus.textContent = 'Analysed';
        updateStats();

        showMessage('Score saved successfully', 'success');
        setTimeout(() => {
            message.style.display = 'none';
        }, 2000);

    } catch (error) {
        showMessage('Error saving score: ' + error.message, 'error');
    }
}

// Set classification for current paper
async function setClassification(classification) {
    try {
        const pmid = rawPapers[currentIndex].pmid;

        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: currentDate,
                pmid: pmid,
                classification: classification
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save classification');
        }

        // Update local state
        manualPapers[currentIndex].classification = classification;

        showMessage('Classification saved', 'success');
        setTimeout(() => {
            message.style.display = 'none';
        }, 2000);

    } catch (error) {
        showMessage('Error saving classification: ' + error.message, 'error');
    }
}

// Update statistics display
function updateStats() {
    const total = rawPapers.length;
    const analysed = manualPapers.filter(p => p.analysed === true).length;

    paperCount.textContent = `Total: ${total}`;
    analysedCount.textContent = `Analysed: ${analysed}`;
}

// Mark current paper as analysed (without changing score)
async function markCurrentAsAnalysed() {
    // Skip if already analysed
    if (manualPapers[currentIndex].analysed === true) {
        return;
    }

    try {
        const pmid = rawPapers[currentIndex].pmid;
        const currentScoreValue = manualPapers[currentIndex].score;

        const response = await fetch('/api/score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: currentDate,
                pmid: pmid,
                score: currentScoreValue
            })
        });

        if (!response.ok) {
            throw new Error('Failed to mark as analysed');
        }

        // Update local state
        manualPapers[currentIndex].analysed = true;
        rawPapers[currentIndex].analysed = true;
        updateStats();

    } catch (error) {
        console.error('Error marking as analysed:', error);
        // Don't show error message to user, just log it
    }
}

// Navigation functions
async function showPreviousPaper() {
    if (currentIndex > 0) {
        await markCurrentAsAnalysed();
        showPaper(currentIndex - 1);
    }
}

async function showNextPaper() {
    if (currentIndex < rawPapers.length - 1) {
        await markCurrentAsAnalysed();
        showPaper(currentIndex + 1);
    }
}

// Show message to user
function showMessage(text, type = 'success') {
    message.textContent = text;
    message.className = 'message ' + type;
    message.style.display = 'block';
}

// Initialize app
init();
