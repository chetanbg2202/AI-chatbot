"""
setup_nltk.py
-------------
One-time NLTK resource downloader.
Run this script before starting the chatbot for the first time:

    python setup_nltk.py
"""

import sys
# Force UTF-8 output to avoid UnicodeEncodeError on Windows cp1252 consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import nltk

RESOURCES = [
    "punkt_tab",
    "stopwords",
    "wordnet",
    "omw-1.4",
]

print("Downloading required NLTK resources...\n")
for pkg_name in RESOURCES:
    print(f"  Downloading {pkg_name}...", end=" ")
    nltk.download(pkg_name, quiet=True)
    print("done")

print("\nAll NLTK resources are ready. You can now run the chatbot.")
print("Run:  python -m streamlit run app.py")
