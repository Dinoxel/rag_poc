"""
Token calculation and reporting for text documents.
Uses tiktoken cl100k_base encoding (GPT-4, GPT-3.5-turbo compatible).
"""

import os
from pathlib import Path

import tiktoken

# Initialize tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return len(tokenizer.encode(text))


# Configuration
SCRIPT_DIR = Path(__file__).parent
DOCUMENT_DIR = Path("./document")
REPORT_PATH = DOCUMENT_DIR / "token_report.txt"


def main():
    """Process all .txt files and generate token count report."""
    if not DOCUMENT_DIR.exists():
        raise FileNotFoundError(f"Directory not found: {DOCUMENT_DIR}")

    txt_files = list(DOCUMENT_DIR.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in documents directory.")

    # Initialize report
    report_lines = []
    total_tokens = 0

    report_lines.append("Token Count Report")
    report_lines.append("=" * 50)
    report_lines.append("")

    # Process each file
    for file_path in txt_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        token_count = count_tokens(content)
        total_tokens += token_count

        report_lines.append(f"File: {file_path.name}")
        report_lines.append(f"Token count: {token_count}")
        report_lines.append("-" * 50)

    # Add summary
    report_lines.append("")
    report_lines.append("Summary")
    report_lines.append("=" * 50)
    report_lines.append(f"Number of documents: {len(txt_files)}")
    report_lines.append(f"Total tokens: {total_tokens}")

    # Save report
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Token report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
