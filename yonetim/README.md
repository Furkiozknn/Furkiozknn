# Merkezi proje yönetimi

21 oyun, ortak altyapı (arena-core), video stüdyosu, sosyal medya ve portal işlerinin tek takip yeri.

- `gorevler.json`: **tek kaynak.** Her görev: `id` (G-NNN), `baslik`, `durum`, `oncelik` (P0-P3), `alan`,
  `bagimli`, `not`; tamamlananlarda `kanit` + `kapandi`, engellenenlerde `engel.neden` + `engel.gereken`.
- `portfoy.json`: oyun başına kit sürümü, video, Instagram ve portal durumu. Kit sütunu
  `python3 yonetim/pano.py --tara <klonlar>` ile klonlardan okunur.
- `PANO.md`: üretilir, elle düzenlenmez: `python3 yonetim/pano.py`.

Durumlar: Bekliyor, Devam Ediyor, Test Ediliyor, Tamamlandı, Engellendi. Tamamlanan görev aktif listeden
geçmişe iner ama kanıtıyla kalır. Aynı başlıklı iki aktif görev olamaz. Bağımlılığı bitmemiş görev
"hazır değil" görünür; "Sıradaki iş" hazır görevlerin en öncelikli olanıdır.

Her çalışma döngüsü: durumu oku → işi seç → uygula → test et → kanıtla kapat → yeni işleri ekle →
`python3 yonetim/pano.py` → commit. CI `test_pano.py` ve `pano.py --kontrol` koşar.
