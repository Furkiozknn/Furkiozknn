# Kişisel Web Sitesi Planı — aboutdean.framer.website Analizinden Yola Çıkarak

**Amaç:** İleride özel bir domain alındığında, `aboutdean.framer.website` kalitesinde ama tamamen özgün bir kişisel site kurmak için somut yol haritası. Detaylı ham analiz: `research/raw/E_framer_site_analysis.md`.

---

## 1. Önemli Keşif

`aboutdean.framer.website` bir bireyin özel sitesi değil, **Framer Marketplace'te satılan "Dean" adlı bir portfolyo şablonunun canlı demo sayfası** (`framer.com/marketplace/templates/dean/`). Bu aslında ilham kaynağı olarak daha değerli: şablon demo sayfaları, potansiyel alıcıya en iyi pratiği göstermek için özenle kurulur.

`*.framer.website` alt alan adı, Framer'ın özel domain bağlanmamış sitelerin varsayılan yayın adresidir — bu, sitenin no-code Framer builder ile yapıldığının en güçlü kanıtı. Framer siteleri React runtime tabanlı bir SPA olarak derlenir, kendi CDN'inde barındırılır ve native HTML export sunmaz.

---

## 2. Sayfa Yapısı (Bu Şablon Kategorisinin Tipik Anatomisi)

1. Sabit/minimal navigasyon (logo + birkaç anchor link + belirgin CTA)
2. Hero — kısa çarpıcı başlık + alt başlık + CTA, büyük portre/avatar
3. (Opsiyonel) sosyal kanıt şeridi — müşteri logoları/istatistikler
4. Hakkımda + 4 adımlı süreç anlatımı (konuşma → konsept → iterasyon → teslim)
5. CMS-yönetimli proje/iş grid'i (Framer Collections)
6. Hizmetler bölümü
7. Referanslar (carousel/grid)
8. Rezervasyon takvimi + iletişim formu
9. Footer

## 3. Tasarım Dili

- **Tipografi:** Büyük, güven veren display font (modern grotesk — Inter/General Sans/Neue Montreal tarzı), 3 kademeli tip ölçeği, geniş satır yüksekliği.
- **Renk:** Kısıtlı nötr taban (açık/koyu tema, token-tabanlı) + tek vurgu rengi sadece CTA/link için.
- **Boşluk:** Cömert negatif alan, ortalanmış max-width kolon, bölümler arası büyük dikey padding.
- **Bileşenler:** Yeniden kullanılabilir Framer bileşenleri (nav, CTA, testimonial, servis kartı, footer) — tutarlı bir sistem gibi okunuyor.
- **Etkileşim:** Scroll-tetiklemeli fade/slide-in (grid'lerde staggered), hover mikro-etkileşimleri, tema geçişinde yumuşak cross-fade, spring tabanlı buton geri bildirimi.

---

## 4. İki Yol: Framer (no-code) vs. Next.js (hand-coded)

| | **Framer (no-code)** | **Next.js + Tailwind + Motion/GSAP** |
|---|---|---|
| Hıza en uygun | Evet — saatler/günler | Hayır — günler/haftalar |
| Tam yaratıcı/teknik tavan (özel mantık, WebGL) | Code Components ile sınırlı | Sınırsız |
| Sahiplik/taşınabilirlik | Framer platformuna bağımlı | Tamamen bize ait, düz Git repo |
| Sürekli maliyet | Abonelik (koltuk/plan başına) | Sadece hosting (çoğu zaman Vercel free-tier) |
| Kime uygun | Hızlı yayına almak, görsel iterasyon isteyen | Zaten kod yazan, siteyi mühendislik+tasarım kanıtı olarak da kullanmak isteyen, platform kilidi istemeyen |

**Öneri: Next.js + Tailwind + Framer Motion/GSAP yolu.** Zaten kod yazıyoruz, özgün (klonlanmamış) bir sonuç istiyoruz ve site kendisi bir portfolyo kanıtı olsun istiyoruz — bu üç kriter de kod yazma tarafını işaret ediyor.

### Somut stack
- **Next.js 15+ (App Router)** + **Tailwind CSS 4** (opsiyonel shadcn/ui erişilebilir primitifler için)
- **Framer Motion** (`motion` paketi) component-seviyesi mikro-etkileşimler için; **GSAP + ScrollTrigger** sadece pinned section / scrub-linked animasyon gibi Framer Motion'ın zayıf olduğu karmaşık senaryolarda
- **Lenis** — sinematik yumuşak kaydırma hissi için (opsiyonel)
- İçerik katmanı: headless CMS (Sanity/Contentful) veya tipli local MDX/JSON — Framer Collections'ın kod karşılığı
- Tipografi: `clamp()` ile akıcı tip ölçeği, bir display + bir body font, maksimum 2-3 ağırlık
- Renk: CSS custom properties / Tailwind token'ları, `data-theme` veya `prefers-color-scheme` ile açık/koyu
- Performans: Framer'ın ~800KB runtime yükü yok — bunu koru: code-splitting, `next/image`, Lighthouse denetimi
- Deploy: Vercel + özel domain

### Motion tasarım prensipleri
- Scroll-tetiklemeli reveal (`whileInView` / `ScrollTrigger.batch`), grid'lerde staggered children
- Spring tabanlı hover/tap geri bildirimi
- Native CSS scroll-driven animations ve View Transitions API — bazı basit senaryolarda JS kütüphanesi ihtiyacını azaltıyor (2026 itibarıyla üretime hazır)

---

## 5. Adım Adım Uygulama Planı

1. Tasarım token'larını tanımla (renk, tip ölçeği, spacing) — kod yazmadan önce.
2. Next.js + Tailwind iskeletini kur, açık/koyu tema desteğini en baştan ekle.
3. İçerik modelini kur (projeler/deneyim/yazılar için tipli MDX veya headless CMS).
4. Bölümleri sırayla inşa et: nav → hero → hakkımda → proje grid'i → (varsa) hizmetler → iletişim → footer.
5. Framer Motion ile temel scroll-reveal ve hover mikro-etkileşimlerini ekle; abartıdan kaçın — "restraint premium okunur."
6. Lighthouse/erişilebilirlik denetimi yap, performans bütçesini koru.
7. Vercel'e deploy et, özel domain bağlandığında SEO/OG/JSON-LD detaylarını tamamla.

---

## Kaynaklar

Detaylı kaynak listesi ve tam analiz için: [`research/raw/E_framer_site_analysis.md`](./raw/E_framer_site_analysis.md)
