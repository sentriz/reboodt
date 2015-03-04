import markdown
import os

current_folder = os.path.dirname(__file__)
markdown_file = os.path.join(current_folder, "README.md")
html_file = os.path.join(current_folder, "index.html")

markdown.markdownFromFile(markdown_file, output=html_file)