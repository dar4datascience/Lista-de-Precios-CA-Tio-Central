# test tabulizer vs tabulapdf all require java
#https://github.com/ropensci/tabulapdf
# not working
library(tabulapdf)
f <- "pdfs/lista de precios vol 9.pdf"

another_bad_example <- "https://databankfiles.worldbank.org/public/ddpext_download/GDP.pdf"

worldexample <- extract_tables(another_bad_example, method = "stream")

check_tables <- extract_tables(f, pages = 2, method = "stream")

# first_table <- locate_areas(f, pages = 2)[[1]]
#
# outnew <- extract_tables(f, pages = 2, area = list(first_table), guess = FALSE)
#
# second_table <- locate_areas(f, pages = 3)[[1]]
#
# third_table <- locate_areas(f, pages = 4)[[1]]
#
# fourth_table <- locate_areas(f, pages = 5)[[1]]
#
# fifth_table <- locate_areas(f, pages = 6)[[1]]
#
# sixth_table <- locate_areas(f, pages = 7)[[1]]
#
# seventh_table <- locate_areas(f, pages = 8)[[1]]
#
# eighth_table <- locate_areas(f, pages = 9)[[1]]
#
# ninth_table <- locate_areas(f, pages = 10)[[1]]
#
# tenth_table <- locate_areas(f, pages = 11)[[1]]
#
# eleventh_table <- locate_areas(f, pages = 12)[[1]]
#
pngfile <- pdftools::pdf_convert("pdfs/lista de precios vol 8.pdf", dpi = 400)
# library(tesseract)
# eng <- tesseract("spa")
# text <- tesseract::ocr(pngfile[2], engine = eng)
# cat(text)
