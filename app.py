import logging

import requests
import streamlit as st
from bs4 import BeautifulSoup

# Configure basic logging (optional, logs to console where Streamlit runs)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# --- Helper Function to Fetch and Parse (Modified for Streamlit feedback) ---
def fetch_and_parse_url(target_url):
    """
    Fetches a URL, parses its HTML content, and extracts text.

    Args:
        target_url (str): The URL to fetch and parse (including scheme if provided).

    Returns:
        tuple: (success, result)
               success (bool): True if successful, False if an error occurred.
               result (str): Parsed text content if successful, or an error message string if failed.
    """
    # --- 1. Prepend scheme if missing ---
    if not target_url.startswith(("http://", "https://")):
        # Try https first, then http as a fallback
        schemes_to_try = ["https://", "http://"]
    else:
        schemes_to_try = [target_url]  # Already has a scheme

    last_error = None
    full_url = ""

    for scheme in schemes_to_try:
        if scheme in ["https://", "http://"]:
            current_url_attempt = (
                scheme + target_url.split("://", 1)[-1]
            )  # Handle if user typed http:// but we try https://
        else:
            current_url_attempt = scheme  # Use the full URL as is

        full_url = (
            current_url_attempt  # Keep track of the last tried URL for error messages
        )
        logging.info(f"Attempting to fetch URL: {full_url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            # --- 2. Make the HTTP GET request ---
            response = requests.get(
                full_url, headers=headers, timeout=20
            )  # Increased timeout slightly

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            # --- 3. Check Content-Type ---
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                logging.warning(
                    f"URL {full_url} returned non-HTML content: {content_type}"
                )
                # Continue to next scheme if possible, otherwise this will be the error
                last_error = f"URL returned non-HTML content: {content_type}. Please provide a URL pointing to an HTML page."
                continue  # Try http if https failed here

            # --- 4. Parse HTML with BeautifulSoup ---
            soup = BeautifulSoup(response.content, "html.parser")  # Or 'lxml'

            # --- 5. Extract Text ---
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text_content = soup.get_text(separator=" ", strip=True)

            logging.info(f"Successfully parsed text from {full_url}")
            return True, text_content  # Success! Return the text

        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while fetching {full_url}")
            last_error = f"Timeout: The request to {full_url} took too long to respond."
            # Don't immediately return, maybe the other scheme works
            continue
        except requests.exceptions.SSLError as e:
            logging.error(f"SSL Error for {full_url}: {e}")
            last_error = f"SSL Error for {full_url}. The site might use outdated security, or you might need to specify http:// explicitly."
            # Often happens when trying https on a site that only supports http
            continue
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL {full_url}: {e}")
            error_message = str(e)
            if isinstance(e, requests.exceptions.ConnectionError):
                error_message = f"Could not connect to {full_url}. Check the URL, your network connection, or try specifying http:// or https://."
            elif isinstance(e, requests.exceptions.HTTPError):
                error_message = f"Request to {full_url} failed with status code {response.status_code} ({response.reason})."

            last_error = error_message
            # If it's a 4xx/5xx error, trying the other scheme probably won't help, but connection errors might
            if not isinstance(e, requests.exceptions.ConnectionError):
                break  # Stop trying other schemes for definite errors like 404

    # If loop finished without returning success
    logging.error(
        f"Failed to fetch and parse '{target_url}' after trying schemes. Last error: {last_error}"
    )
    return (
        False,
        last_error
        if last_error
        else f"Could not retrieve or parse the URL '{target_url}' after trying available schemes.",
    )


# --- Streamlit User Interface ---

st.set_page_config(page_title="HTML Text Extractor", layout="wide")

st.title("🌐 HTML Content to Text Extractor")
st.markdown("Enter a URL below to fetch its HTML content and extract the plain text.")

# Input field for the URL
url_input = st.text_input(
    "Enter URL:", placeholder="e.g., www.google.com or https://example.com"
)

# Button to trigger the process
fetch_button = st.button("Fetch and Extract Text")

if fetch_button:
    if not url_input:
        st.warning("⚠️ Please enter a URL.")
    else:
        cleaned_url = url_input.strip()
        st.info(f"⏳ Fetching and parsing '{cleaned_url}'...")

        # Use a spinner for better user feedback during processing
        with st.spinner("Processing... Please wait."):
            success, result = fetch_and_parse_url(cleaned_url)

        if success:
            st.success("✅ Successfully extracted text:")
            # Display the extracted text in a text area (good for large text, allows copying)
            st.text_area("Extracted Text:", result, height=400)
        else:
            # Display the error message
            st.error(f"❌ Error: {result}")

st.markdown("---")
st.markdown(
    "*(Note: This tool extracts text from the raw HTML source. It does not render JavaScript, so content loaded dynamically after the initial page load might be missed.)*"
)
