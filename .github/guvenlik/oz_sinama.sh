#!/usr/bin/env bash
# Guvenlik kapisinin oz sinamasi: kapi GERCEK depoyu taramadan once,
# kirmiziya donebildigini kanitlar. "Tarayici 0 dondu" ancak ayni
# tarayici bilinen kotu bir girdide 0 disinda donuyorsa bir sey soyler.
#
# Sahte anahtarlar calisma aninda parcalardan kurulur; bu dosyada
# tarayicinin yakalayacagi bir dizi yoktur (yoksa depo kendi kendini
# kirmiziya boyar). Hicbiri gercek bir kimlik bilgisi degildir.
#
# Kullanim: oz_sinama.sh zizmor|betterleaks   (araclar PATH'te olmali)
set -uo pipefail

KOK=$(cd "$(dirname "$0")/../.." && pwd)
CFG="$KOK/.github/guvenlik"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
hata=0

bekle() { # ad beklenen gercek
  if [ "$2" = "$3" ]; then echo "  ok    $1 (cikis $3)"
  else echo "  HATA  $1: beklenen cikis $2, gelen $3"; hata=1; fi
}

yeni_depo() {
  rm -rf "$T/d"; mkdir -p "$T/d"
  git -C "$T/d" init -q
  git -C "$T/d" config user.email oz@sinama.invalid
  git -C "$T/d" config user.name oz-sinama
}

isle() { git -C "$T/d" add -A && git -C "$T/d" commit -qm x; }

case "${1:-}" in
zizmor)
  z() { zizmor --offline --persona=regular --min-severity low \
          --config "$CFG/zizmor.yml" --format plain "$T/d" >/dev/null 2>&1; echo $?; }
  yeni_depo; mkdir -p "$T/d/.github/workflows"
  # 1) temiz: actions/* etiketle (politika izin veriyor), izin yok, kimlik kalmiyor
  cat > "$T/d/.github/workflows/a.yml" <<'EOF'
name: a
on: [push]
permissions: {}
jobs:
  j:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - run: echo merhaba
EOF
  bekle "temiz is akisi" 0 "$(z)"
  # 2) ucuncu taraf eylem etiketle -> hash-pin politikasi
  sed -i 's|      - run: echo merhaba|      - uses: someone/tool@v1\n      - run: echo merhaba|' "$T/d/.github/workflows/a.yml"
  r=$(z); [ "$r" != 0 ] && r=kirmizi; bekle "pinsiz ucuncu taraf eylem" kirmizi "$r"
  # 3) sablon enjeksiyonu
  cat > "$T/d/.github/workflows/a.yml" <<'EOF'
name: a
on: [pull_request_target]
permissions: {}
jobs:
  j:
    runs-on: ubuntu-24.04
    steps:
      - run: echo "${{ github.event.pull_request.title }}"
EOF
  r=$(z); [ "$r" != 0 ] && r=kirmizi; bekle "sablon enjeksiyonu" kirmizi "$r"
  ;;
betterleaks)
  b() { betterleaks git --no-banner --redact --exit-code 1 --ignore-gitleaks-allow \
          -i "$CFG" --config "$CFG/betterleaks.toml" "$T/d" >/dev/null 2>&1; echo $?; }
  # Uydurma, deterministik; dusuk entropili bir dizi (ornegin tekrar eden
  # bir parca) tarayicinin entropi esigine takilir ve tarayici 0 doner
  # (sahte yesil). Bu oz sinamanin ilk surumu tam olarak bunu yakaladi.
  sahte="ghp_$(printf oz-sinama | sha256sum | base64 -w0 | tr -dc 'A-Za-z0-9' | cut -c1-36)"
  yeni_depo; echo "merhaba" > "$T/d/a.txt"; isle
  bekle "temiz gecmis" 0 "$(b)"
  # 2) gecmiste kalan anahtar (sonraki commit silse bile)
  echo "token = \"$sahte\"" > "$T/d/b.txt"; isle
  git -C "$T/d" rm -q b.txt; isle
  bekle "silinmis ama gecmiste duran anahtar" 1 "$(b)"
  # 3) kilit.json istisnasi dar mi: 64 hex gecer, gercek anahtar gecmez
  yeni_depo; mkdir -p "$T/d/.claude/skills"
  printf '{\n  "a/kapi.py": "%s"\n}\n' "$(printf 'ab%.0s' $(seq 32))" > "$T/d/.claude/skills/kilit.json"; isle
  bekle "kilit.json sha256 ozeti (istisna)" 0 "$(b)"
  printf '{\n  "a/kapi.py": "%s"\n}\n' "$sahte" > "$T/d/.claude/skills/kilit.json"; isle
  bekle "kilit.json icinde anahtar (istisna disi)" 1 "$(b)"
  # 4) satir ici 'gitleaks:allow' yorumu kapiyi susturamaz
  yeni_depo; echo "token = \"$sahte\" # gitleaks:allow" > "$T/d/c.txt"; isle
  bekle "satir ici allow yorumu yok sayilir" 1 "$(b)"
  ;;
*) echo "kullanim: $0 zizmor|betterleaks" >&2; exit 2 ;;
esac

[ "$hata" = 0 ] && echo "oz sinama: $1 kirmiziya donebiliyor" || echo "oz sinama: $1 BASARISIZ"
exit "$hata"
