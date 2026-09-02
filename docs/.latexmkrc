# fontspec/unicode-math need xelatex; pdflatex dies at the first \setmainfont.
$pdf_mode = 5;          # 5 = xelatex
$postscript_mode = $dvi_mode = 0;

# Keep docs/ free of .aux/.log/.toc clutter. docs/_pdf/ is gitignored.
$out_dir = '_pdf';
$aux_dir = '_pdf';
