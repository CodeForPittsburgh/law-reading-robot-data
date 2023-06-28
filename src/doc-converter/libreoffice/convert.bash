#!/usr/bin/env bash

if [ $# -ne 2 ]; then
  echo "Usage ./program <House Bill .doc URL> <Output filename>"
  exit 1
fi

URL="$1"
DOC_FILE="$(mktemp)"
HTML_FILE="$(mktemp --suffix=html)"
OUT_FILE="out/$2"

echo "Downloading .doc file at '${URL}'"
curl -s "${URL}" > "${DOC_FILE}.doc"
echo "Converting .doc file to .docx with LibreOffice"
lowriter --convert-to docx --outdir "$(dirname ${DOC_FILE})" "${DOC_FILE}.doc" > out/libre_office.log 2>&1
echo "Converting .docx file to HTML with Mammoth JS"
npx mammoth ${DOC_FILE}.docx > "${HTML_FILE}" 2>out/mammoth.log
echo "Pretty formatting HTML into '${OUT_FILE}'"
tidy -config .tidyrc -o "${OUT_FILE}" -f out/tidy.log "${HTML_FILE}" 
