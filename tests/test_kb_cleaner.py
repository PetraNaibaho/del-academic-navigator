"""Unit tests for Document Text Cleaner module (src/kb/cleaner.py).

Tests Unicode normalization (NFKC), hyphenation repair,
repetitive header/footer/page removal, whitespace normalization,
structural preservation, and edge cases (empty text, stats accuracy).
"""

import pytest
from src.kb.cleaner import CleaningStats, TextCleaner


@pytest.fixture
def cleaner() -> TextCleaner:
    return TextCleaner()


def test_cleaner_empty_string(cleaner: TextCleaner):
    cleaned, stats = cleaner.clean_with_stats("")
    assert cleaned == ""
    assert stats.original_chars == 0
    assert stats.cleaned_chars == 0
    assert stats.original_words == 0
    assert stats.cleaned_words == 0
    assert stats.char_reduction_pct == 0.0


def test_cleaner_whitespace_only(cleaner: TextCleaner):
    cleaned, stats = cleaner.clean_with_stats("   \n\n\t  \n  ")
    assert cleaned == ""
    assert stats.cleaned_words == 0


def test_cleaner_unicode_nfkc_normalization(cleaner: TextCleaner):
    # Ligatures (e.g., 'ﬁ' -> 'fi', 'ﬀ' -> 'ff', full-width characters)
    raw = "Veriﬁkasi jadwal perkuliahan ﬀokus pada evaluasi ＡＢＣ."
    cleaned = cleaner.clean(raw)
    assert "Verifikasi" in cleaned
    assert "fokus" in cleaned
    assert "ABC" in cleaned


def test_cleaner_hyphenation_across_linebreaks(cleaner: TextCleaner):
    # Hyphenated words across line breaks should be merged into single words
    raw = (
        "Dosen pengampu wajib mengajukan permo-\n"
        "honan kuliah pengganti paling lambat dua hari kerja sebelum pembe- \n"
        "lajaran tatap muka dimulai."
    )
    cleaned, stats = cleaner.clean_with_stats(raw)
    assert "permohonan" in cleaned
    assert "pembelajaran" in cleaned
    assert "permo-\nhonan" not in cleaned
    assert stats.hyphens_fixed_count >= 2


def test_cleaner_header_footer_removal(cleaner: TextCleaner):
    raw = (
        "INSTITUT TEKNOLOGI DEL - DOKUMEN RESMI\n"
        "BAB I: KETENTUAN UMUM\n"
        "Setiap mahasiswa wajib mematuhi aturan asrama.\n"
        "Halaman 1 dari 12\n"
        "Page 2 of 5\n"
        "Institut Teknologi Del – Sistem Manajemen Pengetahuan Enterprise\n"
        "BAB II: SANKSI DISIPLIN\n"
        "Halaman 3\n"
    )
    cleaned, stats = cleaner.clean_with_stats(raw)
    assert "INSTITUT TEKNOLOGI DEL - DOKUMEN RESMI" not in cleaned
    assert "Halaman 1 dari 12" not in cleaned
    assert "Page 2 of 5" not in cleaned
    assert "Halaman 3" not in cleaned
    assert "BAB I: KETENTUAN UMUM" in cleaned
    assert "BAB II: SANKSI DISIPLIN" in cleaned
    assert stats.headers_footers_removed_count >= 4


def test_cleaner_whitespace_normalization(cleaner: TextCleaner):
    raw = "Paragraf 1    dengan   spasi    berlebih.\n\n\n\n\nParagraf 2 setelah spasi kosong banyak."
    cleaned = cleaner.clean(raw)
    assert "    " not in cleaned
    assert "\n\n\n" not in cleaned
    assert "Paragraf 1 dengan spasi berlebih.\n\nParagraf 2 setelah spasi kosong banyak." == cleaned


def test_cleaner_structure_preservation(cleaner: TextCleaner):
    # Ensure article numbers, bullet points, and section titles remain intact
    raw = """
## BAB III: ALOKASI DAN UTILISASI RUANGAN
1. Kelas Paralel (> 40 Mahasiswa):
   - Wajib menempati ruang GD721 atau GD722.
   - Kapasitas ruangan mencukupi kebutuhan rombel.
2. Sesi Praktikum Laboratorium:
   - Dilaksanakan di Lab Komputer GD911.
"""
    cleaned = cleaner.clean(raw)
    assert "## BAB III: ALOKASI DAN UTILISASI RUANGAN" in cleaned
    assert "1. Kelas Paralel (> 40 Mahasiswa):" in cleaned
    assert "- Wajib menempati ruang GD721 atau GD722." in cleaned
    assert "2. Sesi Praktikum Laboratorium:" in cleaned
    assert "- Dilaksanakan di Lab Komputer GD911." in cleaned


def test_cleaner_stats_accuracy(cleaner: TextCleaner):
    raw = (
        "INSTITUT TEKNOLOGI DEL - DOKUMEN RESMI\n"
        "Peraturan ini mengatur pelak- \n"
        "sanaan kuliah pengganti.\n"
        "Halaman 1 dari 5"
    )
    cleaned, stats = cleaner.clean_with_stats(raw)
    assert isinstance(stats, CleaningStats)
    assert stats.original_chars > stats.cleaned_chars
    assert stats.char_reduction_pct > 0.0
    assert stats.hyphens_fixed_count == 1
    assert stats.headers_footers_removed_count == 2
    assert "pelaksanaan" in cleaned
