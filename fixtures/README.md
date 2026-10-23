# Synthetic fixtures

All fixture text was created for these tests with AI assistance. It is not copied from a law, judgment, government portal, or private collection and makes no statement of applicable law. Dates, amounts, title, status and UUID are invented test values.

`synthetic_boe.json` imitates the input schema only. Its BOE-shaped URL uses a synthetic UUID so URL-validation logic can be exercised locally. Tests never request that URL. `expected_body.txt` is the independently specified expected faithful Arabic body after the documented whitespace and NFC changes. Search normalization is tested separately.

These fixtures may accompany the processing code under its code license. They must not be mixed with the actual dataset or counted as official documents. Tests create their own temporary source and state directories and do not read the original collection.
