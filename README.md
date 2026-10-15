# LSEG × ENS asset registry demo

An interactive, static presentation showing how assets named under `lseg.com`
could carry token addresses and identifiers across Ethereum, Solana, and Stellar.
The sample assets and identifiers are fictional.

Open `index.html` locally or deploy this repository as a static site. It needs no
build step or server API. For GitHub Pages, publish from the root of `main`. For
Vercel, import this repository with the root directory and default static settings.

The eight-slide deck follows the downloaded ENS Labs concept in `../lseg-demo`,
with its ENS design system bundled in `assets/ens.css`. Browser-save scripts are
removed. Fonts use the stylesheet's hosted fonts and system fallbacks.

CSV imports and new sample assets live only in page memory and reset on reload.
The demo does not write onchain or verify ENS or vLEI records.

Run the deck and typography lint before publishing:

```sh
python3 lint.py
```
