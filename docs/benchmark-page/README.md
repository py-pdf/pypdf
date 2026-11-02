# Benchmark page

The pages at <https://py-pdf.github.io/pypdf/dev/bench/> show how fast pypdf is
after every commit to `main`:

* [index.html](index.html): one chart per benchmark.
* [ng.html](ng.html): a dashboard with zoom, release markers and commit details.

## How it works

1. On every push to `main`,
   [benchmark.yaml](../../.github/workflows/benchmark.yaml) runs
   [tests/bench.py](../../tests/bench.py) with pytest-benchmark, once on
   CPython and once on PyPy. If another push arrives while it runs, the run
   is cancelled and that commit gets no data point.
2. [github-action-benchmark](https://github.com/benchmark-action/github-action-benchmark)
   appends the results to `gh-pages:dev/bench/data.js`.
3. After both runs, the `publish` job copies [index.html](index.html) and
   [ng.html](ng.html) to `gh-pages:dev/bench/`, and commits and pushes them
   if they changed.
4. GitHub Pages serves the `gh-pages` branch. The pages load `data.js` and
   draw the charts in the browser with Chart.js.

## Changing the pages

Edit [index.html](index.html) or [ng.html](ng.html) on `main` and open a PR as
usual. Do not edit the files in `dev/bench/` on `gh-pages` directly: the next
benchmark run overwrites them.

The pages load their JavaScript libraries from jsDelivr, pinned to a version
and with an SRI hash. Every Monday,
[gh-pages-check.yaml](../../.github/workflows/gh-pages-check.yaml) checks the
pages in this directory for newer versions. If it fails, update the version and
the `integrity` attribute that it prints here on `main`.

To try a page locally, download `data.js` next to it and serve the folder:

```bash
cd docs/benchmark-page
curl -O https://py-pdf.github.io/pypdf/dev/bench/data.js
python -m http.server
```

Then open <http://localhost:8000/> or <http://localhost:8000/ng.html>.
Do not commit `data.js`.
