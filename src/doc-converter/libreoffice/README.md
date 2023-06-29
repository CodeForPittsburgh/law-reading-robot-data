# .doc to HTML Converter

## Requirements

1. Docker
1. Make

## Run

1. Build image: `make build`
1. Run command: `URL="<House Bill .doc URL>" FILE="<output filename>" make run`

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
URL="${URL}" FILE="hb_612.txt" make run
```

Should place the converted bill in `out/hb_612.txt`. Note that the
strikethrough text is no longer present.
