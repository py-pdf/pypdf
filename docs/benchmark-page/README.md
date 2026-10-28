# Benchmark page

The page at <https://py-pdf.github.io/pypdf/dev/bench/> shows how fast pypdf is
after every commit to `main`. This folder holds the page and this description of
how it is built. All code lives on `main`; the `gh-pages` branch only holds the
published copy and the results.

## How it works

```mermaid
flowchart LR
    push["Commit to main"] --> bench["benchmark job<br>(CPython, PyPy)"]
    bench -->|calibrated.json| publish["publish job"]
    publish -->|"index.html, archive"| pages["gh-pages:<br>dev/bench/"]
    publish -->|"data.js via<br>github-action-benchmark"| pages
    pages --> site["py-pdf.github.io/pypdf/dev/bench/"]
```

1. **Measure.** On every push to `main`, the `benchmark` job of
   [benchmark.yaml](../../.github/workflows/benchmark.yaml) runs
   [tests/bench.py](../../tests/bench.py) with pytest-benchmark, once on
   CPython and once on PyPy.
2. **Calibrate.** GitHub runners differ in speed by up to a factor of two.
   `tests/bench.py` therefore contains `test_calibration`, a fixed workload that
   does not use pypdf.
   [calibrate_benchmarks.py](../../.github/scripts/calibrate_benchmarks.py)
   divides the median time of every other benchmark by the median time of the
   calibration, and adds the machine (CPU, cores, Python version) to each
   result. The job uploads the raw and the calibrated results as an artifact
   and shows a table in the job summary.
