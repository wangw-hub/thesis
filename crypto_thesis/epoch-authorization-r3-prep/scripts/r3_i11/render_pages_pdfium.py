import pypdfium2 as pdfium, sys, pathlib
pdf = pathlib.Path(sys.argv[1])
outdir = pathlib.Path(sys.argv[2])
doc = pdfium.PdfDocument(str(pdf))
scale = 90 / 72.0
for i in range(len(doc)):
    page = doc[i]
    img = page.render(scale=scale).to_pil()
    img.save(outdir / ('page-%03d.png' % (i + 1)))
print('pages', len(doc))
