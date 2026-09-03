#!/usr/bin/env bash
#
# Typeset the notes. LaTeX is the source; Markdown is not involved.
#
#   ./docs/build.sh 05_modelling           one chapter, light
#   ./docs/build.sh 05_modelling --dark    the same chapter, dark page + dark figures
#   ./docs/build.sh --all                  every chapter under chapters/
#   ./docs/build.sh --book                 all_chapters.tex, the bound edition
#   ./docs/build.sh --figures --all        regenerate the PNGs first, then typeset
#
# Layout:
#
#   preamble.tex                     the one file that decides what things look like
#   chapters/<stem>/<stem>.tex       a body-only fragment: no \documentclass
#   chapters/<stem>/_build/          wrapper, .aux, .log, .toc -- scratch, gitignored
#   read_only_chapters/<stem>.pdf    the light PDF, and the only place a chapter PDF lives
#   all_chapters.pdf                 every chapter bound together
#
# A chapter .tex carries no layout instruction of its own, so swapping
# preamble.tex moves all of them at once.

set -euo pipefail

DOCS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$DOCS/read_only_chapters"
PYTHON="${PYTHON:-python3}"
THEME=light
FIGURES=0
BOOK=0
STEMS=()

all_stems() {
  for d in "$DOCS"/chapters/*/; do
    s="$(basename "$d")"
    [ -f "$d/$s.tex" ] && echo "$s"
  done
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dark)    THEME=dark ;;
    --light)   THEME=light ;;
    --figures) FIGURES=1 ;;
    --book)    BOOK=1 ;;
    --all)     while IFS= read -r s; do STEMS+=("$s"); done < <(all_stems) ;;
    -o)        shift; OUT="$1" ;;
    -*)        echo "unknown flag: $1" >&2; exit 2 ;;
    *)         STEMS+=("$(basename "${1%.tex}")") ;;
  esac
  shift
done

command -v pdflatex >/dev/null || { echo "pdflatex not found -- install MacTeX" >&2; exit 1; }

# Figures first, so a chapter never typesets against a stale PNG.
if [ "$FIGURES" = 1 ]; then
  for s in "$DOCS"/figures/*_figures/make_*.py; do
    printf '%-46s ' "$(basename "$s")"; "$PYTHON" "$s"
  done
fi

if [ ${#STEMS[@]} -eq 0 ] && [ "$BOOK" = 0 ] && [ "$FIGURES" = 1 ]; then exit 0; fi
if [ ${#STEMS[@]} -eq 0 ] && [ "$BOOK" = 0 ]; then
  echo "usage: build.sh <chapter> [--dark] | --all | --book | --figures" >&2; exit 2
fi

mkdir -p "$OUT"
cd "$DOCS"   # every path below -- graphicspath included -- is relative to docs/

# Twice: pass one writes the .toc and the \ref targets, pass two reads them
# back. Otherwise every cross-reference prints as "??".
run_twice() {   # run_twice <output-dir> <jobname> <tex-line>
  local dir=$1 job=$2 line=$3
  for _ in 1 2; do
    pdflatex -interaction=nonstopmode -halt-on-error \
             -output-directory="$dir" -jobname="$job" "$line" \
             > "$dir/$job.log" 2>&1 \
      || { echo "xxx $job failed:" >&2; grep -A4 '^!' "$dir/$job.log" | head -30 >&2; exit 1; }
  done
}

pages() { pdfinfo "$1" 2>/dev/null | awk '/^Pages/{print $2}'; }

for STEM in ${STEMS[@]+"${STEMS[@]}"}; do   # bash 3.2: an empty array is "unset" under set -u
  BODY="chapters/$STEM/$STEM.tex"
  [ -f "$BODY" ] || { echo "no such chapter: $DOCS/$BODY" >&2; exit 1; }
  WORK="chapters/$STEM/_build"
  mkdir -p "$WORK"

  # The wrapper. \DARKMODE is defined before \documentclass, which is how
  # preamble.tex learns which theme it is being built for.
  {
    if [ "$THEME" = dark ]; then echo '\def\DARKMODE{}'; fi
    echo '\input{preamble}'
    echo '\begin{document}'
    echo "\\input{chapters/$STEM/$STEM}"
    echo '\end{document}'
  } > "$WORK/$STEM-$THEME.tex"

  run_twice "$WORK" "$STEM-$THEME" "\\input{$WORK/$STEM-$THEME.tex}"

  # A chapter PDF lives in exactly one place. The light build is the published
  # one; dark is a reading convenience and stays in the chapter's scratch dir.
  if [ "$THEME" = light ]; then
    mv "$WORK/$STEM-light.pdf" "$OUT/$STEM.pdf"
    echo "--> read_only_chapters/$STEM.pdf  ($(pages "$OUT/$STEM.pdf") pages)"
  else
    echo "--> $WORK/$STEM-dark.pdf  ($(pages "$WORK/$STEM-dark.pdf") pages)"
  fi
done

if [ "$BOOK" = 1 ]; then
  WORK="_build"
  mkdir -p "$WORK"
  JOB="all_chapters-$THEME"
  PRE=''
  if [ "$THEME" = dark ]; then PRE='\def\DARKMODE{}'; fi
  run_twice "$WORK" "$JOB" "$PRE\\input{all_chapters.tex}"
  mv "$WORK/$JOB.pdf" "all_chapters.pdf"
  echo "--> docs/all_chapters.pdf  ($(pages all_chapters.pdf) pages)"
fi
