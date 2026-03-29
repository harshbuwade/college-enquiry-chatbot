import nltk
import ssl
import os

# Disable SSL verification for downloading (if needed)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print("Downloading NLTK data...")

# Download required NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')  # This is the missing one causing the 500 error!
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

print("NLTK data downloaded successfully!")