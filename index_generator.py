#!/usr/bin/env python3
"""
Index page generator for neXco Chapter Dashboard.
Generates the chapter listing HTML page.
"""

import html

from file_writer import atomic_write_text


INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>neXco Chapter Dashboards</title>
    <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
    <header class="dashboard-header">
        <a href="https://nexconational.com/" target="_blank" rel="noopener noreferrer">
            <img src="assets/img/nexco-logo.png" alt="neXco National" class="logo">
        </a>
        <h1>neXco Chapter Dashboards</h1>
    </header>
    <main>
        <nav class="chapter-list">
            <ul>
{chapter_list}
            </ul>
        </nav>
    </main>
</body>
</html>
'''


def generate_index_html(chapters: list, output_path: str) -> None:
    """
    Generate the chapter index HTML page.

    Args:
        chapters: List of ChapterConfig objects
        output_path: Path to write index.html
    """
    # Sort chapters alphabetically by display_name
    sorted_chapters = sorted(chapters, key=lambda c: c.display_name.lower())

    # Build list items
    lines = []
    for chapter in sorted_chapters:
        escaped_name = html.escape(chapter.display_name)
        escaped_slug = html.escape(chapter.chapter_slug)
        lines.append(f'                <li><a href="{escaped_slug}/">{escaped_name}</a></li>')

    chapter_list = "\n".join(lines)

    # Generate HTML
    html_content = INDEX_TEMPLATE.format(chapter_list=chapter_list)

    # Write atomically
    atomic_write_text(html_content, output_path)


if __name__ == "__main__":
    print("Index generator module loaded successfully")
