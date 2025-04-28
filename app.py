import logging
import string
from collections import Counter

import altair as alt
import circlify  # Required for circle packing layout
import nltk
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

# --- Streamlit Page Configuration (MUST BE FIRST st command) ---
st.set_page_config(page_title="HTML Text Extractor & Analyzer", layout="wide")

# --- NLTK Data Download ---
try:
    nltk.data.find("corpora/stopwords")
    logging.info("NLTK 'stopwords' data found.")
except LookupError:
    st.info("⏳ Downloading NLTK 'stopwords' data (needed once)...")
    try:
        nltk.download("stopwords", quiet=True)
        logging.info("NLTK 'stopwords' downloaded successfully.")
    except Exception as e:
        st.warning(
            f"Could not download NLTK stopwords: {e}. Word frequency chart might not filter common words."
        )
        logging.error(f"NLTK stopwords download failed: {e}")

try:
    nltk.data.find("tokenizers/punkt")
    logging.info("NLTK 'punkt' tokenizer found.")
except LookupError:
    st.info("⏳ Downloading NLTK 'punkt' tokenizer (needed once)...")
    try:
        nltk.download("punkt", quiet=True)
        logging.info("NLTK 'punkt' downloaded successfully.")
    except Exception as e:
        st.warning(
            f"Could not download NLTK punkt: {e}. Word frequency chart might fail."
        )
        logging.error(f"NLTK punkt download failed: {e}")

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# --- Helper Function to Fetch and Parse ---
def fetch_and_parse_url(target_url):
    """Fetches a URL, parses its HTML content, and extracts text."""
    if not target_url.startswith(("http://", "https://")):
        schemes_to_try = ["https://", "http://"]
    else:
        schemes_to_try = [target_url]

    last_error = None
    full_url = ""
    response_for_error = None

    for scheme in schemes_to_try:
        if scheme in ["https://", "http://"]:
            current_url_attempt = scheme + target_url.split("://", 1)[-1]
        else:
            current_url_attempt = scheme

        full_url = current_url_attempt
        logging.info(f"Attempting to fetch URL: {full_url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(full_url, headers=headers, timeout=20)
            response_for_error = response
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                logging.warning(
                    f"URL {full_url} returned non-HTML content: {content_type}"
                )
                last_error = f"URL returned non-HTML content: {content_type}. Please provide a URL pointing to an HTML page."
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text_content = soup.get_text(separator=" ", strip=True)

            logging.info(f"Successfully parsed text from {full_url}")
            return True, text_content

        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while fetching {full_url}")
            last_error = f"Timeout: The request to {full_url} took too long to respond."
            continue
        except requests.exceptions.SSLError as e:
            logging.error(f"SSL Error for {full_url}: {e}")
            last_error = f"SSL Error for {full_url}. The site might use outdated security, or you might need to specify http:// explicitly."
            continue
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL {full_url}: {e}")
            error_message = str(e)
            if isinstance(e, requests.exceptions.ConnectionError):
                error_message = f"Could not connect to {full_url}. Check the URL or network connection."
            elif isinstance(e, requests.exceptions.HTTPError):
                status_code = (
                    response_for_error.status_code if response_for_error else "N/A"
                )
                reason = response_for_error.reason if response_for_error else "N/A"
                error_message = (
                    f"Request to {full_url} failed: Status {status_code} ({reason})."
                )

            last_error = error_message
            if isinstance(e, requests.exceptions.HTTPError):
                break  # Stop trying schemes on HTTP errors

    logging.error(f"Failed to fetch/parse '{target_url}'. Last error: {last_error}")
    return False, last_error or f"Could not retrieve or parse the URL '{target_url}'."


# --- Helper Function for Word Frequency Analysis ---
def analyze_text_frequency(text, top_n=50):
    """Analyzes text to find word frequencies after cleaning and removing stopwords."""
    if not text:
        return None

    try:
        stop_words = set(stopwords.words("english"))
    except LookupError:
        st.warning(
            "Stopwords list not found. Frequency analysis might include common words."
        )
        stop_words = set()

    try:
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))

        try:
            tokens = nltk.word_tokenize(text)
        except LookupError:
            st.warning("Punkt tokenizer not found. Using basic split().")
            tokens = text.split()

        filtered_words = [
            word for word in tokens if word.isalpha() and word not in stop_words
        ]

        if not filtered_words:
            return None

        word_counts = Counter(filtered_words)
        common_words = word_counts.most_common(top_n)
        df = pd.DataFrame(common_words, columns=["word", "frequency"])
        return df

    except Exception as e:
        logging.error(f"Error during text frequency analysis: {e}")
        st.warning(f"Could not analyze word frequency: {e}")
        return None


