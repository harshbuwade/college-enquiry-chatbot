"""
download_nltk.py
Run once to download all required NLTK corpora.
Usage: python download_nltk.py
"""
import nltk

packages = [
    'punkt',
    'punkt_tab',
    'stopwords',
    'wordnet',
    'averaged_perceptron_tagger',
    'omw-1.4',
]

print('Downloading NLTK data...')
for pkg in packages:
    nltk.download(pkg, quiet=False)

print('\n✅ All NLTK data downloaded successfully.')
