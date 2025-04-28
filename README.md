# 🌐 HTML Text Extractor & Word Analyzer

![screenshot](screenshot.png)

A web application built with Streamlit that allows users to enter a URL, fetch its HTML content, parse it to extract plain text, and then analyze and visualize the word frequency as a packed bubble chart.

## Features

*   Fetches content from a given URL (attempts HTTPS first, then HTTP if no scheme is provided).
*   Parses the raw HTML source code using BeautifulSoup.
*   Extracts text content, removing content from `<script>` and `<style>` tags.
*   Analyzes extracted text to calculate word frequencies (using NLTK).
*   Removes common English stopwords and punctuation before analysis.
*   Visualizes the most frequent words as an interactive packed bubble chart (using Circlify for layout and Altair for plotting).
*   Displays word and frequency labels inside larger bubbles.
*   Provides a simple web interface for URL input and displays extracted text, the visualization, or relevant error messages.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python:** Version 3.8 or higher recommended.
*   **pip:** Python package installer (usually comes with Python).

## Installation

1.  **Get the Code:** Make sure you have the application script (e.g., `app.py`) saved on your local machine.

2.  **Install Dependencies:** Open your terminal or command prompt, navigate to the directory where you saved the script, and run the following command to install the required Python libraries:

    ```bash
    pip install streamlit requests beautifulsoup4 pandas altair nltk circlify numpy
    ```

3.  **NLTK Data:** The first time you run the app, it may need to download necessary data packages (`stopwords`, `punkt`) from NLTK. The application attempts to do this automatically and will show status messages in the Streamlit interface. Ensure you have an internet connection during the first run.

## Running the Application

1.  **Navigate:** Open your terminal or command prompt and change to the directory containing the `app.py` file.

2.  **Run Streamlit:** Execute the following command:

    ```bash
    streamlit run app.py
    ```

3.  **Access the App:** Streamlit will start a local web server and should automatically open the application in your default web browser. If it doesn't, the terminal output will provide local and network URLs (usually starting with `http://localhost:8501`) that you can navigate to manually.

## How to Use

1.  Once the application is open in your browser, you will see a title and an input field labeled "Enter URL:".
2.  Type or paste the full URL of the website you want to extract text from (e.g., `www.google.com`, `https://example.com`, `https://en.wikipedia.org/wiki/Python_(programming_language)`).
3.  Click the "Fetch and Analyze" button.
4.  The application will show loading indicators while it fetches, parses, and analyzes the URL.
5.  If successful, the extracted plain text content will be displayed in a text area, followed by the interactive packed bubble chart visualizing word frequencies. Hover over bubbles for details (word and frequency).
6.  If an error occurs (e.g., invalid URL, network timeout, site blocking, non-HTML content, analysis issues), an error message detailing the issue will be shown instead.

## Limitations

*   **No JavaScript Execution:** This tool parses the initial HTML source. It **does not** execute JavaScript. Content loaded dynamically after the initial page load will be missed.
*   **Website Blocking:** Some websites may block automated scraping attempts. This tool may not work on all websites.
*   **Parsing Accuracy:** Complex or malformed HTML might lead to imperfect text extraction.
*   **Analysis Specificity:** Word frequency analysis uses standard English stopwords. Results may be less meaningful for non-English text or highly specialized content. Tokenization accuracy depends on NLTK's models.
*   **Visualization Layout:** The circle packing visualization uses an algorithm (`circlify`) to arrange bubbles. The exact layout appearance depends on the data and the algorithm's output. Very small bubbles might not display labels clearly.
*   **Basic Error Handling:** Handles common errors but may not cover all edge cases.