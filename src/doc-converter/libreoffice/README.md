# .doc to HTML Converter

## Requirements

Docker

## Run

1. Build image: `docker compose build`
1. Run command: `docker compose run convert <House Bill .doc URL> <output filename>`

Note that the output file will be placed in the `out/` directory which is
mounted as a volume and the `<output filename>` should just be a filename and
 not a path (no directories.)

## Example

A bill with strikethrough text is House Bill 612
([HTML](https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=HTM&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=612&pn=1703),
[DOC](https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=DOC&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=612&pn=1703))
with an appropriations strikethrough near the bottom of the text.

Running

```bash
URL='https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=DOC&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=612&pn=1703'
docker compose run convert "$URL" hb_612.html
```

Should place the converted bill in `out/hb_612.html`.  Note that the
strikethrough is preserved as simple `<s></s>` elements.
