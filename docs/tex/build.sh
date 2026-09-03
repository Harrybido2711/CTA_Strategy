#!/usr/bin/env bash
#
# Compile a chapter body into its own PDF, in both themes.
#
#   ./docs/tex/build.sh 05-modelling          # light + dark
#   ./docs/tex/build.sh 05-modelling --light  # just one
#   ./docs/tex/build.sh --all
#
# Each chapter .tex is a body-only fragment: no \documentclass, no
# \begin{document}. This script wraps it around preamble.tex, so the
# layout lives in exactly one file and swapping it moves every chapter.
#
# Output lands in docs/_pdf/ (gitignored).

set -euo pipefail

TEXDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$TEXDIR/../_pdf"
WORK="$TEXDIR/_build"
THEMES=()
FILES=()

while [ $# -gt 0 ]; do
  case "$1" in
    --light) THEMES+=(light) ;;
    --dark)  THEMES+=(dark) ;;
    --all)   while IFS= read -r f; do FILES+=("$(basename "$f" .tex)"); done \
               < <(find "$TEXDIR" -maxdepth 1 -name '[0-9]*.tex' | sort) ;;
    -o)      shift; OUT="$1" ;;
    -*)      echo "unknown flag: $1" >&2; exit 2 ;;
    *)       FILES+=("$(basename "$1" .tex)") ;;
  esac
  shift
done

[ ${#THEMES[@]} -gt 0 ] || THEMES=(light dark)
[ ${#FILES[@]} -gt 0 ] || { echo "usage: build.sh <chapter> [--light|--dark] | --all" >&2; exit 2; }

command -v pdflatex >/dev/null || { echo "pdflatex not found -- install MacTeX" >&2; exit 1; }

mkdir -p "$OUT" "$WORK"
cd "$TEXDIR"

for STEM in "${FILES[@]}"; do
  [ -f "$STEM.tex" ] || { echo "no such chapter: $TEXDIR/$STEM.tex" >&2; exit 1; }

  for THEME in "${THEMES[@]}"; do
    JOB="$STEM-$THEME"

    # The wrapper. \DARKMODE is defined before \documentclass, which is
    # how preamble.tex learns which theme it is being built for.
    {
      [ "$THEME" = dark ] && echo '\def\DARKMODE{}'
      echo '\input{preamble}'
      echo '\begin{document}'
      echo "\\input{$STEM}"
      echo '\end{document}'
    } > "$WORK/$JOB.tex"

    # Twice: pass one writes the .toc and the \ref targets, pass two
    # reads them back. Otherwise every cross-reference prints as "??".
    for _ in 1 2; do
      pdflatex -interaction=nonstopmode -halt-on-error \
               -output-directory="$WORK" "$WORK/$JOB.tex" > "$WORK/$JOB.log" 2>&1 \
        || { echo "xxx $JOB failed:" >&2; grep -A4 '^!' "$WORK/$JOB.log" | head -30 >&2; exit 1; }
    done

    cp "$WORK/$JOB.pdf" "$OUT/$JOB.pdf"
    echo "--> $OUT/$JOB.pdf  ($(pdfinfo "$OUT/$JOB.pdf" 2>/dev/null | awk '/^Pages/{print $2}') pages)"
  done
done
