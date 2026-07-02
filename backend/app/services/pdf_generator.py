from __future__ import annotations

from pathlib import Path


def _escape_pdf_text(value: str) -> str:
	return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def generate_application_pdf(application_reference: str, lines: list[str], output_dir: str = "storage") -> str:
	"""Generate a minimal PDF file with application summary lines."""
	root = Path(output_dir)
	root.mkdir(parents=True, exist_ok=True)
	pdf_path = root / f"{application_reference}.pdf"

	max_lines = min(20, len(lines))
	text_commands = ["BT", "/F1 12 Tf", "50 770 Td"]
	for index in range(max_lines):
		escaped = _escape_pdf_text(lines[index])
		if index > 0:
			text_commands.append("0 -18 Td")
		text_commands.append(f"({escaped}) Tj")
	text_commands.append("ET")
	stream_data = "\n".join(text_commands).encode("utf-8")

	objects: list[bytes] = []
	objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
	objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
	objects.append(
		b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
	)
	objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
	objects.append(
		b"5 0 obj << /Length " + str(len(stream_data)).encode("utf-8") + b" >> stream\n" + stream_data + b"\nendstream endobj\n"
	)

	content = bytearray(b"%PDF-1.4\n")
	xref_offsets = [0]
	for obj in objects:
		xref_offsets.append(len(content))
		content.extend(obj)

	xref_start = len(content)
	content.extend(f"xref\n0 {len(xref_offsets)}\n".encode("utf-8"))
	content.extend(b"0000000000 65535 f \n")
	for offset in xref_offsets[1:]:
		content.extend(f"{offset:010d} 00000 n \n".encode("utf-8"))

	content.extend(
		(
			f"trailer\n<< /Size {len(xref_offsets)} /Root 1 0 R >>\n"
			f"startxref\n{xref_start}\n%%EOF\n"
		).encode("utf-8")
	)

	pdf_path.write_bytes(content)
	return str(pdf_path)

