# marimo

While I'm still nostalgic for Sweave and tidyverse, this repository is for testing marimo. For a practical example, converting an old notebook for SIR models into an interactive marimo app that can be a GitHub Page

* SIR Notebook Rnw: https://github.com/j23414/sir_models

## Setup

```
marimo edit sir_model.py
marimo export html-wasm sir_model.py -o docs
cd docs
npx serve
```

## Live Site

* https://j23414.github.io/marimo
