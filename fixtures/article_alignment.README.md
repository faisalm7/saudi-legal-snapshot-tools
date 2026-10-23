# Synthetic article-alignment fixture

`article_alignment.json` contains entirely invented Arabic text and invented extracted-PDF lines. It is not a law, judgment, government document, or quotation from the user's collection. Its numbers, dates, article labels and cross-references exist solely to exercise exact offsets, an ordinal beyond eleven, and ambiguous reference handling.

The tests pass a digest of this invented evidence string as a deterministic stand-in for the PDF hash supplied by the caller. These unit tests do not pretend to validate a real PDF or official legal segmentation. They verify that the mapper carries evidence unchanged and never rewrites the provided body.

This fixture may accompany code under the code license and must not be counted as a source document in the corpus.
