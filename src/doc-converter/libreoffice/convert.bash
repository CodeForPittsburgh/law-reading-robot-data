#!/usr/bin/env bash

if [ $# -ne 2 ]; then
  echo "Usage ./program <House Bill .doc URL> <Output filename>"
  exit 1
fi

URL="$1"
DOC_FILE="$(mktemp)"
HTML_FILE="$(mktemp --suffix=.html)"
PRETTY_HTML_FILE="$(mktemp --suffix=.html)"
OUT_FILE="out/$2"

echo "Downloading .doc file at '${URL}'"
curl -s "${URL}" > "${DOC_FILE}.doc"
echo "Converting .doc file to .docx with LibreOffice"
lowriter --convert-to docx --outdir "$(dirname ${DOC_FILE})" "${DOC_FILE}.doc" > out/libre_office.log 2>&1
echo "Converting .docx file to HTML with Mammoth JS"
npx mammoth ${DOC_FILE}.docx > "${HTML_FILE}" 2> out/mammoth.log
# Pretty printing the HTML is actually important as the whitespace it introduces is necessary to
# keep the extracted text from having runon words - e.g.
# ('<p>Hello</p><p>There</p>' -> 'HelloThere' vs '<p>Hello</p>\n<p>There</p>' -> 'Hello\nThere')
# This reliance is a source of brittleness, but unfortunately JSDOM does not support `innerText`
# just `textContent`.
# https://github.com/jsdom/jsdom/issues/1245
# https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent#differences_from_innertext
echo "Pretty formatting HTML to aid JSDOM"
tidy -config .tidyrc -o "${PRETTY_HTML_FILE}" -f out/tidy.log "${HTML_FILE}"
echo "Extracting non-stricken text"
node process.js "${PRETTY_HTML_FILE}" > "${OUT_FILE}"
exit 0