# --- Streamlit User Interface ---

st.title("🌐 HTML Content to Text Extractor & Word Analyzer")
st.markdown(
    "Enter a URL to fetch its HTML content, extract plain text, and visualize word frequency using circle packing."
)

url_input = st.text_input(
    "Enter URL:", placeholder="e.g., www.google.com or https://example.com"
)

fetch_button = st.button("Fetch and Analyze")

if fetch_button:
    if not url_input:
        st.warning("⚠️ Please enter a URL.")
    else:
        cleaned_url = url_input.strip()
        st.info(f"⏳ Fetching and parsing '{cleaned_url}'...")

        with st.spinner("Processing... Please wait."):
            success, result = fetch_and_parse_url(cleaned_url)

        if success:
            st.success("✅ Successfully extracted text:")
            st.text_area("Extracted Text:", result, height=300)

            st.markdown("---")
            st.subheader("📊 Word Frequency Analysis (Packed Bubble Chart)")

            word_freq_df = analyze_text_frequency(result, top_n=75)

            if word_freq_df is not None and not word_freq_df.empty:
                st.info("⚙️ Computing circle packing layout...")
                data_for_circlify = [
                    {"id": d["word"], "datum": d["frequency"]}
                    for d in word_freq_df.to_dict("records")
                ]

                try:
                    packed_circles = circlify.circlify(
                        data_for_circlify,
                        show_enclosure=False,
                        target_enclosure=circlify.Circle(x=0, y=0, r=1),
                    )
                    st.info("✅ Layout computed.")

                    plot_data = []
                    for circle in packed_circles:
                        plot_data.append(
                            {
                                "word": circle.ex["id"],
                                "frequency": circle.ex["datum"],
                                "x": circle.x,
                                "y": circle.y,
                                "radius": circle.r,  # Use original radius
                            }
                        )
                    plot_df = pd.DataFrame(plot_data)

                    plot_df["label_text"] = (
                        plot_df["word"] + "\n" + plot_df["frequency"].astype(str)
                    )
                    min_radius_for_label = 0.05  # Adjust this threshold as needed

                    # --- Create Altair Chart using calculated layout ---
                    base = alt.Chart(plot_df).encode(
                        x=alt.X("x", axis=None),
                        y=alt.Y("y", axis=None),
                    )

                    bubbles = base.mark_circle().encode(
                        # Size using original radius
                        size=alt.Size(
                            "radius",
                            scale=alt.Scale(
                                range=[1, 5000]
                            ),  # Adjust range based on radius values
                            legend=None,
                        ),
                        color=alt.Color(
                            "word", legend=None, scale=alt.Scale(scheme="category20")
                        ),
                        tooltip=["word", "frequency", "radius"],
                    )

                    labels = base.mark_text(
                        align="center",
                        baseline="middle",
                        fontSize=9,
                        fontWeight="normal",
                    ).encode(
                        text="label_text",
                        color=alt.value("white"),
                        opacity=alt.condition(
                            alt.datum.radius >= min_radius_for_label,
                            alt.value(0.8),
                            alt.value(0),
                        ),
                    )

                    chart = (
                        (bubbles + labels)
                        .properties(
                            title=f"Top {len(plot_df)} Most Frequent Words (Packed Layout)"
                        )
                        .configure_view(
                            strokeWidth=0  # Remove chart border
                        )
                        .interactive()
                    )

                    st.altair_chart(chart, use_container_width=True)
                    st.caption("Circle packing layout. Hover for details.")

                except Exception as e:
                    st.error(f"❌ Error during circle packing layout: {e}")
                    logging.error(f"Circlify layout error: {e}")

            else:
                st.info(
                    "ℹ️ No significant words found after cleaning or text was empty."
                )

        else:
            st.error(f"❌ Error: {result}")

st.markdown("---")
st.markdown(
    "*(Note: Analysis excludes common English 'stopwords'. Does not render JavaScript.)*"
)
