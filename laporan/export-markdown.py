from markdown_pdf import MarkdownPdf, Section

with open("main.md", "r", encoding="utf-8") as f:
    md_text = f.read()

pdf = MarkdownPdf()
pdf.add_section(Section(md_text))
pdf.save("laporan.pdf")