3. **Publish.** The `publish` job is the only one allowed to write to the
   repository, and the only one that pushes to `gh-pages`, so the two matrix
   jobs cannot race each other. It:
   1. copies [index.html](index.html) to `gh-pages:dev/bench/index.html` and
      runs [archive_uncalibrated_results.py](archive_uncalibrated_results.py)
      (see below), then commits and pushes if anything changed;
   2. hands the calibrated results to
      [github-action-benchmark](https://github.com/benchmark-action/github-action-benchmark),
      which appends them to `gh-pages:dev/bench/data.js`, writes a comparison
      table to the job summary and fails the job if a CPython benchmark got
      more than 1.5× slower than on the previous commit. PyPy never fails the
      job.
4. **Serve.** GitHub Pages serves the `gh-pages` branch. The page reads
   `data.js` and draws the charts in the browser.

## What lives where

### On `main`

| File | Purpose |
| --- | --- |
| [tests/bench.py](../../tests/bench.py) | The benchmarks, including `test_calibration`. |
| [.github/scripts/calibrate_benchmarks.py](../../.github/scripts/calibrate_benchmarks.py) | Divides by the calibration, prints a table and writes the input for github-action-benchmark. |
| [.github/workflows/benchmark.yaml](../../.github/workflows/benchmark.yaml) | Runs the benchmarks and publishes everything. |
| [docs/benchmark-page/index.html](index.html) | The page. One self-contained file without external scripts or fonts. |
| [docs/benchmark-page/archive_uncalibrated_results.py](archive_uncalibrated_results.py) | Moves the results from before the calibration into the archive. |
| [Makefile](../../Makefile) | `make benchmark` runs the benchmarks locally and prints calibrated values. |

### On `gh-pages`

Everything here is generated. Do not edit it by hand: the workflow overwrites
`index.html` on the next commit to `main`.

| File | Written by | Content |
| --- | --- | --- |
| `dev/bench/index.html` | `publish` job | A copy of [index.html](index.html). |
| `dev/bench/data.js` | github-action-benchmark | `window.BENCHMARK_DATA`, the calibrated results in the suites `CPython (calibrated)` and `PyPy (calibrated)`. |
| `dev/bench/archive/before-calibration.js` | `archive_uncalibrated_results.py`, once | `window.BENCHMARK_ARCHIVE`, the results from before the calibration (CPython since April 2022, PyPy since December 2025). Nothing changes it afterwards. |
| `dev/bench/ng.html` | nobody | An older dashboard. It is no longer maintained and can be deleted. |
| `index.html` | nobody | Redirects the root of the site to the documentation on Read the Docs. |

### Repository settings

- **Pages:** *Settings → Pages* must deploy from the branch `gh-pages`, folder
  `/ (root)`. Then `gh-pages:dev/bench/index.html` is served at `/dev/bench/`.
- **Actions:** the workflow needs no secrets. It pushes with the built-in
  `GITHUB_TOKEN`, so *Settings → Actions → General → Workflow permissions* must
  not forbid `contents: write` for jobs that ask for it.

## The data

`data.js` and the archive have the format of github-action-benchmark:

```js
window.BENCHMARK_DATA = {
  "lastUpdate": 1793184154794,          // milliseconds since 1970
  "repoUrl": "https://github.com/py-pdf/pypdf",
  "entries": {
    "CPython (calibrated)": [           // one entry per commit, oldest first
      {
        "commit": { "id": "c7d391c2…", "message": "…", "timestamp": "…", "url": "…", "author": { "name": "…" } },
        "date": 1793184154794,          // when the benchmark ran
        "tool": "customSmallerIsBetter",
        "benches": [
          {
            "name": "page_operations",
            "unit": "x calibration",
            "value": 3.8801,              // median time / calibration time
            "range": "IQR: 0.1215",
            "extra": "median: 618.7 ms\nrounds: 10\ncalibration: 159.5 ms\nmachine: Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz (8 cores), CPython 3.10.2"
          }
        ]
      }
    ]
  }
};
```

The archive uses `window.BENCHMARK_ARCHIVE` instead, the suites
`CPython Benchmark` and `PyPy Benchmark`, the tool `pytest` and the unit
`iter/sec` (higher is faster). Its numbers cannot be compared with the
calibrated ones, which is why the page shows them in a separate view.

### The one-time archive step

Until the calibration was introduced, github-action-benchmark wrote the
uncalibrated suites into `data.js`. On its first run, the `publish` job moves
them unchanged into `dev/bench/archive/before-calibration.js`. On every later
run the script sees that the archive exists and does nothing. The previous
`data.js` also stays in the history of `gh-pages`.

## Working on the page

The page is plain HTML, CSS and JavaScript in one file. To try a change with
the real data, run this in the root of the repository:

```sh
repo=$(pwd)
site=$(mktemp -d)
mkdir -p "$site/dev/bench/archive"
cp docs/benchmark-page/index.html "$site/dev/bench/"
git fetch origin gh-pages
git show origin/gh-pages:dev/bench/data.js > "$site/dev/bench/data.js"
if git cat-file -e origin/gh-pages:dev/bench/archive/before-calibration.js 2>/dev/null; then
  git show origin/gh-pages:dev/bench/archive/before-calibration.js > "$site/dev/bench/archive/before-calibration.js"
else
  # The workflow has not archived the old results yet; do it in the copy.
  (cd "$site" && python "$repo/docs/benchmark-page/archive_uncalibrated_results.py")
fi
xdg-open "$site/dev/bench/index.html"   # macOS: open
```

Keep the page free of external scripts, stylesheets and fonts. It then needs no
updates when a CDN version gets old, and it sends no visitor data to third
parties. Check it at 320 px width: nothing may scroll sideways.

## Changing the benchmarks

- **Never change `calibration_workload` in `tests/bench.py`.** All published
  values are relative to it. If it has to change, start new suites by renaming
  them in `benchmark.yaml` (for example `CPython (calibration 2)`) and archive
  the old ones the same way as above.
- **Adding a benchmark** is fine. Its chart starts with the next commit.
- **Renaming a benchmark** starts a new chart. The old one stays in `data.js`
  under its old name.
- **Changing what a benchmark measures** creates a step in its chart. Mention
  it in the commit message, so that the step can be explained later.
- Keep file access and assertions out of the timed functions. They only add
  noise.

## Comparing with your machine

```sh
make benchmark
```

prints the calibrated values for your machine, in the same unit as the page.
They are close to the published values, but not identical: how much faster one
CPU runs pypdf than the calibration still depends a little on the CPU and the
Python version. Compare the version without and with your change on the same
machine to measure the change itself.
