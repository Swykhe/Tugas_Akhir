# Bersihkan karakter U+00A0 dari file Python kamu
with open('ta.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Ganti non-breaking space dengan spasi biasa
cleaned = content.replace('\u00A0', ' ')

with open('ta.py', 'w', encoding='utf-8') as file:
    file.write(cleaned)

print("Karakter U+00A0 berhasil dihapus.")
