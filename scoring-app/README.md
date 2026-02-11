# Article Scoring Web App

A simple web application for manually scoring research articles from PubMed searches.

## Features

- Load papers from any date in the data directory
- View title and abstract for each paper
- Score papers (0 = Not Relevant, 1 = Maybe, 2 = Relevant)
- Track which papers have been analysed
- Navigate through papers with Next/Previous buttons
- Keyboard shortcuts for faster scoring
- Real-time statistics (total papers, analysed count)

## Usage

1. Start the server:
   ```bash
   cd scoring-app
   python server.py
   ```

2. Open your browser to: http://localhost:8000

3. Select a date from the dropdown and click "Load Papers"

4. Review each paper and score it using the buttons or keyboard shortcuts

## Keyboard Shortcuts

- **0, 1, 2**: Set score for current paper
- **←** (Left Arrow): Previous paper
- **→** (Right Arrow): Next paper

## How It Works

The app reads from two JSON files for each date:
- `papers_raw_YYYY-MM-DD.json`: Contains full article metadata (title, abstract, etc.)
- `papers_for_manual_YYYY-MM-DD.json`: Contains scoring data (pmid, title, score)

When you score a paper:
1. The score is saved to `papers_for_manual_*.json`
2. An `analysed` field is set to `true` in both JSON files
3. Statistics update automatically

## Files

- `index.html`: Main HTML structure
- `styles.css`: CSS styling
- `app.js`: Frontend JavaScript logic
- `server.py`: Python backend server for file operations
- `README.md`: This file

## Requirements

- Python 3.12+
- Modern web browser (Chrome, Firefox, Safari, Edge)
