window.BENCHMARK_DATA = {
  "lastUpdate": 1664343057875,
  "repoUrl": "https://github.com/py-pdf/PyPDF2",
  "entries": {
    "Python Benchmark with pytest-benchmark": [
      {
        "commit": {
          "author": {
            "name": "py-pdf",
            "username": "py-pdf"
          },
          "committer": {
            "name": "py-pdf",
            "username": "py-pdf"
          },
          "id": "1305df628fc63ed70829902edf934ab186b112c7",
          "message": "Add Benchmark for Performance Testing",
          "timestamp": "2022-04-19T10:36:47Z",
          "url": "https://github.com/py-pdf/PyPDF2/pull/781/commits/1305df628fc63ed70829902edf934ab186b112c7"
        },
        "date": 1650371123811,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9324214668863358,
            "unit": "iter/sec",
            "range": "stddev: 0.004305996984652197",
            "extra": "mean: 1.0724763806 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "py-pdf",
            "username": "py-pdf"
          },
          "committer": {
            "name": "py-pdf",
            "username": "py-pdf"
          },
          "id": "3dac50386da3c6d310d4a9ece804bc140e8e0798",
          "message": "Add Benchmark for Performance Testing",
          "timestamp": "2022-04-19T10:36:47Z",
          "url": "https://github.com/py-pdf/PyPDF2/pull/781/commits/3dac50386da3c6d310d4a9ece804bc140e8e0798"
        },
        "date": 1650372088110,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9422550305909239,
            "unit": "iter/sec",
            "range": "stddev: 0.006487516920717905",
            "extra": "mean: 1.0612838005999947 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.256656597871526,
            "unit": "iter/sec",
            "range": "stddev: 0.004297642398638799",
            "extra": "mean: 97.49765827272809 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f0f1fa3641cf1cda96e1bb1a655493617df5281c",
          "message": "DEV: Add Benchmark for Performance Testing (#781)\n\nWe want to track performance over time only for what actually\r\nis in main.\r\n\r\nCloses #761",
          "timestamp": "2022-04-21T18:19:24+02:00",
          "tree_id": "1eaf5ea1f69a7068b51ebe29334edb8c75efe091",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f0f1fa3641cf1cda96e1bb1a655493617df5281c"
        },
        "date": 1650557998642,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0526627229158771,
            "unit": "iter/sec",
            "range": "stddev: 0.0067697065658216754",
            "extra": "mean: 949.9718934000043 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.38381983307977,
            "unit": "iter/sec",
            "range": "stddev: 0.004719622305106786",
            "extra": "mean: 87.84397633333423 msec\nrounds: 12"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "668869f17988284e260c30b39c47eb26e033df54",
          "message": "DOC: Add compression example (#792)",
          "timestamp": "2022-04-22T08:10:05+02:00",
          "tree_id": "50ce3e1e74b68984df1ee6d33fddab8e41c6054a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/668869f17988284e260c30b39c47eb26e033df54"
        },
        "date": 1650607837510,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9530085273748775,
            "unit": "iter/sec",
            "range": "stddev: 0.012098282851842536",
            "extra": "mean: 1.049308554199996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.434029435085847,
            "unit": "iter/sec",
            "range": "stddev: 0.0046057474193716705",
            "extra": "mean: 95.84025099999849 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ffb208478144c2dc8f7ee9a4038f2c1c85ac99df",
          "message": "ENH: Allow setting form field flags (#802)\n\nCloses #574\r\nCloses #801\r\n\r\nCo-authored-by: Craig Jones <craig@k6nnl.com>",
          "timestamp": "2022-04-23T10:17:57+02:00",
          "tree_id": "730c99cfa0a0db24008b5ec4faf861825b15be0a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ffb208478144c2dc8f7ee9a4038f2c1c85ac99df"
        },
        "date": 1650701907682,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.05365515080177,
            "unit": "iter/sec",
            "range": "stddev: 0.005612559551809395",
            "extra": "mean: 949.0771238000008 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.561522963694742,
            "unit": "iter/sec",
            "range": "stddev: 0.0038475156847702775",
            "extra": "mean: 86.49379525000118 msec\nrounds: 12"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "40df4d7622c8b838a631113ced680d021070dd80",
          "message": "ENH: Allow setting permission flags when encrypting (#803)\n\nCloses #161\r\nCloses #308",
          "timestamp": "2022-04-23T10:43:54+02:00",
          "tree_id": "908a8418f3c819e228019736692c867df495166a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/40df4d7622c8b838a631113ced680d021070dd80"
        },
        "date": 1650703469764,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.950078836259226,
            "unit": "iter/sec",
            "range": "stddev: 0.005702058684478769",
            "extra": "mean: 1.0525442330000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.280940522982494,
            "unit": "iter/sec",
            "range": "stddev: 0.00423528362980359",
            "extra": "mean: 97.26736554545309 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3d659389e7561c024b5ffb9edd810e94814fa63e",
          "message": "ROB: Handle recursion error (#804)\n\nThis doesn't solve the issue, but it might make it less severe.\r\n\r\nSee #520\r\nSee #268\r\nSee https://github.com/virantha/pypdfocr/issues/59\r\n\r\nhttps://github.com/sfneal/PyPDF3/commit/3558a69388b12bbf166d81b8a863b1d6c9843c62\r\n\r\nCo-authored-by: danniesim <geemee@gmail.com>",
          "timestamp": "2022-04-23T10:57:54+02:00",
          "tree_id": "bc451d9cfc50cc3ba097311c2ed29028491f0ef3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3d659389e7561c024b5ffb9edd810e94814fa63e"
        },
        "date": 1650704308997,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9304874995964462,
            "unit": "iter/sec",
            "range": "stddev: 0.005964200812272813",
            "extra": "mean: 1.0747054640000016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.056596564428304,
            "unit": "iter/sec",
            "range": "stddev: 0.0035597955706618586",
            "extra": "mean: 99.43721949999969 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9941099b80dee1db6bfc747535b9d822b0fb0617",
          "message": "TST: Newlines in text extraction (#807)",
          "timestamp": "2022-04-23T14:50:17+02:00",
          "tree_id": "5c94513b4178944e0e5a534e1dce9dbc1e9d4f80",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9941099b80dee1db6bfc747535b9d822b0fb0617"
        },
        "date": 1650718254429,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9236413346619341,
            "unit": "iter/sec",
            "range": "stddev: 0.004035420224873149",
            "extra": "mean: 1.0826713384000015 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.939253390400175,
            "unit": "iter/sec",
            "range": "stddev: 0.0038204766514719417",
            "extra": "mean: 100.61117879999415 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "jensg@posteo.de",
            "name": "dsk7",
            "username": "dsk7"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c6c56f550bb384e05f0139c796ba1308837d6373",
          "message": "MAINT: Quadratic runtime while parsing reduced to linear  (#808)\n\nWhen the PdfFileReader tries to find the xref marker, the readNextEndLine methods builds a so called line by reading byte-for-byte. Every time a new byte is read, it is concatenated with the currently read line. This leads to quadratic runtime O(n²) behavior as Python strings (also byte-strings) are immutable and have to be copied where n is the size of the file.\r\nFor files where the xref marker can not be found at the end this takes a enormous amount of time:\r\n\r\n* 1mb of zeros at the end: 45.54 seconds\r\n* 2mb of zeros at the end: 357.04 seconds\r\n(measured on a laptop made in 2015)\r\n\r\nThis pull request changes the relevant section of the code to become linear runtime O(n), leading to a run time of less then a second for both cases mentioned above. Furthermore this PR adds a regression test.",
          "timestamp": "2022-04-23T19:12:13+02:00",
          "tree_id": "808b058c26b46591b397469807b07d8e66b9f34c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c6c56f550bb384e05f0139c796ba1308837d6373"
        },
        "date": 1650733971283,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8009431525956788,
            "unit": "iter/sec",
            "range": "stddev: 0.03857775783449113",
            "extra": "mean: 1.2485280593999988 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.39094445470576,
            "unit": "iter/sec",
            "range": "stddev: 0.006776916663739223",
            "extra": "mean: 119.17609577777455 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d4c8cab3292ccc52117ad1b38a10262640dfc158",
          "message": "BUG: Fix PDFDocEncoding Character Set (#809)\n\nCloses #151",
          "timestamp": "2022-04-23T22:27:38+02:00",
          "tree_id": "0b6a206e03da2af191d7509479c739e2d3f99f89",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d4c8cab3292ccc52117ad1b38a10262640dfc158"
        },
        "date": 1650745704204,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5706882244432586,
            "unit": "iter/sec",
            "range": "stddev: 0.014223725815557052",
            "extra": "mean: 1.752270254000004 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.80955246084517,
            "unit": "iter/sec",
            "range": "stddev: 0.004528453099679591",
            "extra": "mean: 113.51314433333452 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d1be80dff6b3dee50fe742ad39ddc9621785dd4f",
          "message": "BUG: Improve spacing for text extraction (#806)\n\nPyPDF2 now takes positive / negative spaces between text blocks into account. Not very elegant, but the result looks way better than before.",
          "timestamp": "2022-04-23T22:49:16+02:00",
          "tree_id": "0a6aa3c32ef620aef177d4b8768221b45e0b7202",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d1be80dff6b3dee50fe742ad39ddc9621785dd4f"
        },
        "date": 1650746991936,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6484490309962616,
            "unit": "iter/sec",
            "range": "stddev: 0.004707152661956923",
            "extra": "mean: 1.5421412511999961 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.089894095260362,
            "unit": "iter/sec",
            "range": "stddev: 0.0007410550961924088",
            "extra": "mean: 99.10906800000419 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b3247e8d531b7dd35ca1c55a5bed5ea4151b9fa8",
          "message": "ENH: Add papersizes (#800)",
          "timestamp": "2022-04-24T06:03:50+02:00",
          "tree_id": "966fb1ac42051614b11acae333b07bb52398e051",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b3247e8d531b7dd35ca1c55a5bed5ea4151b9fa8"
        },
        "date": 1650773067691,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5540552761217961,
            "unit": "iter/sec",
            "range": "stddev: 0.0049744553903781135",
            "extra": "mean: 1.804874067800003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.949716349828208,
            "unit": "iter/sec",
            "range": "stddev: 0.0008507589272494641",
            "extra": "mean: 111.73538477777514 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "75410478227a396886be41b336aaefb201ac92cf",
          "message": "DOC: The PDF Format + commit prefixes (#810)",
          "timestamp": "2022-04-24T07:12:39+02:00",
          "tree_id": "749b17278ac678804df14095f3d9ffdfee7720c2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/75410478227a396886be41b336aaefb201ac92cf"
        },
        "date": 1650777194088,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6479789131674737,
            "unit": "iter/sec",
            "range": "stddev: 0.003677746212021266",
            "extra": "mean: 1.543260096399996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.12288684932602,
            "unit": "iter/sec",
            "range": "stddev: 0.006132508373283311",
            "extra": "mean: 98.78604936363384 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6729b8005e3d07ddf858da319e1ce27784368d88",
          "message": "DOC: CMaps (#811)",
          "timestamp": "2022-04-24T11:30:59+02:00",
          "tree_id": "0e168da055bb6a4f07ccb33287a14b730d4daa8d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6729b8005e3d07ddf858da319e1ce27784368d88"
        },
        "date": 1650792707218,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5062473877039959,
            "unit": "iter/sec",
            "range": "stddev: 0.020347651861574872",
            "extra": "mean: 1.9753188347999981 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.8468491530427995,
            "unit": "iter/sec",
            "range": "stddev: 0.007294014757637078",
            "extra": "mean: 127.43968700000133 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "f48b4acb5c1578fceb9fa97153583489cc4d164e",
          "message": "DEV: Adjust performance benchmark",
          "timestamp": "2022-04-24T13:21:27+02:00",
          "tree_id": "634289bb4f5e46222b399606562d13abad9a95fa",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f48b4acb5c1578fceb9fa97153583489cc4d164e"
        },
        "date": 1650799332627,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6476011688384089,
            "unit": "iter/sec",
            "range": "stddev: 0.013645267097183788",
            "extra": "mean: 1.5441602765999989 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.24335243186828,
            "unit": "iter/sec",
            "range": "stddev: 0.005659092465901196",
            "extra": "mean: 97.62428918181922 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "663ca9899fcd98630727c235278f114ea75533de",
          "message": "ROB: Use null ID when encrypted but no ID given (#812)\n\nIf no '/ID' key is present in self.trailer an array of two empty bytestrings is used in place of an '/ID'. This is how Apache PDFBox handles this case.\r\n\r\nThis makes PyPDF2 more robust to malformed PDFs.\r\n\r\nCloses #608\r\nCloses #610\r\n\r\nFull credit for this one to Richard Millson - Martin Thoma only fixed a merge conflict\r\n\r\nCo-authored-by: Richard Millson <8217613+richardmillson@users.noreply.github.com>",
          "timestamp": "2022-04-24T13:30:33+02:00",
          "tree_id": "6a4e8497c6589f5375088f1d77c909b865bfcece",
          "url": "https://github.com/py-pdf/PyPDF2/commit/663ca9899fcd98630727c235278f114ea75533de"
        },
        "date": 1650799875942,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.541893603172852,
            "unit": "iter/sec",
            "range": "stddev: 0.019628717523265633",
            "extra": "mean: 1.8453807059999974 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.78432658130401,
            "unit": "iter/sec",
            "range": "stddev: 0.0025973099354251743",
            "extra": "mean: 113.83911911111493 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "63b4c91f4f466fa6fb9e256af3cadc11bb8e4a05",
          "message": "BUG: TypeError in xmp._converter_date (#813)\n\nFix: Convert decimal to int before passing it to datetime\r\n\r\nCloses #774",
          "timestamp": "2022-04-24T13:46:20+02:00",
          "tree_id": "33563b704555604f79db8e5c1737c3c781aa9546",
          "url": "https://github.com/py-pdf/PyPDF2/commit/63b4c91f4f466fa6fb9e256af3cadc11bb8e4a05"
        },
        "date": 1650800821542,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5308827521609454,
            "unit": "iter/sec",
            "range": "stddev: 0.07265480137831483",
            "extra": "mean: 1.8836550932000038 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.928300240309044,
            "unit": "iter/sec",
            "range": "stddev: 0.007008704187200776",
            "extra": "mean: 112.0034018888892 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5bc7219360978dfb593fc4275e76b6f3057972c9",
          "message": "MAINT: Validate PDF magic byte in strict mode (#814)\n\nCloses #626",
          "timestamp": "2022-04-24T14:51:19+02:00",
          "tree_id": "fac05cd2ef17e2fdd9a43ce133b252c299455a62",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5bc7219360978dfb593fc4275e76b6f3057972c9"
        },
        "date": 1650804720365,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5968691930782724,
            "unit": "iter/sec",
            "range": "stddev: 0.10524568460776369",
            "extra": "mean: 1.6754089700000008 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.975065944299576,
            "unit": "iter/sec",
            "range": "stddev: 0.0069488832822520805",
            "extra": "mean: 100.2499638181808 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "e673a6eb2dc9b2207a144d253f2504739655f461",
          "message": "DEV: Minor fix in make_changelog.py",
          "timestamp": "2022-04-24T15:30:16+02:00",
          "tree_id": "ec4435cfb572d70414b43320a4df5d94432b0e0c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e673a6eb2dc9b2207a144d253f2504739655f461"
        },
        "date": 1650807055894,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6580371905513777,
            "unit": "iter/sec",
            "range": "stddev: 0.0040697971114903985",
            "extra": "mean: 1.5196709461999973 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.018692922795166,
            "unit": "iter/sec",
            "range": "stddev: 0.00440530782071321",
            "extra": "mean: 99.81341954545155 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "22033d724e0c8a684c5aca1d390deedb4331a273",
          "message": "REL: 1.27.9\n\nA change I would like to highlight is the performance improvement for\nlarge PDF files (#808) 🎉\n\nNew Features (ENH):\n-  Add papersizes (#800)\n-  Allow setting permission flags when encrypting (#803)\n-  Allow setting form field flags (#802)\n\nBug Fixes (BUG):\n-  TypeError in xmp._converter_date (#813)\n-  Improve spacing for text extraction (#806)\n-  Fix PDFDocEncoding Character Set (#809)\n\nRobustness (ROB):\n-  Use null ID when encrypted but no ID given (#812)\n-  Handle recursion error (#804)\n\nDocumentation (DOC):\n-  CMaps (#811)\n-  The PDF Format + commit prefixes (#810)\n-  Add compression example (#792)\n\nDeveloper Experience (DEV):\n-  Add Benchmark for Performance Testing (#781)\n\nMaintenance (MAINT):\n-  Validate PDF magic byte in strict mode (#814)\n-  Make PdfFileMerger.addBookmark() behave life PdfFileWriters\\' (#339)\n-  Quadratic runtime while parsing reduced to linear  (#808)\n\nTesting (TST):\n-  Newlines in text extraction (#807)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/1.27.8...1.27.9",
          "timestamp": "2022-04-24T15:32:00+02:00",
          "tree_id": "87103a760ba5e5826c6472d92e28e22513835231",
          "url": "https://github.com/py-pdf/PyPDF2/commit/22033d724e0c8a684c5aca1d390deedb4331a273"
        },
        "date": 1650807175210,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5705970637383673,
            "unit": "iter/sec",
            "range": "stddev: 0.006161448737138847",
            "extra": "mean: 1.752550203200002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.321006282639642,
            "unit": "iter/sec",
            "range": "stddev: 0.0016392937995490596",
            "extra": "mean: 107.28455380000099 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "39215c704791c10189668bbd1fa1d04d0b1f3f81",
          "message": "DOC: More details on text parsing issues (#815)",
          "timestamp": "2022-04-24T16:29:40+02:00",
          "tree_id": "cf2929720a034465cd1497ceb5d50ef283785b74",
          "url": "https://github.com/py-pdf/PyPDF2/commit/39215c704791c10189668bbd1fa1d04d0b1f3f81"
        },
        "date": 1650810620707,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5266091808541599,
            "unit": "iter/sec",
            "range": "stddev: 0.04462753547546615",
            "extra": "mean: 1.8989414471999908 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.53769833696998,
            "unit": "iter/sec",
            "range": "stddev: 0.006891337436723719",
            "extra": "mean: 117.12758644443966 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "80f2f2572d2602f37e0ed3be34ef95d5df62a278",
          "message": "DOC: PDF feature/version support (#816)",
          "timestamp": "2022-04-24T17:15:49+02:00",
          "tree_id": "2da7f003dd39086e84797959d37cb6e663394948",
          "url": "https://github.com/py-pdf/PyPDF2/commit/80f2f2572d2602f37e0ed3be34ef95d5df62a278"
        },
        "date": 1650813390431,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.49904665714763946,
            "unit": "iter/sec",
            "range": "stddev: 0.016996534436094574",
            "extra": "mean: 2.003820656200001 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.91783474963698,
            "unit": "iter/sec",
            "range": "stddev: 0.005104605993043909",
            "extra": "mean: 126.29715466666546 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "10ccbae325e875432a9980c4b78758203b728f33",
          "message": "TST: Add test for filters.ASCIIHexDecode (#822)\n\nFull Credit goes to https://github.com/py-pdf/PyPDF2/pull/817/commits/5c74416e6cb9675628975f12528ca908c554bb63\r\nwho wrote the test in 2018 for PyPDF4\r\n\r\nCo-authored-by: Acsor <nildexo@yandex.com>",
          "timestamp": "2022-04-25T21:53:25+02:00",
          "tree_id": "7ad67406b3aee8c71ae7848fddb8f4d705bc3f3c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/10ccbae325e875432a9980c4b78758203b728f33"
        },
        "date": 1650916454674,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.4993369078003011,
            "unit": "iter/sec",
            "range": "stddev: 0.026954339188757847",
            "extra": "mean: 2.002655891000006 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.302262730048474,
            "unit": "iter/sec",
            "range": "stddev: 0.0012979079016196592",
            "extra": "mean: 120.44909111111224 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "39ffc1d6265e1b710d87cd6fc1a5f6b270978090",
          "message": "TST: Add test for FlateDecode (#823)\n\nFull credit to\r\nhttps://github.com/py-pdf/PyPDF2/pull/817/commits/9f628b3989b2f9714db9eb850bed323329a61922\r\nwho added the test in 2018 to PyPDF4\r\n\r\nCo-authored-by: Acsor <nildexo@yandex.com>",
          "timestamp": "2022-04-25T22:38:54+02:00",
          "tree_id": "1406b92bec2277732129a7c71c9e5d0bf03b3e9e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/39ffc1d6265e1b710d87cd6fc1a5f6b270978090"
        },
        "date": 1650919175534,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.533021892422493,
            "unit": "iter/sec",
            "range": "stddev: 0.04128214521394912",
            "extra": "mean: 1.8760955491999993 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.931744670108035,
            "unit": "iter/sec",
            "range": "stddev: 0.0009845891608524406",
            "extra": "mean: 111.96020900000765 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "963b25159a69eb3264cb7179082fe6ffce16126b",
          "message": "TST: Use external repository for larger/more PDFs for testing (#820)\n\n* Use submodule so that the connection is clear. Ensure that Flake8 issues of the submodule don't show up here\r\n* As a first step, just try to get the number of pages from the non-encrypted PDFs\r\n* Create an \"external\" pytest marker which allows people to deactivate tests that need the submodule",
          "timestamp": "2022-04-26T17:02:57+02:00",
          "tree_id": "c2f56b9f16c0df0b78500c475fe2e36d672a47be",
          "url": "https://github.com/py-pdf/PyPDF2/commit/963b25159a69eb3264cb7179082fe6ffce16126b"
        },
        "date": 1650985417517,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6455807745487593,
            "unit": "iter/sec",
            "range": "stddev: 0.009333597564409836",
            "extra": "mean: 1.5489928439999914 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.110828960054192,
            "unit": "iter/sec",
            "range": "stddev: 0.007821850869459548",
            "extra": "mean: 98.90385881818341 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "96d8d0f937dbffc867f0d49d66f5c40b36bb431d",
          "message": "TST: Add Test for ASCII85Decode (#825)\n\nFull credit to\r\nhttps://github.com/py-pdf/PyPDF2/pull/817/commits/6dc90b1e64c1965b61aa2561ce912f64ca19cad4\r\n\r\nCo-authored-by: Acsor <nildexo@yandex.com>",
          "timestamp": "2022-04-26T18:20:09+02:00",
          "tree_id": "02a47e5754b4e83a52ebb6301118b24d837ef7ed",
          "url": "https://github.com/py-pdf/PyPDF2/commit/96d8d0f937dbffc867f0d49d66f5c40b36bb431d"
        },
        "date": 1650990044230,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6541198244177866,
            "unit": "iter/sec",
            "range": "stddev: 0.003829907124529457",
            "extra": "mean: 1.5287718896000002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.085985833131874,
            "unit": "iter/sec",
            "range": "stddev: 0.0006931207886781686",
            "extra": "mean: 99.1474721999964 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "355f805f30e493cda2af134ccb768edccf3ff0ab",
          "message": "DEV: Ignore IronPython parts for code coverage (#826)\n\nI have no idea how to test for that in GithubActions.\r\nAs this likely only affects a small fraction of PyPDF2 users,\r\nI want to ignore it for now.\r\n\r\nFeel free to add a PR that adds IronPython to GithubActions -\r\nthen we can enable this again.",
          "timestamp": "2022-04-26T18:30:53+02:00",
          "tree_id": "c399e5e719e31fdc84ae2cd3b91082c21b3bb121",
          "url": "https://github.com/py-pdf/PyPDF2/commit/355f805f30e493cda2af134ccb768edccf3ff0ab"
        },
        "date": 1650990689658,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.652312710979302,
            "unit": "iter/sec",
            "range": "stddev: 0.008901747430670692",
            "extra": "mean: 1.5330070734000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.376939144749729,
            "unit": "iter/sec",
            "range": "stddev: 0.0060005167688021105",
            "extra": "mean: 96.36753054545527 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f90a9d7140a9cddcc60cc1f17a695ca2b363af39",
          "message": "TST: Add tests for utils, form fields, PageRange (#827)\n\ngetFormTextFields now return an empty dict instead of throwing an exception if no form fields are found. This should eliminate an error source",
          "timestamp": "2022-04-26T22:20:02+02:00",
          "tree_id": "4e8432ad79fb24f91acc3e0cf86d42a6259aff1d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f90a9d7140a9cddcc60cc1f17a695ca2b363af39"
        },
        "date": 1651004444445,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5339640513290262,
            "unit": "iter/sec",
            "range": "stddev: 0.012493021925103417",
            "extra": "mean: 1.8727852511999998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.75920949734288,
            "unit": "iter/sec",
            "range": "stddev: 0.00284369106426063",
            "extra": "mean: 114.16555344444627 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "35086b6e2c0b45ce4b80e2581e8b27cd12a6d373",
          "message": "STY: Remove debug code (#828)",
          "timestamp": "2022-04-27T08:03:14+02:00",
          "tree_id": "9c32fdaceaabf28b00855dfe80d3eabb7b10481b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/35086b6e2c0b45ce4b80e2581e8b27cd12a6d373"
        },
        "date": 1651039434526,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5350829750413725,
            "unit": "iter/sec",
            "range": "stddev: 0.031613512699053894",
            "extra": "mean: 1.8688690289999983 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.653130659753275,
            "unit": "iter/sec",
            "range": "stddev: 0.004827429409492978",
            "extra": "mean: 115.56511039999862 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "904b0df5a2d840d0ef0d1db52c7ee6a114664594",
          "message": "ROB: Fix corruption in startxref or xref table (#788)\n\nUse PdfReadWarning instead of UserWarning to be consistent\r\n\r\nCloses #297",
          "timestamp": "2022-04-27T13:30:31+02:00",
          "tree_id": "9b911b76a3f9a819ee0ca14a104336eeb0bd51db",
          "url": "https://github.com/py-pdf/PyPDF2/commit/904b0df5a2d840d0ef0d1db52c7ee6a114664594"
        },
        "date": 1651059070812,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6500721455982809,
            "unit": "iter/sec",
            "range": "stddev: 0.006260350447390519",
            "extra": "mean: 1.5382907986000078 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.383048126671477,
            "unit": "iter/sec",
            "range": "stddev: 0.005338950545449663",
            "extra": "mean: 96.31083163635233 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fd775d34d9ccf8f77596ca9e82944c869901ac0f",
          "message": "MAINT: Refactoring after #788 (#830)\n\nThis refactoring aims at making maintenance easier:\r\n\r\n1. Too long functions make it hard to grasp the overall behavior. Hence the _get_xref_issues function was split out\r\n2. `_get_xref_issues` is made a static method of the PdfFileReader to show that it belongs to the reader, but doesn't require any of its attributes\r\n3. `_get_xref_issues` makes use of an integer return value instead of raising + catching exceptions. \r\n4. `_rebuild_xref_table` was moved to a method for the same reason.",
          "timestamp": "2022-04-27T17:44:09+02:00",
          "tree_id": "beff2babbf9ba4905400267caa89d4e7ddc069ac",
          "url": "https://github.com/py-pdf/PyPDF2/commit/fd775d34d9ccf8f77596ca9e82944c869901ac0f"
        },
        "date": 1651074294887,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6534127715275444,
            "unit": "iter/sec",
            "range": "stddev: 0.0030763372688520432",
            "extra": "mean: 1.5304261618 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.089517366180937,
            "unit": "iter/sec",
            "range": "stddev: 0.0008623789855637931",
            "extra": "mean: 99.11276860000271 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "cb32323a4c2581c0a0c395bbe2320b6ca776c67d",
          "message": "DOC: History of PyPDF2",
          "timestamp": "2022-04-27T17:49:59+02:00",
          "tree_id": "e10220d86b8ceea20c75cbe0939d7972bdabee71",
          "url": "https://github.com/py-pdf/PyPDF2/commit/cb32323a4c2581c0a0c395bbe2320b6ca776c67d"
        },
        "date": 1651074640781,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6502136222433015,
            "unit": "iter/sec",
            "range": "stddev: 0.003251982470534682",
            "extra": "mean: 1.5379560897999967 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.026016520294906,
            "unit": "iter/sec",
            "range": "stddev: 0.0008580678769596281",
            "extra": "mean: 99.74050989999625 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fcd1aed0f762d5c26eba9bcdff4eb8e0eb39ca8f",
          "message": "TST: Add tests for PyPDF2.generic (#831)\n\n* BUG: StopIteration got deprecated in Python 3.7, see PEP 479\r\n* STY: Use property decorator\r\n\r\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-04-28T10:39:51+02:00",
          "tree_id": "3a9c71f52bc2f5e6cee461016ef1d1ad21078f00",
          "url": "https://github.com/py-pdf/PyPDF2/commit/fcd1aed0f762d5c26eba9bcdff4eb8e0eb39ca8f"
        },
        "date": 1651135253971,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5520707881894535,
            "unit": "iter/sec",
            "range": "stddev: 0.018268466912576466",
            "extra": "mean: 1.811361914800011 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.792815022718578,
            "unit": "iter/sec",
            "range": "stddev: 0.0010336042124188555",
            "extra": "mean: 113.72922066667319 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "865d74433e2b776ee131663f984e52dc083dca70",
          "message": "MAINT: Update requirements files",
          "timestamp": "2022-04-28T11:02:26+02:00",
          "tree_id": "4f0d14b4f16561868c2203cb124fb3c6afa0e446",
          "url": "https://github.com/py-pdf/PyPDF2/commit/865d74433e2b776ee131663f984e52dc083dca70"
        },
        "date": 1651136596364,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6415824680643019,
            "unit": "iter/sec",
            "range": "stddev: 0.006028124875887984",
            "extra": "mean: 1.5586460818000034 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.189942048271186,
            "unit": "iter/sec",
            "range": "stddev: 0.006762608643911026",
            "extra": "mean: 98.13598499999898 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eef03d935dfeacaa75848b39082cf94d833d3174",
          "message": "STY: Apply pre-commit (black, isort) + use snake_case variables (#832)\n\nThis change standardizes the code formatting quite a bit.\r\nHaving standardized formatting makes the code easier to read\r\nand reduces the diff.\r\n\r\nThis includes:\r\n\r\n* Applying the black auto-formatter (also in the docs)\r\n* Applying isort for import sorting\r\n* Making sure that files end with a newline\r\n\r\nAdditionally, in several places the property function call style was replaced by the decorator style",
          "timestamp": "2022-04-28T11:53:18+02:00",
          "tree_id": "93562802485ae6a26ff05fad3cf13e3a33bdb00a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/eef03d935dfeacaa75848b39082cf94d833d3174"
        },
        "date": 1651139639035,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.744978809967256,
            "unit": "iter/sec",
            "range": "stddev: 0.0047688953823038305",
            "extra": "mean: 1.3423200587999986 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.643426095476853,
            "unit": "iter/sec",
            "range": "stddev: 0.005384084734819235",
            "extra": "mean: 85.88537358333663 msec\nrounds: 12"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c1dfdaa475c8705c45d82305f2d2ec76168e7e30",
          "message": "TST: Reader and page properties (#835)",
          "timestamp": "2022-04-28T12:45:14+02:00",
          "tree_id": "4cf4b3c640d71220342496b9bb66ef1ee07d06ea",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c1dfdaa475c8705c45d82305f2d2ec76168e7e30"
        },
        "date": 1651142754261,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5525941267582756,
            "unit": "iter/sec",
            "range": "stddev: 0.004335068924803803",
            "extra": "mean: 1.8096464503999983 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.918099518311225,
            "unit": "iter/sec",
            "range": "stddev: 0.0013836104991058473",
            "extra": "mean: 112.13151388888794 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e1408f7488f2df54341b1208f2ad0a1b14eb8e81",
          "message": "MAINT: Split pdf module (#836)",
          "timestamp": "2022-04-28T14:40:53+02:00",
          "tree_id": "0620d6908a07c4249190ebf5952edde1bd138176",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e1408f7488f2df54341b1208f2ad0a1b14eb8e81"
        },
        "date": 1651149694527,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6511333754112755,
            "unit": "iter/sec",
            "range": "stddev: 0.005939225208470314",
            "extra": "mean: 1.5357836623999959 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.28649261251013,
            "unit": "iter/sec",
            "range": "stddev: 0.006082521245230465",
            "extra": "mean: 97.21486590908833 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5c7d6e8bc1908dd179383397a605133cf1d83939",
          "message": "TST: swap incorrect test names (#838)",
          "timestamp": "2022-04-28T16:11:12+02:00",
          "tree_id": "3981c3cda471e4d14157fb0b97f1aac4b93cdec7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5c7d6e8bc1908dd179383397a605133cf1d83939"
        },
        "date": 1651155110130,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6615813811562604,
            "unit": "iter/sec",
            "range": "stddev: 0.0046065495210667684",
            "extra": "mean: 1.5115298412000016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.00428368875864,
            "unit": "iter/sec",
            "range": "stddev: 0.004433978733442472",
            "extra": "mean: 99.95718145454578 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5e86977813d9714e9383a5b2801e26d57a16a86d",
          "message": "ROB: warn-only in readStringFromStream (#837)\n\nAn unexpected escape string was raising a PdfReadError before.\r\nNow, only a warning is issued.\r\n\r\nCloses #360\r\nCloses #794 : Passing the strict parameter looks like a good idea,\r\n              but there is also the pdf parameter. Sadly, it is\r\n              None for that issue.",
          "timestamp": "2022-04-28T16:18:18+02:00",
          "tree_id": "8059010d5156444397416dc2e9b56b64e45f5437",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5e86977813d9714e9383a5b2801e26d57a16a86d"
        },
        "date": 1651155537175,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6544444290869603,
            "unit": "iter/sec",
            "range": "stddev: 0.0032139339956374427",
            "extra": "mean: 1.5280136182000006 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.13957595768099,
            "unit": "iter/sec",
            "range": "stddev: 0.0007348270835737484",
            "extra": "mean: 98.62345370000156 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3fe9e6ef0e547a044cfa7ec6df6e76452cc09c10",
          "message": "ROB: Handle missing destinations in reader (#840)\n\nIf a destination is missing, getDestinationPageNumber now returns -1\r\nIf `strict=False`, the first page is used as a fallback.\r\n\r\nThe code triggering the exception was\r\n\r\n```python\r\nfrom PyPDF2 import PdfFileReader\r\n\r\n# https://github.com/mstamy2/PyPDF2/files/6045010/thyroid.pdf\r\nwith open(\"thyroid.pdf\", \"rb\") as f:\r\n   reader = PdfFileReader(f)\r\n   bookmarks = pdf.getOutlines()\r\n   for b in bookmarks:\r\n       print(reader.getDestinationPageNumber(b) + 1)  # page count starts from 0\r\n```\r\n\r\nThe error message was:\r\n    PyPDF2.utils.PdfReadError: Unknown Destination Type: 0\r\n\r\nCloses #604 \r\nCloses #821",
          "timestamp": "2022-04-30T20:13:24+02:00",
          "tree_id": "5db3305fbfb9b628d599904682d8f840cd1734f5",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3fe9e6ef0e547a044cfa7ec6df6e76452cc09c10"
        },
        "date": 1651342444178,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6549521794964375,
            "unit": "iter/sec",
            "range": "stddev: 0.006425753643669064",
            "extra": "mean: 1.5268290286000024 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.295506195647757,
            "unit": "iter/sec",
            "range": "stddev: 0.006403111875990784",
            "extra": "mean: 97.12975554545653 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "444fca22836df061d9d23e71ffb7d68edcdfa766",
          "message": "STY: Documentation, Variable names (#839)\n\n* pytest style\r\n* use more constants",
          "timestamp": "2022-04-30T20:19:26+02:00",
          "tree_id": "13153ced2b968d63d1003bb6128dd3e12f7b2fd7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/444fca22836df061d9d23e71ffb7d68edcdfa766"
        },
        "date": 1651342801039,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7273790759126576,
            "unit": "iter/sec",
            "range": "stddev: 0.0041930713218297855",
            "extra": "mean: 1.3747989640000013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.613264540689384,
            "unit": "iter/sec",
            "range": "stddev: 0.005972794829883468",
            "extra": "mean: 86.10843200000318 msec\nrounds: 12"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d2ed8e593bedeca0cc6283f9d4894a45c7a85323",
          "message": "MAINT: Separated CCITTFax param parsing/decoding (#841)\n\n* BUG: Changed default /K to conform with the PDF 1.7 standard\r\n* TST: Add test for CCITTFax\r\n* TST: Add test for TextStringObject\r\n\r\nSTY:\r\n* Group Python 2.7 imports\r\n* camelCase variables to snake_case\r\n* Apply black formatter",
          "timestamp": "2022-05-01T10:55:00+02:00",
          "tree_id": "c8e20b34d7d1b7804daf4ed0e385cb99d5d02205",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d2ed8e593bedeca0cc6283f9d4894a45c7a85323"
        },
        "date": 1651395337855,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6595642448645689,
            "unit": "iter/sec",
            "range": "stddev: 0.0027934216538311064",
            "extra": "mean: 1.5161525322000045 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.03107597243035,
            "unit": "iter/sec",
            "range": "stddev: 0.004474913223608447",
            "extra": "mean: 99.69020299999958 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7592257855b619d1d13752afac052147377a3c3f",
          "message": "DOC: Project Governance (#799)\n\nThank you Matthew for your support / suggestions!\r\n\r\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-05-01T10:56:30+02:00",
          "tree_id": "dd41e47f40b1052d0966d687b88e2020d3ef7297",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7592257855b619d1d13752afac052147377a3c3f"
        },
        "date": 1651395428249,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5730060597961345,
            "unit": "iter/sec",
            "range": "stddev: 0.018179231162042064",
            "extra": "mean: 1.745182241799995 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.116730914362284,
            "unit": "iter/sec",
            "range": "stddev: 0.0012190247077632514",
            "extra": "mean: 109.6884408888962 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "be6cdd8864075ba08e789c2b5b0b83b16fc6ea9e",
          "message": "DEV: Add benchmark command to Makefile",
          "timestamp": "2022-05-01T11:08:03+02:00",
          "tree_id": "57cc50e2e0749d944b412c468589ae5a1beaaccb",
          "url": "https://github.com/py-pdf/PyPDF2/commit/be6cdd8864075ba08e789c2b5b0b83b16fc6ea9e"
        },
        "date": 1651396126499,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5648025130939326,
            "unit": "iter/sec",
            "range": "stddev: 0.028904580240274903",
            "extra": "mean: 1.7705303656000013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.228001369841428,
            "unit": "iter/sec",
            "range": "stddev: 0.004177987880058724",
            "extra": "mean: 108.36582700000008 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "def7a629ad4e1341dfdd68f6c7f56c111f1ee5c6",
          "message": "REL: 1.27.10\n\nRobustness (ROB):\n-  Handle missing destinations in reader (#840)\n-  warn-only in readStringFromStream (#837)\n-  Fix corruption in startxref or xref table (#788 and #830)\n\nDocumentation (DOC):\n-  Project Governance (#799)\n-  History of PyPDF2\n-  PDF feature/version support (#816)\n-  More details on text parsing issues (#815)\n\nDeveloper Experience (DEV):\n-  Add benchmark command to Makefile\n-  Ignore IronPython parts for code coverage (#826)\n\nMaintenance (MAINT):\n-  Split pdf module (#836)\n-  Separated CCITTFax param parsing/decoding (#841)\n-  Update requirements files\n\nTesting (TST):\n-  Use external repository for larger/more PDFs for testing (#820)\n-  Swap incorrect test names (#838)\n-  Add test for PdfFileReader and page properties (#835)\n-  Add tests for PyPDF2.generic (#831)\n-  Add tests for utils, form fields, PageRange (#827)\n-  Add test for ASCII85Decode (#825)\n-  Add test for FlateDecode (#823)\n-  Add test for filters.ASCIIHexDecode (#822)\n\nCode Style (STY):\n-  Apply pre-commit (black, isort) + use snake_case variables (#832)\n-  Remove debug code (#828)\n-  Documentation, Variable names (#839)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/1.27.9...1.27.10",
          "timestamp": "2022-05-01T11:15:33+02:00",
          "tree_id": "a6ba2d1fde8e3e3f583d447470fcf0f92c852334",
          "url": "https://github.com/py-pdf/PyPDF2/commit/def7a629ad4e1341dfdd68f6c7f56c111f1ee5c6"
        },
        "date": 1651396574859,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6616531682541348,
            "unit": "iter/sec",
            "range": "stddev: 0.0035949971699881533",
            "extra": "mean: 1.5113658454000016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.943860974640522,
            "unit": "iter/sec",
            "range": "stddev: 0.0047829961485161675",
            "extra": "mean: 100.56455963636908 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c96489d789c18170ba9ff8d9aa852efab1037d96",
          "message": "BUG: Incorrectly issued xref warning/exception (#855)\n\nCloses #852",
          "timestamp": "2022-05-02T08:44:00+02:00",
          "tree_id": "2e9cf604a84066f36193d6c25ee3447bb6dcf0d0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c96489d789c18170ba9ff8d9aa852efab1037d96"
        },
        "date": 1651473878291,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6619677017339488,
            "unit": "iter/sec",
            "range": "stddev: 0.003690628561990942",
            "extra": "mean: 1.5106477210000038 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.986055372417564,
            "unit": "iter/sec",
            "range": "stddev: 0.004534714433574842",
            "extra": "mean: 100.13964099999839 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "998d5bad34956524abb5017ca98eb98e78f977ce",
          "message": "REL: 1.27.11\n\nBug Fixes (BUG):\n-  Incorrectly issued xref warning/exception (#855)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/1.27.10...1.27.11",
          "timestamp": "2022-05-02T08:46:14+02:00",
          "tree_id": "b5dc8606d281db02f295fd0b3f2644f7497c2440",
          "url": "https://github.com/py-pdf/PyPDF2/commit/998d5bad34956524abb5017ca98eb98e78f977ce"
        },
        "date": 1651474058223,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6528417792666815,
            "unit": "iter/sec",
            "range": "stddev: 0.008126007738070226",
            "extra": "mean: 1.531764712000006 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.203348666866178,
            "unit": "iter/sec",
            "range": "stddev: 0.006634021469313385",
            "extra": "mean: 98.00703990909844 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "955da9922f93e909110f083a4ddd422778265cfa",
          "message": "DOC: Security Policy",
          "timestamp": "2022-05-02T13:27:33+02:00",
          "tree_id": "ff07b8cf1d83ab13e45a4dc0ae7cb7665100c510",
          "url": "https://github.com/py-pdf/PyPDF2/commit/955da9922f93e909110f083a4ddd422778265cfa"
        },
        "date": 1651490903091,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5549167864033904,
            "unit": "iter/sec",
            "range": "stddev: 0.043146079989043136",
            "extra": "mean: 1.8020719944000063 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.942439011681005,
            "unit": "iter/sec",
            "range": "stddev: 0.004484850855279719",
            "extra": "mean: 111.82631479999543 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "48d5f0ca3e702da1460107dbe7d90ccdd60a4c1f",
          "message": "BUG: _rebuild_xref_table expects trailer to be a dict (#857)\n\nThis caused:\r\n    AttributeError: 'FloatObject' object has no attribute 'items'\r\n\r\nCloses #856\r\n\r\nCo-authored-by: pubpub-zz <4083478+pubpub-zz@users.noreply.github.com>",
          "timestamp": "2022-05-02T21:06:20+02:00",
          "tree_id": "f67c717266a4e5080a449700dc88c806e776f63a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/48d5f0ca3e702da1460107dbe7d90ccdd60a4c1f"
        },
        "date": 1651518420900,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5464325263471695,
            "unit": "iter/sec",
            "range": "stddev: 0.007997181509643857",
            "extra": "mean: 1.830052114000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.927549861794354,
            "unit": "iter/sec",
            "range": "stddev: 0.0010864594569718394",
            "extra": "mean: 112.0128160000004 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "f3cb316f0135bc4f761e78086effa66e1652b2e4",
          "message": "REL: 1.27.12\n\nBug Fixes (BUG):\n-  _rebuild_xref_table expects trailer to be a dict (#857)\n\nDocumentation (DOC):\n-  Security Policy\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/1.27.11...1.27.12",
          "timestamp": "2022-05-02T21:10:50+02:00",
          "tree_id": "7d28a3654698edfcf47b451f055bec5039d6118d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f3cb316f0135bc4f761e78086effa66e1652b2e4"
        },
        "date": 1651518714191,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6517502234565721,
            "unit": "iter/sec",
            "range": "stddev: 0.011350903544595869",
            "extra": "mean: 1.5343301222000008 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.248858811233584,
            "unit": "iter/sec",
            "range": "stddev: 0.006084210437525165",
            "extra": "mean: 97.57183881818321 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a791ef16c009bcf528fba2e566cc58b5d18dc4f4",
          "message": "MAINT: Remove IronPython Fallback for zlib (#868)\n\nSee https://github.com/py-pdf/PyPDF2/discussions/863",
          "timestamp": "2022-05-09T22:20:34+02:00",
          "tree_id": "e73c854d078a066be3190333e77505b517005268",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a791ef16c009bcf528fba2e566cc58b5d18dc4f4"
        },
        "date": 1652127673196,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6529593825268383,
            "unit": "iter/sec",
            "range": "stddev: 0.004686145907465022",
            "extra": "mean: 1.531488828800002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.199708238087558,
            "unit": "iter/sec",
            "range": "stddev: 0.006640646404993513",
            "extra": "mean: 98.04202009090996 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c66ee8cf01a9ef5984bdc5a8eb612227ede413ab",
          "message": "DEP: PEP8-style module, class, and method names (#867)\n\nThis commit strives to make the usage for new PyPDF2 users easier by following\r\nPEP8 naming schemes. It's mostly about camelCase method names being converted to\r\nsnake_case. Other changes make the public interface of PyPDF2 smaller and thus\r\neasier to discover.\r\n\r\nThis commit does not introduce any breaking changes as the old modules /\r\nclasses / method signatures are still present. They have now deprecation\r\nwarnings and the docs show that those are considered deprecated.\r\n\r\nIf a property and a getter-method are both present, use the property.\r\n\r\nModule level changes\r\n--------------------\r\n\r\n- utils ➔ _utils: The module is renamed to '_utils' to indicate that it should\r\n                not be used by PyPDF2 users. It's only meant for PyPDF2 itself.\r\n- The 'pdf' module was removed. Most classes / functions are now either in\r\n  '_utils' or in 'generic'.\r\n\r\n\r\nCore classes\r\n------------\r\n\r\n- PdfFileReader➔ PdfReader (strict=False is new default)\r\n- PdfFileWriter➔ PdfWriter\r\n- PdfFileMerger➔ PdfMerger (strict=False is new default)\r\n\r\nPdfReader\r\n---------\r\n\r\n- writer.getPage(pageNumber) ➔ writer.pages[page_number]\r\n- writer.getNumPages() ➔ len(writer.pages)\r\n- getPageLayout / pageLayout ➔ page_layout\r\n- getPageMode / pageMode ➔ page_mode\r\n- getIsEncrypted / isEncrypted ➔ is_encrypted\r\n- getDocumentInfo ➔ metadata\r\n\r\nPdfWriter\r\n---------\r\n\r\n- writer.getPage(pageNumber) ➔ writer.pages[page_number]\r\n- writer.getNumPages() ➔ len(writer.pages)\r\n- getPageLayout / setPageLayout / pageLayout ➔ page_layout\r\n- getPageMode / setPageMode / pageMode ➔ page_mode\r\n\r\nPage\r\n----\r\n\r\n- mediabox / trimbox / cropbox / bleedbox / artbox:\r\n    - getWidth, getHeight  ➔ width / height\r\n    - getLowerLeft_x / getUpperLeft_x ➔ left\r\n    - getUpperRight_x / getLowerRight_x ➔ right\r\n    - getLowerLeft_y / getLowerRight_y ➔ bottom\r\n    - getUpperRight_y / getUpperLeft_y ➔ top\r\n    - getLowerLeft / setLowerLeft ➔ lower_left property\r\n    - upperRight ➔ upper_right\r\n- Add Transformation class to make it easy to create transformation matrices\r\n- add_transformation and merge_page should be used instead of:\r\n    - mergeTransformedPage\r\n    - mergeScaledPage\r\n    - mergeRotatedPage\r\n    - mergeTranslatedPage\r\n    - mergeRotatedTranslatedPage\r\n    - mergeRotatedScaledPage\r\n    - mergeScaledTranslatedPage\r\n    - mergeRotatedScaledTranslatedPage\r\n\r\nSee the CHANGELOG for a full list of changes",
          "timestamp": "2022-05-22T14:20:05+02:00",
          "tree_id": "42eab87f3de9a4c4c8e530a4fcc0e0124872bbd3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c66ee8cf01a9ef5984bdc5a8eb612227ede413ab"
        },
        "date": 1653222044026,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6599236178218959,
            "unit": "iter/sec",
            "range": "stddev: 0.010464724886038564",
            "extra": "mean: 1.515326884800001 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.119673911318733,
            "unit": "iter/sec",
            "range": "stddev: 0.005340151061360368",
            "extra": "mean: 98.81741336363734 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "a214c9ee83605eec0ef52b1990786b909f7fbc1b",
          "message": "REL: 1.28.0\n\nThis release adds a lot of deprecation warnings in preparation of the\nPyPDF2 2.0.0 release. The changes are mostly using snake_case function-, method-,\nand variable-names as well as using properties instead of getter-methods.\n\nMaintenance (MAINT):\n-  Remove IronPython Fallback for zlib (#868)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/1.27.12...1.27.13\n\n* Make the `PyPDF2.utils` module private\n* Rename of core classes:\n  * PdfFileReader ➔ PdfReader\n  * PdfFileWriter ➔ PdfWriter\n  * PdfFileMerger ➔ PdfMerger\n* Use PEP8 conventions for function names and parameters\n* If a property and a getter-method are both present, use the property\n\nIn many places:\n  - getObject ➔ get_object\n  - writeToStream ➔ write_to_stream\n  - readFromStream ➔ read_from_stream\n\nPyPDF2.generic\n  - readObject ➔ read_object\n  - convertToInt ➔ convert_to_int\n  - DocumentInformation.getText ➔ DocumentInformation._get_text :\n    This method should typically not be used; please let me know if you need it.\n\nPdfReader class:\n  - `reader.getPage(pageNumber)` ➔ `reader.pages[page_number]`\n  - `reader.getNumPages()` / `reader.numPages` ➔ `len(reader.pages)`\n  - getDocumentInfo ➔ metadata\n  - flattenedPages attribute ➔ flattened_pages\n  - resolvedObjects attribute ➔ resolved_objects\n  - xrefIndex attribute ➔ xref_index\n  - getNamedDestinations / namedDestinations attribute ➔ named_destinations\n  - getPageLayout / pageLayout ➔ page_layout attribute\n  - getPageMode / pageMode ➔ page_mode attribute\n  - getIsEncrypted / isEncrypted ➔ is_encrypted attribute\n  - getOutlines ➔ get_outlines\n  - readObjectHeader ➔ read_object_header (TODO: read vs get?)\n  - cacheGetIndirectObject ➔ cache_get_indirect_object (TODO: public vs private?)\n  - cacheIndirectObject ➔ cache_indirect_object (TODO: public vs private?)\n  - getDestinationPageNumber ➔ get_destination_page_number\n  - readNextEndLine ➔ read_next_end_line\n  - _zeroXref ➔ _zero_xref\n  - _authenticateUserPassword ➔ _authenticate_user_password\n  - _pageId2Num attribute ➔ _page_id2num\n  - _buildDestination ➔ _build_destination\n  - _buildOutline ➔ _build_outline\n  - _getPageNumberByIndirect(indirectRef) ➔ _get_page_number_by_indirect(indirect_ref)\n  - _getObjectFromStream ➔ _get_object_from_stream\n  - _decryptObject ➔ _decrypt_object\n  - _flatten(..., indirectRef) ➔ _flatten(..., indirect_ref)\n  - _buildField ➔ _build_field\n  - _checkKids ➔ _check_kids\n  - _writeField ➔ _write_field\n  - _write_field(..., fieldAttributes) ➔ _write_field(..., field_attributes)\n  - _read_xref_subsections(..., getEntry, ...) ➔ _read_xref_subsections(..., get_entry, ...)\n\nPdfWriter class:\n  - `writer.getPage(pageNumber)` ➔ `writer.pages[page_number]`\n  - `writer.getNumPages()` ➔ `len(writer.pages)`\n  - addMetadata ➔ add_metadata\n  - addPage ➔ add_page\n  - addBlankPage ➔ add_blank_page\n  - addAttachment(fname, fdata) ➔ add_attachment(filename, data)\n  - insertPage ➔ insert_page\n  - insertBlankPage ➔ insert_blank_page\n  - appendPagesFromReader ➔ append_pages_from_reader\n  - updatePageFormFieldValues ➔ update_page_form_field_values\n  - cloneReaderDocumentRoot ➔ clone_reader_document_root\n  - cloneDocumentFromReader ➔ clone_document_from_reader\n  - getReference ➔ get_reference\n  - getOutlineRoot ➔ get_outline_root\n  - getNamedDestRoot ➔ get_named_dest_root\n  - addBookmarkDestination ➔ add_bookmark_destination\n  - addBookmarkDict ➔ add_bookmark_dict\n  - addBookmark ➔ add_bookmark\n  - addNamedDestinationObject ➔ add_named_destination_object\n  - addNamedDestination ➔ add_named_destination\n  - removeLinks ➔ remove_links\n  - removeImages(ignoreByteStringObject) ➔ remove_images(ignore_byte_string_object)\n  - removeText(ignoreByteStringObject) ➔ remove_text(ignore_byte_string_object)\n  - addURI ➔ add_uri\n  - addLink ➔ add_link\n  - getPage(pageNumber) ➔ get_page(page_number)\n  - getPageLayout / setPageLayout / pageLayout ➔ page_layout attribute\n  - getPageMode / setPageMode / pageMode ➔ page_mode attribute\n  - _addObject ➔ _add_object\n  - _addPage ➔ _add_page\n  - _sweepIndirectReferences ➔ _sweep_indirect_references\n\nPdfMerger class\n  - `__init__` parameter: strict=True ➔ strict=False (the PdfFileMerger still has the old default)\n  - addMetadata ➔ add_metadata\n  - addNamedDestination ➔ add_named_destination\n  - setPageLayout ➔ set_page_layout\n  - setPageMode ➔ set_page_mode\n\nPage class:\n  - artBox / bleedBox/ cropBox/ mediaBox / trimBox ➔ artbox / bleedbox/ cropbox/ mediabox / trimbox\n    - getWidth, getHeight  ➔ width / height\n    - getLowerLeft_x / getUpperLeft_x ➔ left\n    - getUpperRight_x / getLowerRight_x ➔ right\n    - getLowerLeft_y / getLowerRight_y ➔ bottom\n    - getUpperRight_y / getUpperLeft_y ➔ top\n    - getLowerLeft / setLowerLeft ➔ lower_left property\n    - upperRight ➔ upper_right\n  - mergePage ➔ merge_page\n  - rotateClockwise / rotateCounterClockwise ➔ rotate_clockwise\n  - _mergeResources ➔ _merge_resources\n  - _contentStreamRename ➔ _content_stream_rename\n  - _pushPopGS ➔ _push_pop_gs\n  - _addTransformationMatrix ➔ _add_transformation_matrix\n  - _mergePage ➔ _merge_page\n\nXmpInformation class:\n  - getElement(..., aboutUri, ...) ➔ get_element(..., about_uri, ...)\n  - getNodesInNamespace(..., aboutUri, ...) ➔ get_nodes_in_namespace(..., aboutUri, ...)\n  - _getText ➔ _get_text\n\nutils.py:\n  - matrixMultiply ➔ matrix_multiply\n  - RC4_encrypt is moved to the security module",
          "timestamp": "2022-05-22T17:27:20+02:00",
          "tree_id": "8428e9bdfa47db0fc96802dea7a440e3b6635807",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a214c9ee83605eec0ef52b1990786b909f7fbc1b"
        },
        "date": 1653233327515,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5019163662253934,
            "unit": "iter/sec",
            "range": "stddev: 0.0424229428461148",
            "extra": "mean: 1.9923638026000021 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.030111690231465,
            "unit": "iter/sec",
            "range": "stddev: 0.0024678264836649672",
            "extra": "mean: 124.53126912499712 msec\nrounds: 8"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "560d2a7d63d6038b36401af794e1c41187c71710",
          "message": "MAINT: Remove duplicate warnings imports (#888)",
          "timestamp": "2022-05-22T21:05:14+02:00",
          "tree_id": "2cc6ee7eb85291f54ffe2a3b186e11052bec1f14",
          "url": "https://github.com/py-pdf/PyPDF2/commit/560d2a7d63d6038b36401af794e1c41187c71710"
        },
        "date": 1653246357077,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.4807529335221447,
            "unit": "iter/sec",
            "range": "stddev: 0.027920571749779174",
            "extra": "mean: 2.0800705107999873 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.218363597837061,
            "unit": "iter/sec",
            "range": "stddev: 0.003874427666178201",
            "extra": "mean: 138.53555400002904 msec\nrounds: 8"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ce1cb6697f9db60c5188624e56da1c676b1733f5",
          "message": "BUG: Incorrectly show deprecation warnings on internal usage (#887)",
          "timestamp": "2022-05-22T21:09:29+02:00",
          "tree_id": "4a67d62b70feac3bb3c63c66eded8d307164da7f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ce1cb6697f9db60c5188624e56da1c676b1733f5"
        },
        "date": 1653246626985,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5064319620757102,
            "unit": "iter/sec",
            "range": "stddev: 0.1197135605168158",
            "extra": "mean: 1.974598909400001 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.56222227677507,
            "unit": "iter/sec",
            "range": "stddev: 0.009266148921254243",
            "extra": "mean: 116.79210929999897 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f74d733ae5e93b2fa73e912754c9158f6018d851",
          "message": "MAINT: Add stacklevel=2 to deprecation warnings (#889)\n\n* STY: Adjust code/docs in several places to make it more similar to the 2.0.0 branch\r\n* MAINT: Remove excessive <py36 warnings",
          "timestamp": "2022-05-22T21:44:31+02:00",
          "tree_id": "d99fa7a659ed8b2e1c4b8c2be88325447fde672c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f74d733ae5e93b2fa73e912754c9158f6018d851"
        },
        "date": 1653248707485,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6584098089297077,
            "unit": "iter/sec",
            "range": "stddev: 0.007816245602955785",
            "extra": "mean: 1.5188109084000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.522844651050827,
            "unit": "iter/sec",
            "range": "stddev: 0.0009774204855581411",
            "extra": "mean: 105.0106387999989 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "000ac498ecc9343c11b89a785314b72730419818",
          "message": "REL: 1.28.1\n\nBug Fixes (BUG):\n-  Incorrectly show deprecation warnings on internal usage (#887)\n\nMaintenance (MAINT):\n-  Add stacklevel=2 to deprecation warnings (#889)\n-  Remove duplicate warnings imports (#888)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/1.28.0...1.28.1",
          "timestamp": "2022-05-22T21:52:56+02:00",
          "tree_id": "71669813a6c12b4757f2588a0336cb4336aadc0e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/000ac498ecc9343c11b89a785314b72730419818"
        },
        "date": 1653249243477,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6625144684497531,
            "unit": "iter/sec",
            "range": "stddev: 0.009516052739706142",
            "extra": "mean: 1.5094009982000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.558250576948518,
            "unit": "iter/sec",
            "range": "stddev: 0.0009916151322350054",
            "extra": "mean: 104.62165559999903 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "68c9202a456c0193ab2e4fc8a66b2c3ec70b91e4",
          "message": "BUG: Fix deprecation warning on using PdfMerger (#891)\n\nFixes a deprecation warning being raised when trying to use the PdfMerger class. This regression of #887 is caused by #889 which reversed the changes done to the PyPDF2/merger.py module so that it once again used the deprecated user-facing isString method as opposed to the internal _isString method.\r\n\r\nAdditionally, this PR fixes the deprecation warning raised by referencing reader.namedDestinations as opposed to reader.named_destinations.\r\n\r\nCloses #890",
          "timestamp": "2022-05-23T13:27:38+02:00",
          "tree_id": "550d2e550045da3b18574419d3f540f0221b0de4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/68c9202a456c0193ab2e4fc8a66b2c3ec70b91e4"
        },
        "date": 1653305301488,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6630140442381052,
            "unit": "iter/sec",
            "range": "stddev: 0.005091146774385556",
            "extra": "mean: 1.5082636766000008 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.511981827358483,
            "unit": "iter/sec",
            "range": "stddev: 0.0011029492997410102",
            "extra": "mean: 105.13056250000261 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9947c7b51f9e413458cc91eca2a1250829662fea",
          "message": "BUG: PendingDeprecationWarning for getContents (#893)",
          "timestamp": "2022-05-23T13:37:07+02:00",
          "tree_id": "e8f2a13bff3d852bfc64a168bb13d52f0b3a9eed",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9947c7b51f9e413458cc91eca2a1250829662fea"
        },
        "date": 1653305866099,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6384252319257784,
            "unit": "iter/sec",
            "range": "stddev: 0.0018992346807512022",
            "extra": "mean: 1.5663541319999978 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.974341227663079,
            "unit": "iter/sec",
            "range": "stddev: 0.0016946913288356541",
            "extra": "mean: 111.42879177777824 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "c68b98d91fe6651215b81a1b1b20fc1a30b9d7e8",
          "message": "REL: 1.28.2\n\nBug Fixes (BUG):\n-  PendingDeprecationWarning for getContents (#893)\n-  PendingDeprecationWarning on using PdfMerger (#891)",
          "timestamp": "2022-05-23T13:43:15+02:00",
          "tree_id": "6df9d2cded070e2146f228642d5b63f6dfd33b71",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c68b98d91fe6651215b81a1b1b20fc1a30b9d7e8"
        },
        "date": 1653306253091,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6522020864438595,
            "unit": "iter/sec",
            "range": "stddev: 0.004528216613580067",
            "extra": "mean: 1.5332670973999996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.312115022439992,
            "unit": "iter/sec",
            "range": "stddev: 0.0009052046268716951",
            "extra": "mean: 107.38698970000229 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "97c55d4612adce6ee70a5df008c13db4840be6d9",
          "message": "Fix merge issues",
          "timestamp": "2022-05-24T08:08:25+02:00",
          "tree_id": "fc4c0b89f3f49844d3d1d8f5ad9150e82d296d90",
          "url": "https://github.com/py-pdf/PyPDF2/commit/97c55d4612adce6ee70a5df008c13db4840be6d9"
        },
        "date": 1653372549207,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.771204347955331,
            "unit": "iter/sec",
            "range": "stddev: 0.010726238644160878",
            "extra": "mean: 1.2966731874000288 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.032410021243166,
            "unit": "iter/sec",
            "range": "stddev: 0.005255479359061474",
            "extra": "mean: 90.64202636363916 msec\nrounds: 11"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "1deb46a292cbcf466f9f36d8c004d7f4c18d9345",
          "message": "Fix mypy issues",
          "timestamp": "2022-05-24T08:17:33+02:00",
          "tree_id": "49b82dce5682459f8b9039275f791f7c07036b22",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1deb46a292cbcf466f9f36d8c004d7f4c18d9345"
        },
        "date": 1653373097547,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6917682133438199,
            "unit": "iter/sec",
            "range": "stddev: 0.058338258771737456",
            "extra": "mean: 1.4455709017999994 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.593165267287814,
            "unit": "iter/sec",
            "range": "stddev: 0.007062289635730386",
            "extra": "mean: 104.24088110000014 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "43276ab5002e37cd2c654cdbe67bbfa0b1fe2eb3",
          "message": "BUG: PendingDeprecationWarning on merge/transform PageObject (#898)",
          "timestamp": "2022-05-25T08:48:04+02:00",
          "tree_id": "648b3230b8d3069270401c9372d91118335baba1",
          "url": "https://github.com/py-pdf/PyPDF2/commit/43276ab5002e37cd2c654cdbe67bbfa0b1fe2eb3"
        },
        "date": 1653461327364,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6145136363540324,
            "unit": "iter/sec",
            "range": "stddev: 0.020197637681566464",
            "extra": "mean: 1.6273031887999991 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.866059490606984,
            "unit": "iter/sec",
            "range": "stddev: 0.004971974635072921",
            "extra": "mean: 112.7896785555562 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f2be61f6c9d398c9381c5a2cbc9c7d4424508001",
          "message": "BUG: Use get_outlines instead of getOutlines (#897)\n\nThis removes a PendingDeprecationWarning",
          "timestamp": "2022-05-25T17:26:37+02:00",
          "tree_id": "2deaf5433081c231fa2a09c3c651239fea659396",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f2be61f6c9d398c9381c5a2cbc9c7d4424508001"
        },
        "date": 1653492440764,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6843738934384183,
            "unit": "iter/sec",
            "range": "stddev: 0.0109943253786307",
            "extra": "mean: 1.4611895771999996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.501997345022126,
            "unit": "iter/sec",
            "range": "stddev: 0.004374873728489817",
            "extra": "mean: 105.241031300001 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e8513e78fa8b532226e74cfda67e842376853a5e",
          "message": "TST: Improve tests for convert_to_int (#899)\n\nThis includes testing that convertToInt raises a pending deprecation warning",
          "timestamp": "2022-05-25T22:26:02+02:00",
          "tree_id": "1e6ecaf8f61c23b545067180b23ec301a8b7d28e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e8513e78fa8b532226e74cfda67e842376853a5e"
        },
        "date": 1653510411244,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5098313065594567,
            "unit": "iter/sec",
            "range": "stddev: 0.0639444041788556",
            "extra": "mean: 1.9614330998000014 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.552076659136676,
            "unit": "iter/sec",
            "range": "stddev: 0.00879345656556602",
            "extra": "mean: 132.41391012499548 msec\nrounds: 8"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "787c784c5ec1c68737717321204943071722e8dc",
          "message": "DEP: PEP8 renaming (#900)\n\nPyPDF2 interface changes:\r\n\r\n* getXmpMetadata / xmpMetadata ➔ xmp_metadata\r\n* get_outlines ➔ _get_outlines (use outlines property instead)\r\n* getXmpMetadata ➔ xmp_metadata\r\n* getDestArray ➔ dest_array\r\n* additionalActions ➔ additional_actions\r\n* defaultValue ➔ default_value\r\n* mappingName ➔ mapping_name\r\n* altName ➔ alternate_name\r\n* fieldType ➔ field_type\r\n* ensureIsNumber ➔ _ensure_is_number\r\n* decodedSelf : decoded_self\r\n* addChild / removeChild  ➔ add_child / remove_child\r\n* flateEncode  ➔ flate_encode\r\n* getData / setData  ➔ get_data / set_data\r\n\r\nDOC: Use the new PyPDF2 interface\r\nSTY: Use reader/writer as variable names for PdfReader / PdfWriter\r\nMAINT: Let pytest capture many warnings\r\n\r\nFixes:\r\n\r\n* add_named_destionation was a typo and thus removed\r\n* Add missing `PendingDeprecationWarning` in warnings\r\n* Add missing `stacklevel=2` in warnings\r\n* merge_rotated_scaled_translated_page ➔ mergeRotatedScaledTranslatedPage: That renaming was not part of the 1.28.0 release and the complete function should be deprecated; no point in adding a renamed one first\r\n* add_transformation: Add missing parameter type annotation",
          "timestamp": "2022-05-26T11:02:38+02:00",
          "tree_id": "526f0bc4bebf7c4822ba763edb94050bbb376469",
          "url": "https://github.com/py-pdf/PyPDF2/commit/787c784c5ec1c68737717321204943071722e8dc"
        },
        "date": 1653555806616,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5828429273514482,
            "unit": "iter/sec",
            "range": "stddev: 0.04039565289623298",
            "extra": "mean: 1.7157281200000056 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.379888478823906,
            "unit": "iter/sec",
            "range": "stddev: 0.00774379559540266",
            "extra": "mean: 119.33333033333484 msec\nrounds: 9"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "68515c94dab84472ab634e297a8da73d28a0ca6e",
          "message": "TST: Remove -OO testrun from CI (#901)\n\nWe needed it because we were manipulating a docstring programmatically.\r\n\r\nAs long as we don't rely on assert / docstrings being present, we don't need to test with -OO.",
          "timestamp": "2022-05-26T14:12:55+02:00",
          "tree_id": "5d7f931822a7ac707c3a6b15a734b87a2f79a1ba",
          "url": "https://github.com/py-pdf/PyPDF2/commit/68515c94dab84472ab634e297a8da73d28a0ca6e"
        },
        "date": 1653567218638,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6833658274627129,
            "unit": "iter/sec",
            "range": "stddev: 0.008813469618698819",
            "extra": "mean: 1.463345048599996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.791071555138185,
            "unit": "iter/sec",
            "range": "stddev: 0.0051502754177186385",
            "extra": "mean: 102.13386700000342 msec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ed952f91889fb6acc238ab0368fe93f2d533c1c6",
          "message": "TST: Use new PyPDF2 API in benchmark (#902)",
          "timestamp": "2022-05-26T17:11:15+02:00",
          "tree_id": "13936811568a88831180966ca0e33cb890d02bda",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ed952f91889fb6acc238ab0368fe93f2d533c1c6"
        },
        "date": 1653577926882,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.510090187706591,
            "unit": "iter/sec",
            "range": "stddev: 0.0189891174726544",
            "extra": "mean: 1.9604376326000021 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.7421016818198245,
            "unit": "iter/sec",
            "range": "stddev: 0.004520191677219272",
            "extra": "mean: 129.1638938749955 msec\nrounds: 8"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "35e014d6b29afa3b2d7542b573a08e2590ab6a09",
          "message": "TST: Checkout submodule sample-files for benchmark",
          "timestamp": "2022-05-26T17:41:30+02:00",
          "tree_id": "7462c8a1f186c0c7383871d2fcbe16d460009916",
          "url": "https://github.com/py-pdf/PyPDF2/commit/35e014d6b29afa3b2d7542b573a08e2590ab6a09"
        },
        "date": 1653579756179,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6390759580068262,
            "unit": "iter/sec",
            "range": "stddev: 0.010086733213925581",
            "extra": "mean: 1.5647592237999959 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.625701599702232,
            "unit": "iter/sec",
            "range": "stddev: 0.005047605209700734",
            "extra": "mean: 103.88853110000156 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25905673112664573,
            "unit": "iter/sec",
            "range": "stddev: 0.014109017577951586",
            "extra": "mean: 3.860158335400007 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c4c2830f28ef04dfb3783ce02e29bdc61f0e3c14",
          "message": "DOC: Add missing deprecation warning for addChild (#906)",
          "timestamp": "2022-05-26T22:41:23+02:00",
          "tree_id": "1e3cf2170c37cf24678d39682bf06ccf7ce4c0f2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c4c2830f28ef04dfb3783ce02e29bdc61f0e3c14"
        },
        "date": 1653597749040,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6310287582032477,
            "unit": "iter/sec",
            "range": "stddev: 0.013924301839389416",
            "extra": "mean: 1.5847138295999983 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.612403088256832,
            "unit": "iter/sec",
            "range": "stddev: 0.006733940730991103",
            "extra": "mean: 104.03225819999875 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2596070072934622,
            "unit": "iter/sec",
            "range": "stddev: 0.010628353561790906",
            "extra": "mean: 3.851976148200001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b387b06718c5347ea641b06acd44ee636b7ca864",
          "message": "DOC: Transformation (#907)",
          "timestamp": "2022-05-26T22:45:24+02:00",
          "tree_id": "646ce26c96a1e1411d15e44e3f291ce38190ffb7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b387b06718c5347ea641b06acd44ee636b7ca864"
        },
        "date": 1653597991977,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6372041428285101,
            "unit": "iter/sec",
            "range": "stddev: 0.009543635355993176",
            "extra": "mean: 1.569355772800003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.802414860582097,
            "unit": "iter/sec",
            "range": "stddev: 0.005097601494057465",
            "extra": "mean: 102.01567819999582 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2619065971790734,
            "unit": "iter/sec",
            "range": "stddev: 0.020114326419335065",
            "extra": "mean: 3.8181550628000025 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b4d54ed59486abfcd429a281c4d12cc09780636b",
          "message": "BUG: Fix error adding transformation to page without /Contents (#908)",
          "timestamp": "2022-05-27T07:58:27+02:00",
          "tree_id": "0f8292364f95a29f7250bed2e892a8899b71735e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b4d54ed59486abfcd429a281c4d12cc09780636b"
        },
        "date": 1653631174546,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6328943629802469,
            "unit": "iter/sec",
            "range": "stddev: 0.011030135335598736",
            "extra": "mean: 1.580042513399998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.751811863239821,
            "unit": "iter/sec",
            "range": "stddev: 0.004706856007834518",
            "extra": "mean: 102.54504640000022 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2625315831703426,
            "unit": "iter/sec",
            "range": "stddev: 0.005789307845957156",
            "extra": "mean: 3.8090655147999994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "892299cd2404678b796ffa1b8bc4cf17e8f9abeb",
          "message": "BUG: Add getPage back (#909)\n\nThis is one of the core methods that a lot of people use. It should not\r\nbe removed already.\r\n\r\nIt was removed by accident.",
          "timestamp": "2022-05-27T09:02:18+02:00",
          "tree_id": "3fb9279570c19745518623d94bf9580e602295df",
          "url": "https://github.com/py-pdf/PyPDF2/commit/892299cd2404678b796ffa1b8bc4cf17e8f9abeb"
        },
        "date": 1653635008988,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.637461245172277,
            "unit": "iter/sec",
            "range": "stddev: 0.004848008414319655",
            "extra": "mean: 1.568722816600004 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.499077246812703,
            "unit": "iter/sec",
            "range": "stddev: 0.004065436979686178",
            "extra": "mean: 105.27338329999765 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2575180535819096,
            "unit": "iter/sec",
            "range": "stddev: 0.009681330626451035",
            "extra": "mean: 3.883222889000001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "24993292fcf65353e4494580b4ca76055ff0589d",
          "message": "BUG: Add PdfObject.getObject back (#911)",
          "timestamp": "2022-05-27T13:15:16+02:00",
          "tree_id": "18f5d4883dd3fa19df6b98ab84153c230ca680b8",
          "url": "https://github.com/py-pdf/PyPDF2/commit/24993292fcf65353e4494580b4ca76055ff0589d"
        },
        "date": 1653650183782,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6387413219007096,
            "unit": "iter/sec",
            "range": "stddev: 0.0072649780466469815",
            "extra": "mean: 1.5655790000000138 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.534368346414464,
            "unit": "iter/sec",
            "range": "stddev: 0.0037511945870815112",
            "extra": "mean: 104.88371789999746 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25657372492503333,
            "unit": "iter/sec",
            "range": "stddev: 0.004484241365494187",
            "extra": "mean: 3.8975152279999974 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f060edb1bd87d0c3eb33198f9c9ea4f9bb18c36f",
          "message": "BUG: XmpInformation missing method _getText (#915)\n\nSee #914",
          "timestamp": "2022-05-28T10:26:38+02:00",
          "tree_id": "1fecfbb6ec799af7732befab89bcdf10816a86cc",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f060edb1bd87d0c3eb33198f9c9ea4f9bb18c36f"
        },
        "date": 1653726481973,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5532821623066452,
            "unit": "iter/sec",
            "range": "stddev: 0.02228751468635365",
            "extra": "mean: 1.8073960596000034 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.315293711691115,
            "unit": "iter/sec",
            "range": "stddev: 0.005200334789145117",
            "extra": "mean: 120.26033411111176 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2243269440821604,
            "unit": "iter/sec",
            "range": "stddev: 0.045037400684582674",
            "extra": "mean: 4.457779265400001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "7f779bda3393708abfde92337ed1b5ab2b64556f",
          "message": "DOC: CHANGELOG of 1.28.x",
          "timestamp": "2022-05-28T10:47:14+02:00",
          "tree_id": "36414684d6466a9cc056985b3e0c85c4182d72d5",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7f779bda3393708abfde92337ed1b5ab2b64556f"
        },
        "date": 1653727710527,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6426272457508126,
            "unit": "iter/sec",
            "range": "stddev: 0.03653620241095908",
            "extra": "mean: 1.5561120488000029 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.153684291621575,
            "unit": "iter/sec",
            "range": "stddev: 0.005313761070886646",
            "extra": "mean: 98.4864184545467 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26292404620164206,
            "unit": "iter/sec",
            "range": "stddev: 0.044245215478784676",
            "extra": "mean: 3.803379776200001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bb68a4b16430fe9a7b0d536f42c7598d267f0922",
          "message": "DEV: Refine Any in xmp module (#918)\n\nSee #914",
          "timestamp": "2022-05-28T11:13:37+02:00",
          "tree_id": "5642a3006db2254b4486c8bc7b041410d3ee38d6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/bb68a4b16430fe9a7b0d536f42c7598d267f0922"
        },
        "date": 1653729285857,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6385451215492326,
            "unit": "iter/sec",
            "range": "stddev: 0.008867337831956685",
            "extra": "mean: 1.5660600422000073 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.780389290380487,
            "unit": "iter/sec",
            "range": "stddev: 0.005454079796788924",
            "extra": "mean: 102.24541889999728 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2619138047707187,
            "unit": "iter/sec",
            "range": "stddev: 0.015759507510597664",
            "extra": "mean: 3.818049991199996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "07bb859e91ce61d053a7abd3eac71665d92e10b7",
          "message": "DEP: rotate_clockwise ➔ rotate for PageObject (#913)\n\nSigned-off-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-05-28T12:10:43+02:00",
          "tree_id": "7e32ed194f855d3647885b18c96ca7fab3b081e0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/07bb859e91ce61d053a7abd3eac71665d92e10b7"
        },
        "date": 1653732706239,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6339722412682771,
            "unit": "iter/sec",
            "range": "stddev: 0.01039634774391367",
            "extra": "mean: 1.5773561283999995 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.644043969217911,
            "unit": "iter/sec",
            "range": "stddev: 0.0066782293305035646",
            "extra": "mean: 103.69094159999932 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2616231286706273,
            "unit": "iter/sec",
            "range": "stddev: 0.012933309796893715",
            "extra": "mean: 3.8222920315999986 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bbfd46ccc9d22b1444e2293943dab5baabab4af6",
          "message": "DEV: Create flake8 config file (#916)\n\nSigned-off-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-05-28T21:13:08+02:00",
          "tree_id": "aa186de9291efb7afd30e8ff30051a7b6bda8cf6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/bbfd46ccc9d22b1444e2293943dab5baabab4af6"
        },
        "date": 1653765256179,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6280606999463212,
            "unit": "iter/sec",
            "range": "stddev: 0.015485614735069498",
            "extra": "mean: 1.592202791999989 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.72505636703493,
            "unit": "iter/sec",
            "range": "stddev: 0.005130952401877954",
            "extra": "mean: 102.82716749999565 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26085810797089304,
            "unit": "iter/sec",
            "range": "stddev: 0.00583720631038026",
            "extra": "mean: 3.833501698599997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7647ab5f35f386050943fbe1be74351d8e5aac91",
          "message": "DOC: Adjust deprecation messages (#919)\n\nWe are trying to break as few running systems as possible. For this\r\nreason we keep the adapter methods / classes in PyPDF2 until 3.0.0.\r\n\r\nThis commit is done to not confuse people. It will not be backported\r\nto the 1.x branch though.\r\n\r\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-05-29T10:40:49+02:00",
          "tree_id": "b19dbb6317897b4b6fd65686586b65f0b68d19e8",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7647ab5f35f386050943fbe1be74351d8e5aac91"
        },
        "date": 1653813734986,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5436673309935659,
            "unit": "iter/sec",
            "range": "stddev: 0.03892472591495414",
            "extra": "mean: 1.8393601068000067 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.155094005486639,
            "unit": "iter/sec",
            "range": "stddev: 0.009736845348701825",
            "extra": "mean: 122.62274344443034 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21894056292532493,
            "unit": "iter/sec",
            "range": "stddev: 0.07996699178911772",
            "extra": "mean: 4.567449661399996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c59224a423f81adfd16cc471322803dcaabe93e0",
          "message": "ENH: Allow setting the decryption password in PdfReader.__init__ (#920)\n\nThis is a convenience change. You can still call `reader = PdfReader(\"encrypted.pdf\"); reader.decrypt(password)`.\r\n\r\nFull credit to pubpub-zz; I just made stylistic changes.\r\n\r\nCloses #910 \r\n\r\nCo-authored-by: pubpub-zz <4083478+pubpub-zz@users.noreply.github.com>",
          "timestamp": "2022-05-29T10:57:37+02:00",
          "tree_id": "b9df8cfaa87cae9db324394306ded3cd8ab6d404",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c59224a423f81adfd16cc471322803dcaabe93e0"
        },
        "date": 1653814738168,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5426886180795918,
            "unit": "iter/sec",
            "range": "stddev: 0.01200177887464513",
            "extra": "mean: 1.842677304599998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.408381666556158,
            "unit": "iter/sec",
            "range": "stddev: 0.005342018483201632",
            "extra": "mean: 118.92894966666903 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22392693607740943,
            "unit": "iter/sec",
            "range": "stddev: 0.007376436019779131",
            "extra": "mean: 4.4657423421999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c008b0f448219d4727a8ba07570aba0abf4321e2",
          "message": "ENH: Improve space setting for text extraction (#922)\n\nFull credit to pubpub-zz who introduced this change in\r\nhttps://github.com/py-pdf/PyPDF2/pull/881\r\n\r\nCo-authored-by: pubpub-zz <4083478+pubpub-zz@users.noreply.github.com>",
          "timestamp": "2022-05-29T14:14:07+02:00",
          "tree_id": "6d3f36d7972ccad55ee119863d23366a9f1c55d3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c008b0f448219d4727a8ba07570aba0abf4321e2"
        },
        "date": 1653826517554,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6377037001130151,
            "unit": "iter/sec",
            "range": "stddev: 0.01050493276016348",
            "extra": "mean: 1.5681263882000025 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.709615217367169,
            "unit": "iter/sec",
            "range": "stddev: 0.005795550970974708",
            "extra": "mean: 102.99069300000099 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22762323826531633,
            "unit": "iter/sec",
            "range": "stddev: 0.014775597994005173",
            "extra": "mean: 4.393224556599998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "42d465968b8333c126ab6967b882c945103672db",
          "message": "TST: Regression test for xmp_metadata converter (#923)",
          "timestamp": "2022-05-29T15:44:39+02:00",
          "tree_id": "9ea6d5bbf4406b9f30e8a1318236e22e03a3af0d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/42d465968b8333c126ab6967b882c945103672db"
        },
        "date": 1653831961663,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5389565502691088,
            "unit": "iter/sec",
            "range": "stddev: 0.009812206401642437",
            "extra": "mean: 1.8554371396000022 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.157595218807504,
            "unit": "iter/sec",
            "range": "stddev: 0.006128000578427391",
            "extra": "mean: 122.5851458888864 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19231766736649508,
            "unit": "iter/sec",
            "range": "stddev: 0.006270496958427273",
            "extra": "mean: 5.199730288399996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "552767ebff5c4b93e1756ab111da6f2418a19cb7",
          "message": "DOC: CHANGELOG of 1.28.4 (#926)",
          "timestamp": "2022-05-30T15:19:20Z",
          "tree_id": "653ab65f3e658259f53b1a497f8238743b7878c6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/552767ebff5c4b93e1756ab111da6f2418a19cb7"
        },
        "date": 1653924030761,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6339928082229468,
            "unit": "iter/sec",
            "range": "stddev: 0.006491794857137019",
            "extra": "mean: 1.5773049584000092 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.744753270628017,
            "unit": "iter/sec",
            "range": "stddev: 0.005343201676564059",
            "extra": "mean: 102.61932470000374 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22816372880708463,
            "unit": "iter/sec",
            "range": "stddev: 0.016290571847674545",
            "extra": "mean: 4.382817572400006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1d14a86f975b5b9e06badba5908e26e7a9d33932",
          "message": "DOC: Fix style of 1.25 and 1.27 patch notes (#927)",
          "timestamp": "2022-05-30T20:08:40+02:00",
          "tree_id": "734b059e8b07cb5afcc9502253dcd6287a6d0908",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1d14a86f975b5b9e06badba5908e26e7a9d33932"
        },
        "date": 1653934211418,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.4727539530556145,
            "unit": "iter/sec",
            "range": "stddev: 0.03327161361334232",
            "extra": "mean: 2.1152652316 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.172594257553638,
            "unit": "iter/sec",
            "range": "stddev: 0.005543246503278477",
            "extra": "mean: 139.41956899999954 msec\nrounds: 7"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1682061105658021,
            "unit": "iter/sec",
            "range": "stddev: 0.06999002272493746",
            "extra": "mean: 5.945087230399997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "57301980b8c44273a53d42ea4041ff7d73697f6f",
          "message": "MAINT: Add wrapper function for PendingDeprecationWarnings (#928)\n\nSigned-off-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-06-01T07:37:32+02:00",
          "tree_id": "dd2a6428546c94917ab8a65362431d08c3e62add",
          "url": "https://github.com/py-pdf/PyPDF2/commit/57301980b8c44273a53d42ea4041ff7d73697f6f"
        },
        "date": 1654061923923,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6421287187167684,
            "unit": "iter/sec",
            "range": "stddev: 0.0034513948440242823",
            "extra": "mean: 1.557320161600002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.854278467705628,
            "unit": "iter/sec",
            "range": "stddev: 0.004465246440355832",
            "extra": "mean: 101.4787640999991 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22798891273046218,
            "unit": "iter/sec",
            "range": "stddev: 0.017851623559301047",
            "extra": "mean: 4.386178204999998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "f261badb87fdbff08cfd2d19711a0ea6cc024489",
          "message": "REL: 2.0.0\n\nThe 2.0.0 release of PyPDF2 includes three core changes:\n\n1. Dropping support for Python 3.5 and older.\n2. Introducing type annotations.\n3. Interface changes, mostly to have PEP8-compliant names\n\nWe introduced a [deprecation process](https://github.com/py-pdf/PyPDF2/pull/930)\nthat hopefully helps users to avoid unexpected breaking changes.\n\nBreaking Changes(DEP):\n- PyPDF2 2.0 requires Python 3.6+. Python 2.7 and 3.5 support were dropped.\n- PdfFileReader: The \"warndest\" parameter was removed\n- PdfFileReader and PdfFileMerger no longer have the `overwriteWarnings`\n  parameter. The new behavior is `overwriteWarnings=False`.\n- merger: OutlinesObject was removed without replacement.\n- merger.py ➔ _merger.py: You must import PdfFileMerger from PyPDF2 directly.\n- utils:\n  * `ConvertFunctionsToVirtualList` was removed\n  * `formatWarning` was removed\n  * `isInt(obj)`: Use `instance(obj, int)` instead\n  * `u_(s)`: Use `s` directly\n  * `chr_(c)`: Use `chr(c)` instead\n  * `barray(b)`: Use `bytearray(b)` instead\n  * `isBytes(b)`: Use `instance(b, type(bytes()))` instead\n  * `xrange_fn`: Use `range` instead\n  * `string_type`: Use `str` instead\n  * `isString(s)`: Use `instance(s, str)` instead\n  * `_basestring`: Use `str` instead\n  * All Exceptions are now in `PyPDF2.errors`:\n    - PageSizeNotDefinedError\n    - PdfReadError\n    - PdfReadWarning\n    - PyPdfError\n- `PyPDF2.pdf` (the `pdf` module) no longer exists. The contents were moved with\n  the library. You should most likely import directly from `PyPDF2` instead.\n  The `RectangleObject` is in `PyPDF2.generic`.\n- The `Resources`, `Scripts`, and `Tests` will no longer be part of the distribution\n  files on PyPI. This should have little to no impact on most people. The\n  `Tests` are renamed to `tests`, the `Resources` are renamed to `resources`.\n  Both are still in the git repository. The `Scripts` are now in\n  https://github.com/py-pdf/cpdf. `Sample_Code` was moved to the `docs`.\n\nFor a full list of deprecated functions, please see the changelog of version\n1.28.0.\n\nNew Features (ENH):\n-  Improve space setting for text extraction (#922)\n-  Allow setting the decryption password in PdfReader.__init__ (#920)\n-  Add Page.add_transformation (#883)\n\nBug Fixes (BUG):\n-  Fix error adding transformation to page without /Contents (#908)\n\nRobustness (ROB):\n-  Cope with invalid length in streams (#861)\n\nDocumentation (DOC):\n-  Fix style of 1.25 and 1.27 patch notes (#927)\n-  Transformation (#907)\n\nDeveloper Experience (DEV):\n-  Create flake8 config file (#916)\n-  Use relative imports (#875)\n\nMaintenance (MAINT):\n-  Use Python 3.6 language features (#849)\n-  Add wrapper function for PendingDeprecationWarnings (#928)\n-  Use new PEP8 compliant names (#884)\n-  Explicitly represent transformation matrix (#878)\n-  Inline PAGE_RANGE_HELP string (#874)\n-  Remove unnecessary generics imports (#873)\n-  Remove star imports (#865)\n-  merger.py ➔ _merger.py (#864)\n-  Type annotations for all functions/methods (#854)\n-  Add initial type support with mypy (#853)\n\nTesting (TST):\n-  Regression test for xmp_metadata converter (#923)\n-  Checkout submodule sample-files for benchmark\n-  Add text extracting performance benchmark\n-  Use new PyPDF2 API in benchmark (#902)\n-  Make test suite fail for uncaught warnings (#892)\n-  Remove -OO testrun from CI (#901)\n-  Improve tests for convert_to_int (#899)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/1.28.4...2.0.0",
          "timestamp": "2022-06-01T07:56:34+02:00",
          "tree_id": "e09b75f4108e70b0933199d91399b9ca51479cd1",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f261badb87fdbff08cfd2d19711a0ea6cc024489"
        },
        "date": 1654063094576,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6293911413071543,
            "unit": "iter/sec",
            "range": "stddev: 0.007449796172802097",
            "extra": "mean: 1.5888371067999856 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.697491419656135,
            "unit": "iter/sec",
            "range": "stddev: 0.004499510098939933",
            "extra": "mean: 103.11945190001097 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22351325680711265,
            "unit": "iter/sec",
            "range": "stddev: 0.009675818763086945",
            "extra": "mean: 4.474007556799995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5730033d99cef3a2a3862f7893c678a21f04ddb6",
          "message": "DOC: Remove scripts (pdfcat) from docs (#934)",
          "timestamp": "2022-06-01T13:53:28+02:00",
          "tree_id": "ab224f10301c410881cccabe8393f18781f9aecf",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5730033d99cef3a2a3862f7893c678a21f04ddb6"
        },
        "date": 1654084487521,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.550771847845214,
            "unit": "iter/sec",
            "range": "stddev: 0.035537354609884365",
            "extra": "mean: 1.8156338307999988 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.619390034440919,
            "unit": "iter/sec",
            "range": "stddev: 0.00850408893750302",
            "extra": "mean: 116.01749033333577 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19731059596320644,
            "unit": "iter/sec",
            "range": "stddev: 0.16220470685048596",
            "extra": "mean: 5.068151535999999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2cd9968c346e49d2fbea62cec1df99083f79fc7a",
          "message": "DOC: Fix typos on robustness page (#935)",
          "timestamp": "2022-06-01T16:01:43+02:00",
          "tree_id": "7f4edcc936a8f2790a520a2cc6ccc32b6a01a880",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2cd9968c346e49d2fbea62cec1df99083f79fc7a"
        },
        "date": 1654092175626,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6263377512724683,
            "unit": "iter/sec",
            "range": "stddev: 0.006329041894278622",
            "extra": "mean: 1.5965826712000024 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.354537492966712,
            "unit": "iter/sec",
            "range": "stddev: 0.004435092013223816",
            "extra": "mean: 106.89999379999904 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2193640902761155,
            "unit": "iter/sec",
            "range": "stddev: 0.04937498190546385",
            "extra": "mean: 4.5586312634 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ba6614dab89517718f13069a7daf2128533a6f62",
          "message": "DOC: How to deprecate (#930)\n\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-06-01T21:47:33+02:00",
          "tree_id": "2d49580da5b03761df247ae661091abaf82784f3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ba6614dab89517718f13069a7daf2128533a6f62"
        },
        "date": 1654112943259,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5095408487575949,
            "unit": "iter/sec",
            "range": "stddev: 0.05136854419861957",
            "extra": "mean: 1.9625511917999972 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.390364203275787,
            "unit": "iter/sec",
            "range": "stddev: 0.007952162170515756",
            "extra": "mean: 119.18433762500769 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1922970125901679,
            "unit": "iter/sec",
            "range": "stddev: 0.10087548857060111",
            "extra": "mean: 5.200288795599988 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "86697bb74248eeb7c58d87210911fd6d3c754dad",
          "message": "DOC: Example how to use PyPDF2 with AWS S3 (#938)",
          "timestamp": "2022-06-04T09:25:16+02:00",
          "tree_id": "ded411dd8811165832641a2b1ebfc1e576e64bac",
          "url": "https://github.com/py-pdf/PyPDF2/commit/86697bb74248eeb7c58d87210911fd6d3c754dad"
        },
        "date": 1654327598769,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.525201298111016,
            "unit": "iter/sec",
            "range": "stddev: 0.007935124771440894",
            "extra": "mean: 1.9040318513999979 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.963488559659653,
            "unit": "iter/sec",
            "range": "stddev: 0.005670726290716172",
            "extra": "mean: 125.57310687500234 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.18596358303114996,
            "unit": "iter/sec",
            "range": "stddev: 0.012239170040795846",
            "extra": "mean: 5.377396927399997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "66ecb2aa56cc7dc8b9750bb7c8efa25fc94d977b",
          "message": "DOC: rotate vs Transformation().rotate (#937)",
          "timestamp": "2022-06-04T09:25:33+02:00",
          "tree_id": "2818f390178a904b832136dde89de371805cb6ce",
          "url": "https://github.com/py-pdf/PyPDF2/commit/66ecb2aa56cc7dc8b9750bb7c8efa25fc94d977b"
        },
        "date": 1654327615737,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5350349841645092,
            "unit": "iter/sec",
            "range": "stddev: 0.11547220481963218",
            "extra": "mean: 1.8690366603999977 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.1430180112801,
            "unit": "iter/sec",
            "range": "stddev: 0.008005330017546403",
            "extra": "mean: 122.8045914444438 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1815989036975589,
            "unit": "iter/sec",
            "range": "stddev: 0.09197359073393402",
            "extra": "mean: 5.506641172599998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "e853ec1b65ee6b5c761289292b3b2835ec2f4320",
          "message": "STY: Apply black/isort",
          "timestamp": "2022-06-04T09:56:16+02:00",
          "tree_id": "df25fe3173a2a4c9f71434924b7cc3ad8e442441",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e853ec1b65ee6b5c761289292b3b2835ec2f4320"
        },
        "date": 1654329454908,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8837199482265174,
            "unit": "iter/sec",
            "range": "stddev: 0.049089868493836494",
            "extra": "mean: 1.131580204799991 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.292333514552215,
            "unit": "iter/sec",
            "range": "stddev: 0.002525919510115837",
            "extra": "mean: 69.96758080000139 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.3147480678322563,
            "unit": "iter/sec",
            "range": "stddev: 0.013254966845663319",
            "extra": "mean: 3.177144205800005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "christopher.j.donlan@gmail.com",
            "name": "Christopher Donlan",
            "username": "chrisdonlan"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "336eae77462f15ed1d6c1490eaed66f53109026b",
          "message": "BUG: Compare StreamObject.decoded_self with None (#931)\n\nThe 'if self.decoded_self' expression evaluates to 'False', e.g. if decoded_self is an empty dictionary.",
          "timestamp": "2022-06-04T11:11:17+02:00",
          "tree_id": "ae23c5b7486b8493fd8cd4d0dd235a86dc2422fc",
          "url": "https://github.com/py-pdf/PyPDF2/commit/336eae77462f15ed1d6c1490eaed66f53109026b"
        },
        "date": 1654333948261,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6284224757609584,
            "unit": "iter/sec",
            "range": "stddev: 0.009406395668927502",
            "extra": "mean: 1.5912861785999894 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.721812692212684,
            "unit": "iter/sec",
            "range": "stddev: 0.0055667794414109555",
            "extra": "mean: 102.86147570000139 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22225392686342357,
            "unit": "iter/sec",
            "range": "stddev: 0.014263327690127765",
            "extra": "mean: 4.499358072600023 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "2e0byo@gmail.com",
            "name": "2e0byo",
            "username": "2e0byo"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "59db8aa111d65b8bc857c4975830755efc6e76b7",
          "message": "DEV: Automatically create Github releases from tags (#870)\n\nAdditionally add comment how to release to PyPI from Github\r\n\r\nCloses #748",
          "timestamp": "2022-06-04T15:49:07+02:00",
          "tree_id": "b4ee60a66c0fd75762bce8adc1184d7e9390f6e9",
          "url": "https://github.com/py-pdf/PyPDF2/commit/59db8aa111d65b8bc857c4975830755efc6e76b7"
        },
        "date": 1654350636126,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.4693266041059559,
            "unit": "iter/sec",
            "range": "stddev: 0.02987176990297823",
            "extra": "mean: 2.130712368 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.278746961890765,
            "unit": "iter/sec",
            "range": "stddev: 0.007027755611665368",
            "extra": "mean: 137.3862843750011 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.16442657516379156,
            "unit": "iter/sec",
            "range": "stddev: 0.06491701075134328",
            "extra": "mean: 6.081741950799997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "98b4739e5a259940877dcd0b467d263d09c4b636",
          "message": "DOC: Add logo (#942)",
          "timestamp": "2022-06-04T18:06:30+02:00",
          "tree_id": "574613507e209a8c43820eabd80a67c900d466ec",
          "url": "https://github.com/py-pdf/PyPDF2/commit/98b4739e5a259940877dcd0b467d263d09c4b636"
        },
        "date": 1654358877680,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.4928239953722949,
            "unit": "iter/sec",
            "range": "stddev: 0.022206150464091308",
            "extra": "mean: 2.0291219774000013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.869002829210174,
            "unit": "iter/sec",
            "range": "stddev: 0.0074498502089382565",
            "extra": "mean: 127.08090487500456 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.18304707042218185,
            "unit": "iter/sec",
            "range": "stddev: 0.04709477185713704",
            "extra": "mean: 5.463075687000009 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a5d68957dfdfdced04fb0fed1f1416266c65759e",
          "message": "DEV: Mark deprecated code with no-cover (#943)\n\nThis allows us to track the blind spots of our unit tests better",
          "timestamp": "2022-06-04T20:11:06+02:00",
          "tree_id": "d4d7277db09733654e0fd3082583c092241e072f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a5d68957dfdfdced04fb0fed1f1416266c65759e"
        },
        "date": 1654366335860,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6472791889144676,
            "unit": "iter/sec",
            "range": "stddev: 0.010206067055147278",
            "extra": "mean: 1.5449283973999997 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.96590481255386,
            "unit": "iter/sec",
            "range": "stddev: 0.005089665132280091",
            "extra": "mean: 100.34211833333175 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22584435942835684,
            "unit": "iter/sec",
            "range": "stddev: 0.09187806665658418",
            "extra": "mean: 4.427828095999996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kim.brose@rwth-aachen.de",
            "name": "Kim Brose",
            "username": "HarHarLinks"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0358e20f46ffcd4f2dd97c69d48b29797f1d33e7",
          "message": "BUG: Delete .python-version file (#944)",
          "timestamp": "2022-06-04T20:13:24+02:00",
          "tree_id": "7c921f6e1a304625208ef92a6fc3fd2a05fd4ff0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0358e20f46ffcd4f2dd97c69d48b29797f1d33e7"
        },
        "date": 1654366491424,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5584075295029769,
            "unit": "iter/sec",
            "range": "stddev: 0.012905612467001691",
            "extra": "mean: 1.7908067982000033 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.631122267925237,
            "unit": "iter/sec",
            "range": "stddev: 0.00626699297855934",
            "extra": "mean: 115.85978844445005 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19700499690889398,
            "unit": "iter/sec",
            "range": "stddev: 0.03156404400092536",
            "extra": "mean: 5.076013378800008 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "76e38ac36623368f00c4ba5a2a8dc563fe822e63",
          "message": "DEV: Ignore .python-version file",
          "timestamp": "2022-06-04T20:15:12+02:00",
          "tree_id": "3efdb906664ba2a8f70c248501e7f899d4c2a321",
          "url": "https://github.com/py-pdf/PyPDF2/commit/76e38ac36623368f00c4ba5a2a8dc563fe822e63"
        },
        "date": 1654366598159,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5583888110141171,
            "unit": "iter/sec",
            "range": "stddev: 0.10402669096090264",
            "extra": "mean: 1.7908668302000024 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.700993987341445,
            "unit": "iter/sec",
            "range": "stddev: 0.006518565385691636",
            "extra": "mean: 114.92939788888951 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21541168893678758,
            "unit": "iter/sec",
            "range": "stddev: 0.09943470674901421",
            "extra": "mean: 4.642273615399995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "34919f9e97b276628e5c6f06b8bf61ae9c7b5b52",
          "message": "TST: Add test for Tree and _security (#945)",
          "timestamp": "2022-06-04T22:36:28+02:00",
          "tree_id": "1250ddfd7b24a78778f13375a7d89c5bf8c3259f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/34919f9e97b276628e5c6f06b8bf61ae9c7b5b52"
        },
        "date": 1654375060068,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6353542239595663,
            "unit": "iter/sec",
            "range": "stddev: 0.007486306204245972",
            "extra": "mean: 1.5739251621999757 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.833261978595612,
            "unit": "iter/sec",
            "range": "stddev: 0.005285128530493252",
            "extra": "mean: 101.69565319999947 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2263526516994648,
            "unit": "iter/sec",
            "range": "stddev: 0.014375532594736997",
            "extra": "mean: 4.4178850678 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1df859c9a102399494c9a71639f5e24c76d23e5c",
          "message": "TST: writer.remove_text (#946)",
          "timestamp": "2022-06-05T11:48:05+02:00",
          "tree_id": "a7d4e0c5244741d10cf6116980c80b545e8bd151",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1df859c9a102399494c9a71639f5e24c76d23e5c"
        },
        "date": 1654422556094,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6419490450577945,
            "unit": "iter/sec",
            "range": "stddev: 0.005172369430100931",
            "extra": "mean: 1.5577560364000078 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.555296583023976,
            "unit": "iter/sec",
            "range": "stddev: 0.0036395111277391272",
            "extra": "mean: 104.65399909999746 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22341562860688183,
            "unit": "iter/sec",
            "range": "stddev: 0.009688495615550418",
            "extra": "mean: 4.4759626094 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b0084120b77fe450629fdd5b4a1d25f991074c6a",
          "message": "TST: Ignore PdfReadWarning in benchmark (#949)\n\nIgnore the PdfReadWarning in the benchmarking code as it is only supposed to be used for performance testing.",
          "timestamp": "2022-06-06T09:36:23+02:00",
          "tree_id": "17ebc5973cbcc26c9aa75f4a30ea9fe214f80340",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b0084120b77fe450629fdd5b4a1d25f991074c6a"
        },
        "date": 1654501057110,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6289519903492351,
            "unit": "iter/sec",
            "range": "stddev: 0.007449504288683419",
            "extra": "mean: 1.5899464749999992 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.850370993045722,
            "unit": "iter/sec",
            "range": "stddev: 0.005813671722364579",
            "extra": "mean: 101.51901899999416 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23285732582591734,
            "unit": "iter/sec",
            "range": "stddev: 0.00972297056825972",
            "extra": "mean: 4.294475153200006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4baedb2054648b9db70c2fbed82b6902aea52365",
          "message": "STY: black, isort, Flake8, splitting buildCharMap (#950)\n\nThis commit contains several small stylistic changes. Most of then were found by Flake8.\r\n\r\nThe biggest single change is moving buildCharMap to its own module. There it was split into several functions to make it easier to understand how it works. This could also make it easier to understand adjustments in future pull requests.\r\n\r\nA caching mechanism for downloaded files was added to speed up local testing",
          "timestamp": "2022-06-06T13:29:00+02:00",
          "tree_id": "8d9948d6b3047a6988a32500c7b3a0bee18e1198",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4baedb2054648b9db70c2fbed82b6902aea52365"
        },
        "date": 1654515018997,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5508708108708029,
            "unit": "iter/sec",
            "range": "stddev: 0.018735453331864042",
            "extra": "mean: 1.8153076552000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.394986291439446,
            "unit": "iter/sec",
            "range": "stddev: 0.007699206183961742",
            "extra": "mean: 119.11871744444922 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20079559405369718,
            "unit": "iter/sec",
            "range": "stddev: 0.038049997881075256",
            "extra": "mean: 4.980188956399999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2a1db78ae5b86eb8fe8584889f8ec6787ecee689",
          "message": "ENH: Allow adding PageRange objects (#948)\n\nNow the following is possible:\r\n\r\n    >>> from PyPDF2 import PageRange\r\n    >>> a = PageRange(\"0:5\")\r\n    >>> b = PageRange(\"2:7\")\r\n    >>> a + b\r\n    PageRange(\"0:7\")\r\n\r\nCloses #759\r\nSee #751\r\nSee #752",
          "timestamp": "2022-06-06T13:35:12+02:00",
          "tree_id": "45d682c20c24379d1385d294f56ce01ab8667289",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2a1db78ae5b86eb8fe8584889f8ec6787ecee689"
        },
        "date": 1654515381454,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.623770095271508,
            "unit": "iter/sec",
            "range": "stddev: 0.03076975969767426",
            "extra": "mean: 1.6031547641999908 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.82141339033016,
            "unit": "iter/sec",
            "range": "stddev: 0.005797230659974639",
            "extra": "mean: 101.81833919999406 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23281603278896892,
            "unit": "iter/sec",
            "range": "stddev: 0.04263352708101484",
            "extra": "mean: 4.2952368358 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "babe32e471c6c0d6ee8dd356432dded225fe69a9",
          "message": "TST: Text extraction for non-latin alphabets (#954)\n\nSee #591",
          "timestamp": "2022-06-06T14:51:33+02:00",
          "tree_id": "609d42cbf4f8f9143f4885c0a83ee8ed7625ab18",
          "url": "https://github.com/py-pdf/PyPDF2/commit/babe32e471c6c0d6ee8dd356432dded225fe69a9"
        },
        "date": 1654519972831,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.49568854269348966,
            "unit": "iter/sec",
            "range": "stddev: 0.089218674142686",
            "extra": "mean: 2.0173958319999996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.256144088956997,
            "unit": "iter/sec",
            "range": "stddev: 0.007661703360511162",
            "extra": "mean: 121.12191711110636 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20322879884227077,
            "unit": "iter/sec",
            "range": "stddev: 0.017251143786564296",
            "extra": "mean: 4.920562468000003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "4e44122147de99d78b6fef0066b3dcfffc3faa69",
          "message": "REL: 2.1.0\n\nThe highlight of the 2.1.0 release is the most massive improvement to the\ntext extraction capabilities of PyPDF2 since 2016 🥳🎊 A very big thank you goes\nto [pubpub-zz](https://github.com/pubpub-zz) who took a lot of time and\nknowledge about the PDF format to finally get those improvements into PyPDF2.\nThank you 🤗💚\n\nIn case the new function causes any issues, you can use `_extract_text_old`\nfor the old functionality. Please also open a bug ticket in that case.\n\nThere were several people who have attempted to bring similar improvements to\nPyPDF2. All of those were valuable. The main reason why they didn't get merged\nis the big amount of open PRs / issues. pubpub-zz was the most comprehensive\nPR which also incorporated the latest changes of PyPDF2 2.0.0.\n\nThank you to [VictorCarlquist](https://github.com/VictorCarlquist) for #858 and\n[asabramo](https://github.com/asabramo) for #464 🤗\n\nNew Features (ENH):\n-  Massive text extraction improvement (#924). Closed many open issues:\n    - Exceptions / missing spaces in extract_text() method (#17) 🕺\n      - Whitespace issues in extract_text() (#42) 💃\n      - pypdf2 reads the hifenated words in a new line (#246)\n    - PyPDF2 failing to read unicode character (#37)\n      - Unable to read bullets (#230)\n    - ExtractText yields nothing for apparently good PDF (#168) 🎉\n    - Encoding issue in extract_text() (#235)\n    - extractText() doesn't work on Chinese PDF (#252)\n    - encoding error (#260)\n    - Trouble with apostophes in names in text \"O'Doul\" (#384)\n    - extract_text works for some PDF files, but not the others (#437)\n    - Euro sign not being recognized by extractText (#443)\n    - Failed extracting text from French texts (#524)\n    - extract_text doesn't extract ligatures correctly (#598)\n    - reading spanish text - mark convert issue (#635)\n    - Read PDF changed from text to random symbols (#654)\n    - .extractText() reads / as 1. (#789)\n-  Update glyphlist (#947) - inspired by #464\n-  Allow adding PageRange objects (#948)\n\nBug Fixes (BUG):\n-  Delete .python-version file (#944)\n-  Compare StreamObject.decoded_self with None (#931)\n\nRobustness (ROB):\n-  Fix some conversion errors on non conform PDF (#932)\n\nDocumentation (DOC):\n-  Elaborate on PDF text extraction difficulties (#939)\n-  Add logo (#942)\n-  rotate vs Transformation().rotate (#937)\n-  Example how to use PyPDF2 with AWS S3 (#938)\n-  How to deprecate (#930)\n-  Fix typos on robustness page (#935)\n-  Remove scripts (pdfcat) from docs (#934)\n\nDeveloper Experience (DEV):\n-  Ignore .python-version file\n-  Mark deprecated code with no-cover (#943)\n-  Automatically create Github releases from tags (#870)\n\nTesting (TST):\n-  Text extraction for non-latin alphabets (#954)\n-  Ignore PdfReadWarning in benchmark (#949)\n-  writer.remove_text (#946)\n-  Add test for Tree and _security (#945)\n\nCode Style (STY):\n-  black, isort, Flake8, splitting buildCharMap (#950)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.0.0...2.1.0",
          "timestamp": "2022-06-06T16:02:41+02:00",
          "tree_id": "6ace3082e4abbce97eda06763be8090be2d65b85",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4e44122147de99d78b6fef0066b3dcfffc3faa69"
        },
        "date": 1654524262165,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6181497606295285,
            "unit": "iter/sec",
            "range": "stddev: 0.007768613450684952",
            "extra": "mean: 1.6177309508000008 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.69034555059045,
            "unit": "iter/sec",
            "range": "stddev: 0.006457488101796432",
            "extra": "mean: 103.19549439999776 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23001084468103136,
            "unit": "iter/sec",
            "range": "stddev: 0.0310197694492913",
            "extra": "mean: 4.3476210931999955 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "67752638+Kreusada@users.noreply.github.com",
            "name": "Kreusada",
            "username": "Kreusada"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9118f030b08a6509163cefc39859f582690bbf92",
          "message": "DOC: intendet ➔ in robustness page  (#958)",
          "timestamp": "2022-06-07T17:10:11+02:00",
          "tree_id": "83373274a3ac68acccfd09c0c7afc221d20f934f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9118f030b08a6509163cefc39859f582690bbf92"
        },
        "date": 1654614689505,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6193629665163818,
            "unit": "iter/sec",
            "range": "stddev: 0.007193108691724643",
            "extra": "mean: 1.6145621454000036 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.604414019645382,
            "unit": "iter/sec",
            "range": "stddev: 0.0065182676808168616",
            "extra": "mean: 104.1187935000039 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22729789216625307,
            "unit": "iter/sec",
            "range": "stddev: 0.01383069473636423",
            "extra": "mean: 4.399512861599999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "23a804228852c25433d888c9ac2caf84da8f7194",
          "message": "TST: utils.paeth_predictor (#959)",
          "timestamp": "2022-06-07T21:49:50+02:00",
          "tree_id": "e0e82f34dbbe32ad85f3ce1545ade699743e1440",
          "url": "https://github.com/py-pdf/PyPDF2/commit/23a804228852c25433d888c9ac2caf84da8f7194"
        },
        "date": 1654631476215,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5276321300551012,
            "unit": "iter/sec",
            "range": "stddev: 0.007357273176118776",
            "extra": "mean: 1.8952598658000013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.168192167009012,
            "unit": "iter/sec",
            "range": "stddev: 0.008468613714797638",
            "extra": "mean: 122.42611088888901 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19662842795036695,
            "unit": "iter/sec",
            "range": "stddev: 0.015093834337135657",
            "extra": "mean: 5.085734603200004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "arthurpinheiro@protonmail.com",
            "name": "Arthur Pinheiro",
            "username": "xilopaint"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a7dc37078012f7a4497d8e5fb3e34da647790c9e",
          "message": "MAINT: Export `PageObject` in PyPDF2 root (#960)",
          "timestamp": "2022-06-08T09:17:16+02:00",
          "tree_id": "92b7ee150fca37dc0a7c9a050c85d7cdef57a2bd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a7dc37078012f7a4497d8e5fb3e34da647790c9e"
        },
        "date": 1654672712408,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6198548129171315,
            "unit": "iter/sec",
            "range": "stddev: 0.011011595563993757",
            "extra": "mean: 1.6132810122000136 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.440413165648424,
            "unit": "iter/sec",
            "range": "stddev: 0.007549789559017618",
            "extra": "mean: 105.92756720000125 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22558743237983822,
            "unit": "iter/sec",
            "range": "stddev: 0.011945410740478533",
            "extra": "mean: 4.432871057800003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d1d15f4a151280c9ba07997e4323a5e79d88ed74",
          "message": "TST: Xmp module (#962)",
          "timestamp": "2022-06-09T13:43:34+02:00",
          "tree_id": "ef9bd6101dbdf5216d9c5e5d0da0cbc1ba96fa32",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d1d15f4a151280c9ba07997e4323a5e79d88ed74"
        },
        "date": 1654775086296,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6240095754339279,
            "unit": "iter/sec",
            "range": "stddev: 0.004968888497922611",
            "extra": "mean: 1.6025395111999898 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.566491235330604,
            "unit": "iter/sec",
            "range": "stddev: 0.005551767604682683",
            "extra": "mean: 104.53153359999305 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2294212912967986,
            "unit": "iter/sec",
            "range": "stddev: 0.013233585817421805",
            "extra": "mean: 4.358793354999977 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "53f0b53600ad50ed4b9fbb2a80b0871d0ec3061e",
          "message": "TST: FlateDecode.decode decodeParms (#964)",
          "timestamp": "2022-06-09T14:38:49+02:00",
          "tree_id": "6f586f1cc04fc2dfdef42f6f9f40c303ae352fde",
          "url": "https://github.com/py-pdf/PyPDF2/commit/53f0b53600ad50ed4b9fbb2a80b0871d0ec3061e"
        },
        "date": 1654778419393,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5234546607936486,
            "unit": "iter/sec",
            "range": "stddev: 0.04073406190635866",
            "extra": "mean: 1.910385129600003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.166259065028576,
            "unit": "iter/sec",
            "range": "stddev: 0.0037960465588685152",
            "extra": "mean: 122.45509137500044 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19860924069076719,
            "unit": "iter/sec",
            "range": "stddev: 0.3208149029710302",
            "extra": "mean: 5.035012452200002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "332fa5e33fe1839a6ad486dc34722d0eb800a665",
          "message": "DOC: Who uses PyPDF2",
          "timestamp": "2022-06-09T18:38:51+02:00",
          "tree_id": "98902a5f8687c88f25fb3eaed0321587e22a572c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/332fa5e33fe1839a6ad486dc34722d0eb800a665"
        },
        "date": 1654792811820,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6198716468973078,
            "unit": "iter/sec",
            "range": "stddev: 0.03275851996744488",
            "extra": "mean: 1.6132371999999975 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.669383351795206,
            "unit": "iter/sec",
            "range": "stddev: 0.008297877495056515",
            "extra": "mean: 103.41921129999889 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23082985936818792,
            "unit": "iter/sec",
            "range": "stddev: 0.03354404010116556",
            "extra": "mean: 4.332195161999982 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ztravis@everlaw.com",
            "name": "ztravis",
            "username": "ztravis"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8cd0cfe17c34c0fea89a94a92af7f061e67831ec",
          "message": "PI: Optimize read_next_end_line (#646)\n\nread_next_end_line is inefficient when handling long lines. If the stream is a buffered binary stream, each one-byte \"backwards\" read may trigger a full buffer read, and (more significantly) iteratively building the line we want to return is quadratic in its total length.",
          "timestamp": "2022-06-09T18:42:21+02:00",
          "tree_id": "7727a0f290483a6d2ef04ab30feac21033352a98",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8cd0cfe17c34c0fea89a94a92af7f061e67831ec"
        },
        "date": 1654793019286,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6194154725118173,
            "unit": "iter/sec",
            "range": "stddev: 0.014989446332443758",
            "extra": "mean: 1.614425283799997 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.668532379833614,
            "unit": "iter/sec",
            "range": "stddev: 0.0061301398414162905",
            "extra": "mean: 103.42831369999601 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22947172717244738,
            "unit": "iter/sec",
            "range": "stddev: 0.016271576127717003",
            "extra": "mean: 4.357835330399996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "336d659c41dca4bce9554f70a8586fb1450dd676",
          "message": "MAINT: Mark read_next_end_line as deprecated (#965)\n\nread_next_end_line was removed with #646, but we need to keep it in order to keep backwards compatibility.",
          "timestamp": "2022-06-09T18:59:06+02:00",
          "tree_id": "ddf76cec034e973d222854955b9b553e9f20e1e8",
          "url": "https://github.com/py-pdf/PyPDF2/commit/336d659c41dca4bce9554f70a8586fb1450dd676"
        },
        "date": 1654794041613,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.4524194119713282,
            "unit": "iter/sec",
            "range": "stddev: 0.038223830538036276",
            "extra": "mean: 2.210338401799997 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.073713669639708,
            "unit": "iter/sec",
            "range": "stddev: 0.004917896143729355",
            "extra": "mean: 141.36845887500192 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1653321660277516,
            "unit": "iter/sec",
            "range": "stddev: 0.07303145213725788",
            "extra": "mean: 6.048429800600002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "df8f12127aad2c2faa97615e6cd8a766b0ca5ed3",
          "message": "BUG: Adobe Acrobat 'Would you like to save this file?' (#970)\n\nIssue: When creating files with the current PpdfWriter,\r\nAdobe Acrobat asks 'would you like to save this file'\r\nwhen attempting to close it - although no changes were made.\r\n\r\nFix: Remove 'self.set_need_appearances_writer()' from writers\r\n     __init__ function\r\n\r\nCaused-by: #412 (see #355)\r\n\r\nCloses #963\r\n\r\nCo-authored-by: pubpub-zz <4083478+pubpub-zz@users.noreply.github.com>",
          "timestamp": "2022-06-11T14:22:23+02:00",
          "tree_id": "c3a635eb956934db6640f73eb850107a448a10a4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/df8f12127aad2c2faa97615e6cd8a766b0ca5ed3"
        },
        "date": 1654950234256,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5038315236623337,
            "unit": "iter/sec",
            "range": "stddev: 0.041521767402438944",
            "extra": "mean: 1.9847904567999932 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.885847520487757,
            "unit": "iter/sec",
            "range": "stddev: 0.008526223833783113",
            "extra": "mean: 126.80945166666724 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.18588710921600757,
            "unit": "iter/sec",
            "range": "stddev: 0.10872839660462243",
            "extra": "mean: 5.379609184399999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "55f7c7b35be4431336a8c5a769a7c261445bd47a",
          "message": "STY: Use more tuples and list/dict comprehensions (#976)",
          "timestamp": "2022-06-12T10:18:09+02:00",
          "tree_id": "9c98a716e6f8b603596bf4c4a6c4ecbd8b7e84c6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/55f7c7b35be4431336a8c5a769a7c261445bd47a"
        },
        "date": 1655021956495,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6189742283226757,
            "unit": "iter/sec",
            "range": "stddev: 0.023772070550596727",
            "extra": "mean: 1.6155761487999996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.724294582848039,
            "unit": "iter/sec",
            "range": "stddev: 0.006230052060353172",
            "extra": "mean: 102.83522279999886 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22954015042013579,
            "unit": "iter/sec",
            "range": "stddev: 0.02353284467230491",
            "extra": "mean: 4.356536310400003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "084745fc51f105f01282c879ed6a18b5b15acbc5",
          "message": "MAINT: pre-commit / requirements.txt updates (#977)",
          "timestamp": "2022-06-12T10:29:47+02:00",
          "tree_id": "cb9b0478116dff8694c7780fdcbdcf7b7225e952",
          "url": "https://github.com/py-pdf/PyPDF2/commit/084745fc51f105f01282c879ed6a18b5b15acbc5"
        },
        "date": 1655022670527,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5237816626107991,
            "unit": "iter/sec",
            "range": "stddev: 0.03442460914405988",
            "extra": "mean: 1.9091924582000104 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.197066310542784,
            "unit": "iter/sec",
            "range": "stddev: 0.003931856254474283",
            "extra": "mean: 121.99486525000225 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1962941927454944,
            "unit": "iter/sec",
            "range": "stddev: 0.06653331623091029",
            "extra": "mean: 5.094394215199998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8149026b0b7e2dbb328aff78fd674bbdc7bbc3b8",
          "message": "ENH: Add support for pathlib as input for PdfReader (#979)",
          "timestamp": "2022-06-12T13:11:39+02:00",
          "tree_id": "f79b8da3c643d507de3019a8adf00d96469d0326",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8149026b0b7e2dbb328aff78fd674bbdc7bbc3b8"
        },
        "date": 1655032366942,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6110192931400946,
            "unit": "iter/sec",
            "range": "stddev: 0.04168416050200808",
            "extra": "mean: 1.6366095329999992 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.710170067025734,
            "unit": "iter/sec",
            "range": "stddev: 0.005735377217202816",
            "extra": "mean: 102.98480800000078 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22997617713071353,
            "unit": "iter/sec",
            "range": "stddev: 0.03183254689992185",
            "extra": "mean: 4.348276471399998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "41eff2a059ee4f4a9cbca931a110e65a3521bcd7",
          "message": "TST: Add MCVE of issue #416 (#980)",
          "timestamp": "2022-06-12T14:02:45+02:00",
          "tree_id": "3db10df8806ed790252cb1f7b3f772052fbdc2e6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/41eff2a059ee4f4a9cbca931a110e65a3521bcd7"
        },
        "date": 1655035435839,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.613796619204195,
            "unit": "iter/sec",
            "range": "stddev: 0.006552381860389591",
            "extra": "mean: 1.6292041511999997 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.700777998999898,
            "unit": "iter/sec",
            "range": "stddev: 0.006139808950785802",
            "extra": "mean: 103.0845155000037 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2309424686771713,
            "unit": "iter/sec",
            "range": "stddev: 0.020098646633538508",
            "extra": "mean: 4.330082750599999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "363372c11005a0ff1dd72b4ff66b5097987d3df6",
          "message": "DOC: Notes on annotations (#982)",
          "timestamp": "2022-06-12T18:04:43+02:00",
          "tree_id": "3d3f6c85c201ea7180363072f5c37f42614f7582",
          "url": "https://github.com/py-pdf/PyPDF2/commit/363372c11005a0ff1dd72b4ff66b5097987d3df6"
        },
        "date": 1655049950138,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6174311176109448,
            "unit": "iter/sec",
            "range": "stddev: 0.007159148538809019",
            "extra": "mean: 1.6196138670000095 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.604462983418456,
            "unit": "iter/sec",
            "range": "stddev: 0.007357280418185147",
            "extra": "mean: 104.1182627000012 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22802086837483473,
            "unit": "iter/sec",
            "range": "stddev: 0.023510727573323512",
            "extra": "mean: 4.385563510599996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "a15cf67173a81523ff3e9eab3ac5ee98429841c2",
          "message": "DEV: Add PI to make_changelog",
          "timestamp": "2022-06-12T18:08:30+02:00",
          "tree_id": "71024cf6f9d03685b1100036aa82c3d505899fee",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a15cf67173a81523ff3e9eab3ac5ee98429841c2"
        },
        "date": 1655050182527,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6253421216261991,
            "unit": "iter/sec",
            "range": "stddev: 0.004406285625831991",
            "extra": "mean: 1.5991246477999994 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.711909170153897,
            "unit": "iter/sec",
            "range": "stddev: 0.007377327677019517",
            "extra": "mean: 102.96636660000331 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2328687867780546,
            "unit": "iter/sec",
            "range": "stddev: 0.027809929745674297",
            "extra": "mean: 4.294263794799997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "9c4e7f52fb3c53ed6391d4a96e227116a9473acf",
          "message": "REL: 2.1.1\n\nNew Features (ENH):\n-  Add support for pathlib as input for PdfReader (#979)\n\nPerformance Improvements (PI):\n-  Optimize read_next_end_line (#646)\n\nBug Fixes (BUG):\n-  Adobe Acrobat \\'Would you like to save this file?\\' (#970)\n\nDocumentation (DOC):\n-  Notes on annotations (#982)\n-  Who uses PyPDF2\n-  intendet \\xe2\\x9e\\x94 in robustness page  (#958)\n\nMaintenance (MAINT):\n-  pre-commit / requirements.txt updates (#977)\n-  Mark read_next_end_line as deprecated (#965)\n-  Export `PageObject` in PyPDF2 root (#960)\n\nTesting (TST):\n-  Add MCVE of issue #416 (#980)\n-  FlateDecode.decode decodeParms (#964)\n-  Xmp module (#962)\n-  utils.paeth_predictor (#959)\n\nCode Style (STY):\n-  Use more tuples and list/dict comprehensions (#976)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.1.0...2.1.1",
          "timestamp": "2022-06-12T18:09:37+02:00",
          "tree_id": "b1cd9b621e479f36784f0489bef278e14fe72e65",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9c4e7f52fb3c53ed6391d4a96e227116a9473acf"
        },
        "date": 1655050296219,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.45877601283803277,
            "unit": "iter/sec",
            "range": "stddev: 0.023922487203348976",
            "extra": "mean: 2.1797129143999996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.028330257471669,
            "unit": "iter/sec",
            "range": "stddev: 0.009814533112778199",
            "extra": "mean: 142.28130485714172 msec\nrounds: 7"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.17337457224514943,
            "unit": "iter/sec",
            "range": "stddev: 0.08641363254316417",
            "extra": "mean: 5.767858498800001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "72fcaae50e9676ca16346a556c29b688ae2714f8",
          "message": "ENH: Text Extraction improvements (#969)\n\n* Improvements around /Encoding / /ToUnicode\r\n* Extraction of CMaps improved\r\n* Fallback for font def missing\r\n* Support for /Identity-H and /Identity-V: utf-16-be\r\n* Support for /GB-EUC-H / /GB-EUC-V / GBp/c-EUC-H / /GBpc-EUC-V (beta release for evaluation)\r\n* Arabic (for evaluation)\r\n* Whitespace extraction improvements",
          "timestamp": "2022-06-13T21:40:43+02:00",
          "tree_id": "a353ad6f36239580ee0c9f3bbbc6f4f170b08281",
          "url": "https://github.com/py-pdf/PyPDF2/commit/72fcaae50e9676ca16346a556c29b688ae2714f8"
        },
        "date": 1655149314974,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6238667778931499,
            "unit": "iter/sec",
            "range": "stddev: 0.011959801989632098",
            "extra": "mean: 1.6029063181999903 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.613936257398946,
            "unit": "iter/sec",
            "range": "stddev: 0.006410231173057463",
            "extra": "mean: 104.01566780000167 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21691445127493675,
            "unit": "iter/sec",
            "range": "stddev: 0.028356942333540334",
            "extra": "mean: 4.61011239280001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "f0cd8292da2dfe020d4042e16b42b24aa2378dd3",
          "message": "REL: 2.2.0\n\nThe 2.2.0 release improves text extraction again via (#969):\n\n* Improvements around /Encoding / /ToUnicode\n* Extraction of CMaps improved\n* Fallback for font def missing\n* Support for /Identity-H and /Identity-V: utf-16-be\n* Support for /GB-EUC-H / /GB-EUC-V / GBp/c-EUC-H / /GBpc-EUC-V (beta release for evaluation)\n* Arabic (for evaluation)\n* Whitespace extraction improvements\n\nThose changes should mainly improve the text extraction for non-ASCII alphabets,\ne.g. Russian / Chinese / Japanese / Korean / Arabic.\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.1.1...2.2.0",
          "timestamp": "2022-06-13T21:45:28+02:00",
          "tree_id": "5c2ecbe33b1f967cc9fd0c7d01894c2e08c64521",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f0cd8292da2dfe020d4042e16b42b24aa2378dd3"
        },
        "date": 1655149647565,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.44268114584711626,
            "unit": "iter/sec",
            "range": "stddev: 0.06830016061664344",
            "extra": "mean: 2.258962256199993 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.9581196314600025,
            "unit": "iter/sec",
            "range": "stddev: 0.0033557399783245927",
            "extra": "mean: 125.6578244999993 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1787840061963882,
            "unit": "iter/sec",
            "range": "stddev: 0.08493061521811243",
            "extra": "mean: 5.5933414921999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8441da42d49551c7fc178b31d516998acff84e83",
          "message": "PI: Remove b_ calls (#986)\n\nFunction calls are cheap, but not for free in Python.\r\nThe b_ function converts a string to a bytes object. When we have\r\na constant string, we can use the constant byte representation\r\ninstead (a b\"byte literal\" instead of b_(\"string literal\"))",
          "timestamp": "2022-06-14T12:35:43+02:00",
          "tree_id": "f419c1304655e296396236af7c130625698b5a63",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8441da42d49551c7fc178b31d516998acff84e83"
        },
        "date": 1655203013478,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6658896852734139,
            "unit": "iter/sec",
            "range": "stddev: 0.007111535799373589",
            "extra": "mean: 1.5017502480000133 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.900811715078332,
            "unit": "iter/sec",
            "range": "stddev: 0.00794771558373348",
            "extra": "mean: 101.00181972727155 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25487888165050904,
            "unit": "iter/sec",
            "range": "stddev: 0.0327202634295768",
            "extra": "mean: 3.9234321554000076 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "712c16dd73e1ecacf5afed1da58b5eb2ccffd000",
          "message": "DOC: Remove reference to Scripts (#987)\n\nCloses #985",
          "timestamp": "2022-06-14T12:38:08+02:00",
          "tree_id": "ab2d9d5e49b5a85b7804ae4ffd8679b5f0bfc252",
          "url": "https://github.com/py-pdf/PyPDF2/commit/712c16dd73e1ecacf5afed1da58b5eb2ccffd000"
        },
        "date": 1655203167338,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.5704879013606602,
            "unit": "iter/sec",
            "range": "stddev: 0.00795389861735368",
            "extra": "mean: 1.7528855522 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.483493965070943,
            "unit": "iter/sec",
            "range": "stddev: 0.007423711667371854",
            "extra": "mean: 117.875960555556 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21677975953201117,
            "unit": "iter/sec",
            "range": "stddev: 0.019266400243769487",
            "extra": "mean: 4.6129767934 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8f5201e2bee7e97bc04f2844c4dd0a5368c7be18",
          "message": "PI: Remove b_ calls (#992)\n\nSee also: #986\r\n\r\nAlso: Minor type improvement",
          "timestamp": "2022-06-14T20:27:34+02:00",
          "tree_id": "950a6e8a842d13148d2424f143d2ff83659d578a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8f5201e2bee7e97bc04f2844c4dd0a5368c7be18"
        },
        "date": 1655231316962,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9760165754224598,
            "unit": "iter/sec",
            "range": "stddev: 0.010061101088401546",
            "extra": "mean: 1.0245727636000026 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.413183831392226,
            "unit": "iter/sec",
            "range": "stddev: 0.0066149778496518786",
            "extra": "mean: 96.03210854545162 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26110126839922587,
            "unit": "iter/sec",
            "range": "stddev: 0.024672083069376866",
            "extra": "mean: 3.829931605199988 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e47e057e9289a5a33b352a49f5b9b3a2af8742e0",
          "message": "PI: Apply improvements to _utils suggested by perflint (#993)",
          "timestamp": "2022-06-14T20:43:17+02:00",
          "tree_id": "474f8d066f26a03ead9e5dac2be1918e59fc0c1e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e47e057e9289a5a33b352a49f5b9b3a2af8742e0"
        },
        "date": 1655232258106,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9694032220491575,
            "unit": "iter/sec",
            "range": "stddev: 0.005380675920287689",
            "extra": "mean: 1.031562488399993 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.369503259240815,
            "unit": "iter/sec",
            "range": "stddev: 0.006866208781360404",
            "extra": "mean: 96.43663490908754 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2636198923582518,
            "unit": "iter/sec",
            "range": "stddev: 0.014565427472591501",
            "extra": "mean: 3.793340445800004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e292822ad9e481ef17384e69769dc7b4d1681870",
          "message": "TST: Add tests for XMP information (#996)",
          "timestamp": "2022-06-15T07:50:21+02:00",
          "tree_id": "f257cfef83c723a12341e9aa9c0491fbb84afb05",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e292822ad9e481ef17384e69769dc7b4d1681870"
        },
        "date": 1655272301383,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7251356543029497,
            "unit": "iter/sec",
            "range": "stddev: 0.009204115854784626",
            "extra": "mean: 1.3790523111999904 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.924500337372118,
            "unit": "iter/sec",
            "range": "stddev: 0.002387837390621819",
            "extra": "mean: 126.19092149999389 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19789114145969272,
            "unit": "iter/sec",
            "range": "stddev: 0.10390335577635496",
            "extra": "mean: 5.0532832982000055 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "034d7a9aaf48432fad0970edd5a59841702203f5",
          "message": "ROB : utf-16-be' codec can't decode (...) (#995)\n\nCloses #988",
          "timestamp": "2022-06-15T20:36:51+02:00",
          "tree_id": "a1bd85177086f2f1918ac2abc606dcffd0268436",
          "url": "https://github.com/py-pdf/PyPDF2/commit/034d7a9aaf48432fad0970edd5a59841702203f5"
        },
        "date": 1655318273539,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.974164880828896,
            "unit": "iter/sec",
            "range": "stddev: 0.005609308836243069",
            "extra": "mean: 1.0265202736000105 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.332738508888722,
            "unit": "iter/sec",
            "range": "stddev: 0.00511675707445432",
            "extra": "mean: 96.7797645454544 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26722496095069176,
            "unit": "iter/sec",
            "range": "stddev: 0.02259375460058008",
            "extra": "mean: 3.7421653891999993 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6ce36f7ab6a66a7fce83e7c101dd5167e45e5613",
          "message": "TST: Improve test coverage by extracting texts (#998)",
          "timestamp": "2022-06-16T10:55:15+02:00",
          "tree_id": "edccd54346f15bca621a89051ea7d7b13fd784f3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6ce36f7ab6a66a7fce83e7c101dd5167e45e5613"
        },
        "date": 1655369790897,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9506659352798031,
            "unit": "iter/sec",
            "range": "stddev: 0.0094299572614412",
            "extra": "mean: 1.051894217400013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.162170437914352,
            "unit": "iter/sec",
            "range": "stddev: 0.007548943347155935",
            "extra": "mean: 98.40417518181641 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2574983527266455,
            "unit": "iter/sec",
            "range": "stddev: 0.01548085819896498",
            "extra": "mean: 3.883519989199999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "faebc9da1567af676edf69803e31fc61396fab93",
          "message": "STY: Apply fixes suggested by pylint (#999)\n\n* Use f-strings: They are IMHO more readable and faster than other formatting options\r\n* Reduce code duplication\r\n* Improvements in type annotations\r\n* Add PyPDF2 module docstring for help text",
          "timestamp": "2022-06-16T13:58:14+02:00",
          "tree_id": "10dffcda58da3e06f463d7327f5c9988c420a7e6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/faebc9da1567af676edf69803e31fc61396fab93"
        },
        "date": 1655380770482,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8225766710837669,
            "unit": "iter/sec",
            "range": "stddev: 0.008314234669688064",
            "extra": "mean: 1.2156921478000016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.812169592107175,
            "unit": "iter/sec",
            "range": "stddev: 0.00768160558077237",
            "extra": "mean: 113.4794320000007 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22474109524674507,
            "unit": "iter/sec",
            "range": "stddev: 0.018917795994089735",
            "extra": "mean: 4.449564504 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1ccf4849f0933b34d6f1e1d8f1c360e7620bba42",
          "message": "DEV: Fix type annotations for add_bookmarks (#1000)",
          "timestamp": "2022-06-16T16:55:17+02:00",
          "tree_id": "57a68406792715c6d95a73f24a7a663c832addc2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1ccf4849f0933b34d6f1e1d8f1c360e7620bba42"
        },
        "date": 1655391404326,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6890046159660322,
            "unit": "iter/sec",
            "range": "stddev: 0.024292111102718283",
            "extra": "mean: 1.4513690863999955 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 7.424477118994786,
            "unit": "iter/sec",
            "range": "stddev: 0.006788092505252368",
            "extra": "mean: 134.68961975000227 msec\nrounds: 8"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19152049000576207,
            "unit": "iter/sec",
            "range": "stddev: 0.08468760655479031",
            "extra": "mean: 5.221373441399999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bb93367f95c9db76bb759e1b0a9d24aa1c10bf90",
          "message": "TST: Add test for PdfMerger (#1001)\n\nBUG: Add file handles of reader early to list so that it can be closed in case of a catched exception",
          "timestamp": "2022-06-16T21:24:03+02:00",
          "tree_id": "48d61e2d8066750770e75cef9ce815f76f1c3b80",
          "url": "https://github.com/py-pdf/PyPDF2/commit/bb93367f95c9db76bb759e1b0a9d24aa1c10bf90"
        },
        "date": 1655407515579,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8185114761045884,
            "unit": "iter/sec",
            "range": "stddev: 0.050185769451911395",
            "extra": "mean: 1.2217299686000018 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.683329721111537,
            "unit": "iter/sec",
            "range": "stddev: 0.010115184473849527",
            "extra": "mean: 115.16319570000064 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22963236061463574,
            "unit": "iter/sec",
            "range": "stddev: 0.10751637486912834",
            "extra": "mean: 4.354786918199997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a6b66b16f605cece73b45fc488ef9d2d75662446",
          "message": "TST: reader.get_fields (#1002)",
          "timestamp": "2022-06-16T22:57:57+02:00",
          "tree_id": "51f5c6cc7f622ab1c424ed7b1a4f24026f8b175e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a6b66b16f605cece73b45fc488ef9d2d75662446"
        },
        "date": 1655413166154,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8219682347317961,
            "unit": "iter/sec",
            "range": "stddev: 0.008099461504109633",
            "extra": "mean: 1.2165920260000007 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.787756634215107,
            "unit": "iter/sec",
            "range": "stddev: 0.008467119136413336",
            "extra": "mean: 113.79468522222187 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22454820015276128,
            "unit": "iter/sec",
            "range": "stddev: 0.015089571938094447",
            "extra": "mean: 4.453386842200004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bf8ad456e534b46583ebbfed41b10b4889bf95fa",
          "message": "TST: reader.get_fields / zlib issue / LZW decode issue (#1004)",
          "timestamp": "2022-06-17T09:55:18+02:00",
          "tree_id": "fb03fc63d732053e2c3dc1e222e22ee99ed77711",
          "url": "https://github.com/py-pdf/PyPDF2/commit/bf8ad456e534b46583ebbfed41b10b4889bf95fa"
        },
        "date": 1655452580964,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9631382068728982,
            "unit": "iter/sec",
            "range": "stddev: 0.006535924326639555",
            "extra": "mean: 1.038272589400003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.402483589552036,
            "unit": "iter/sec",
            "range": "stddev: 0.006205210737651507",
            "extra": "mean: 96.13088945455027 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2652156873560553,
            "unit": "iter/sec",
            "range": "stddev: 0.028587863919452786",
            "extra": "mean: 3.7705160277999994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "91b3e8a89487fe64dad73beff2b2c96e88f8c83d",
          "message": "REL: 2.2.1\n\nPerformance Improvements (PI):\n-  Remove b_ calls (#992, #986)\n-  Apply improvements to _utils suggested by perflint (#993)\n\nRobustness (ROB):\n-  utf-16-be\\' codec can\\'t decode (...) (#995)\n\nDocumentation (DOC):\n-  Remove reference to Scripts (#987)\n\nDeveloper Experience (DEV):\n-  Fix type annotations for add_bookmarks (#1000)\n\nTesting (TST):\n-  Add test for PdfMerger (#1001)\n-  Add tests for XMP information (#996)\n-  reader.get_fields / zlib issue / LZW decode issue (#1004)\n-  reader.get_fields with report generation (#1002)\n-  Improve test coverage by extracting texts (#998)\n\nCode Style (STY):\n-  Apply fixes suggested by pylint (#999)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.2.0...2.2.1",
          "timestamp": "2022-06-17T13:20:49+02:00",
          "tree_id": "9f5f5771693eab9c87db2228453913eecf6b746a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/91b3e8a89487fe64dad73beff2b2c96e88f8c83d"
        },
        "date": 1655464938519,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.831175827657207,
            "unit": "iter/sec",
            "range": "stddev: 0.03477858025420831",
            "extra": "mean: 1.2031148725999998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.201466145421007,
            "unit": "iter/sec",
            "range": "stddev: 0.006466518673642589",
            "extra": "mean: 108.67833280000028 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23204174436104527,
            "unit": "iter/sec",
            "range": "stddev: 0.04918283833400809",
            "extra": "mean: 4.309569395600002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "c540896a349587addfd172344db3b504569f0545",
          "message": "TST: Add mutmut config",
          "timestamp": "2022-06-17T17:58:49+02:00",
          "tree_id": "667df526ce6a90b9599578e9b80f1ea56f75db3c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c540896a349587addfd172344db3b504569f0545"
        },
        "date": 1655481609790,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8549551538771368,
            "unit": "iter/sec",
            "range": "stddev: 0.010425898139371509",
            "extra": "mean: 1.1696519934000036 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.199865362914256,
            "unit": "iter/sec",
            "range": "stddev: 0.007744396943551764",
            "extra": "mean: 108.69724290000136 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23480566119798402,
            "unit": "iter/sec",
            "range": "stddev: 0.029709252514727873",
            "extra": "mean: 4.258841098200003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kianmeng.ang@gmail.com",
            "name": "Kian-Meng Ang",
            "username": "kianmeng"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d3fe4b7776a1085a0e2c3263480d501fa484517d",
          "message": "DOC: Fix typos (#1007)",
          "timestamp": "2022-06-18T19:01:54+02:00",
          "tree_id": "e9e6632f14029c5933d01fe98f2ceb5fa0f034fe",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d3fe4b7776a1085a0e2c3263480d501fa484517d"
        },
        "date": 1655571787297,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7938297976079823,
            "unit": "iter/sec",
            "range": "stddev: 0.05971354469710725",
            "extra": "mean: 1.259715877399995 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 8.607093020434936,
            "unit": "iter/sec",
            "range": "stddev: 0.011415289161190147",
            "extra": "mean: 116.1832453333318 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22810199907859355,
            "unit": "iter/sec",
            "range": "stddev: 0.030896372726721553",
            "extra": "mean: 4.384003665199995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c57e59baf3921ac528d00c51c02cb01e4b0f75e3",
          "message": "TST: Add merger test cases with real PDFs (#1006)",
          "timestamp": "2022-06-19T07:36:42+02:00",
          "tree_id": "9c3929e66f167a4cbcf3e9bda9f3e304dd63c1f3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c57e59baf3921ac528d00c51c02cb01e4b0f75e3"
        },
        "date": 1655617060845,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9534467887530279,
            "unit": "iter/sec",
            "range": "stddev: 0.007713019926785629",
            "extra": "mean: 1.0488262290000023 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.420467601298833,
            "unit": "iter/sec",
            "range": "stddev: 0.006744914987543549",
            "extra": "mean: 95.96498336364075 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2676978261719624,
            "unit": "iter/sec",
            "range": "stddev: 0.017121044815713807",
            "extra": "mean: 3.7355551753999863 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6d426a05c941229452dfd9eab8b04b7ae5bc03a0",
          "message": "TST: Improve encryption/decryption test (#1009)",
          "timestamp": "2022-06-19T08:15:19+02:00",
          "tree_id": "fe4f8fe4950f07a92f59a1047ca60a602805bcfb",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6d426a05c941229452dfd9eab8b04b7ae5bc03a0"
        },
        "date": 1655619381366,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9561526997738262,
            "unit": "iter/sec",
            "range": "stddev: 0.011564527342700298",
            "extra": "mean: 1.0458580520000056 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.32561262777248,
            "unit": "iter/sec",
            "range": "stddev: 0.006089213127626411",
            "extra": "mean: 96.84655390909504 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2632872398730326,
            "unit": "iter/sec",
            "range": "stddev: 0.013273875092311831",
            "extra": "mean: 3.798133173799988 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "exiledkingcc@gmail.com",
            "name": "exiledkingcc",
            "username": "exiledkingcc"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "868f977bb93b2b00ffee7cd849a2bc07f33e5c64",
          "message": "ENH: Add decrypt support for V5 and AES-128, AES-256 (R5 only) (#749)\n\nThis is a rewrite of the encryption part to support V4 and AES-128 encryption (ONLY decrypt for now)\r\nPyCryptodome was added as an optional dependency for AES.\r\n\r\nIt does NOT add support for encryption R=6 as introduced by PDF 2.0\r\n\r\nCloses #528",
          "timestamp": "2022-06-19T08:31:18+02:00",
          "tree_id": "ad1134ccf7d062d3cce88f40de34e59d1d793b31",
          "url": "https://github.com/py-pdf/PyPDF2/commit/868f977bb93b2b00ffee7cd849a2bc07f33e5c64"
        },
        "date": 1655620339780,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9826516066225652,
            "unit": "iter/sec",
            "range": "stddev: 0.005781554300131366",
            "extra": "mean: 1.0176546735999978 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.408359061379997,
            "unit": "iter/sec",
            "range": "stddev: 0.005693879034509232",
            "extra": "mean: 69.40415599999785 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26415829090824966,
            "unit": "iter/sec",
            "range": "stddev: 0.008063422854579054",
            "extra": "mean: 3.7856089868000056 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "797963abdf71d3e184a11871ec0e95943ddfbea5",
          "message": "STY: Make encryption module private, apply pre-commit (#1010)\n\nRelated to #749",
          "timestamp": "2022-06-19T08:59:57+02:00",
          "tree_id": "352ff3cf982f0108f6abadeb4cf4247cd6978826",
          "url": "https://github.com/py-pdf/PyPDF2/commit/797963abdf71d3e184a11871ec0e95943ddfbea5"
        },
        "date": 1655622082878,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6798115085216335,
            "unit": "iter/sec",
            "range": "stddev: 0.024750233276590178",
            "extra": "mean: 1.4709959855999954 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.179822294562625,
            "unit": "iter/sec",
            "range": "stddev: 0.008799753894850666",
            "extra": "mean: 98.23354190908938 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19006333827410843,
            "unit": "iter/sec",
            "range": "stddev: 0.10764334450528514",
            "extra": "mean: 5.261403956600009 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "953a11d9bedd49cedff17dd39e3ea5051fb15496",
          "message": "DEP: Rename names to be PEP8-compliant (#967)\n\nAll of the following get in [the deprecation process](https://pypdf2.readthedocs.io/en/latest/dev/deprecations.html). This means the old parameters will work for a while to give users a chance to migrate without service disruptions.\r\n\r\n`PdfWriter.get_page`: the pageNumber parameter is renamed to page_number\r\n\r\n`PyPDF2.filters`:\r\n\r\n* For all classes, a parameter rename: decodeParms ➔ decode_parms\r\n* decodeStreamData ➔ decode_stream_data\r\n\r\n`PyPDF2.xmp`:\r\n\r\n* XmpInformation.rdfRoot ➔ XmpInformation.rdf_root\r\n* XmpInformation.xmp_createDate ➔ XmpInformation.xmp_create_date\r\n* XmpInformation.xmp_creatorTool ➔ XmpInformation.xmp_creator_tool\r\n* XmpInformation.xmp_metadataDate ➔ XmpInformation.xmp_metadata_date\r\n* XmpInformation.xmp_modifyDate ➔ XmpInformation.xmp_modify_date\r\n* XmpInformation.xmpMetadata ➔ XmpInformation.xmp_metadata\r\n* XmpInformation.xmpmm_documentId ➔ XmpInformation.xmpmm_document_id\r\n* XmpInformation.xmpmm_instanceId ➔ XmpInformation.xmpmm_instance_id\r\n\r\n`PyPDF2.generic`:\r\n\r\n* readHexStringFromStream ➔ read_hex_string_from_stream\r\n* initializeFromDictionary ➔ initialize_from_dictionary\r\n* createStringObject ➔ create_string_object\r\n* TreeObject.hasChildren ➔ TreeObject.has_children\r\n* TreeObject.emptyTree ➔ TreeObject.empty_tree",
          "timestamp": "2022-06-19T09:27:53+02:00",
          "tree_id": "ac6039f86dd4d9e34f795a3c93e7872813f086c7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/953a11d9bedd49cedff17dd39e3ea5051fb15496"
        },
        "date": 1655623734050,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9797980134951144,
            "unit": "iter/sec",
            "range": "stddev: 0.007248612437250133",
            "extra": "mean: 1.0206185215999994 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.337240005025006,
            "unit": "iter/sec",
            "range": "stddev: 0.005830414175252306",
            "extra": "mean: 69.7484313333329 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26382525186151445,
            "unit": "iter/sec",
            "range": "stddev: 0.011562182403087784",
            "extra": "mean: 3.790387739399995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f62e05150eab36cf70770d1e0711e29612e9e479",
          "message": "ROB: Fix corrupted (wrongly) linear PDF (#1008)\n\nFix: Rescan the whole PDF and update/rebuild the trailer\r\n\r\nCloses #989",
          "timestamp": "2022-06-19T09:36:59+02:00",
          "tree_id": "9ab5adcc0bdf78ed73427cbee9c8392cac26b436",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f62e05150eab36cf70770d1e0711e29612e9e479"
        },
        "date": 1655624285387,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.969716317570971,
            "unit": "iter/sec",
            "range": "stddev: 0.005946170806177808",
            "extra": "mean: 1.0312294244 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.252918618605316,
            "unit": "iter/sec",
            "range": "stddev: 0.0065794167301786634",
            "extra": "mean: 70.16106853333402 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2622596813196375,
            "unit": "iter/sec",
            "range": "stddev: 0.01710465099960888",
            "extra": "mean: 3.8130146233999938 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2c53813dfac9791f639a2e6517cba1feb2671c32",
          "message": "STY: Put pure data mappings in separate files (#1005)\n\nCreated a private codecs module",
          "timestamp": "2022-06-19T10:11:31+02:00",
          "tree_id": "02d50b8c43a9236acf43d6fd00f51fd0c0d0e892",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2c53813dfac9791f639a2e6517cba1feb2671c32"
        },
        "date": 1655626374428,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6949554600585487,
            "unit": "iter/sec",
            "range": "stddev: 0.04782707844780199",
            "extra": "mean: 1.438941137200004 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.582839220182525,
            "unit": "iter/sec",
            "range": "stddev: 0.011102814924503306",
            "extra": "mean: 104.35320649999937 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20112849738056496,
            "unit": "iter/sec",
            "range": "stddev: 0.09260031943155554",
            "extra": "mean: 4.971945860600011 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "ad6e941c1b188a5dae0cb82fced48165fc886172",
          "message": "MAINT: Move PDF_Samples folder into ressources",
          "timestamp": "2022-06-19T11:33:39+02:00",
          "tree_id": "aaaef17a516d1c4e1d279ac88565f426bd47b4ff",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ad6e941c1b188a5dae0cb82fced48165fc886172"
        },
        "date": 1655631301117,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9766178580191678,
            "unit": "iter/sec",
            "range": "stddev: 0.007025275195116246",
            "extra": "mean: 1.0239419561999994 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.303205771407113,
            "unit": "iter/sec",
            "range": "stddev: 0.006529112077902035",
            "extra": "mean: 69.91439653333202 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2622625659904564,
            "unit": "iter/sec",
            "range": "stddev: 0.015091388255829608",
            "extra": "mean: 3.8129726833999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "d5bc2788a8d37e4b4a508eba37df0889003c37f7",
          "message": "REL: 2.3.0\n\nThe highlight of this release is improved support for file encryption\n(AES-128 and AES-256, R5 only). See #749 for the amazing work of\n@exiledkingcc 🎊 Thank you 🤗\n\nDeprecations (DEP):\n-  Rename names to be PEP8-compliant (#967)\n  - `PdfWriter.get_page`: the pageNumber parameter is renamed to page_number\n  - `PyPDF2.filters`:\n    * For all classes, a parameter rename: decodeParms ➔ decode_parms\n    * decodeStreamData ➔ decode_stream_data\n  - `PyPDF2.xmp`:\n    * XmpInformation.rdfRoot ➔ XmpInformation.rdf_root\n    * XmpInformation.xmp_createDate ➔ XmpInformation.xmp_create_date\n    * XmpInformation.xmp_creatorTool ➔ XmpInformation.xmp_creator_tool\n    * XmpInformation.xmp_metadataDate ➔ XmpInformation.xmp_metadata_date\n    * XmpInformation.xmp_modifyDate ➔ XmpInformation.xmp_modify_date\n    * XmpInformation.xmpMetadata ➔ XmpInformation.xmp_metadata\n    * XmpInformation.xmpmm_documentId ➔ XmpInformation.xmpmm_document_id\n    * XmpInformation.xmpmm_instanceId ➔ XmpInformation.xmpmm_instance_id\n  - `PyPDF2.generic`:\n    * readHexStringFromStream ➔ read_hex_string_from_stream\n    * initializeFromDictionary ➔ initialize_from_dictionary\n    * createStringObject ➔ create_string_object\n    * TreeObject.hasChildren ➔ TreeObject.has_children\n    * TreeObject.emptyTree ➔ TreeObject.empty_tree\n\nNew Features (ENH):\n-  Add decrypt support for V5 and AES-128, AES-256 (R5 only) (#749)\n\nRobustness (ROB):\n-  Fix corrupted (wrongly) linear PDF (#1008)\n\nMaintenance (MAINT):\n-  Move PDF_Samples folder into ressources\n-  Fix typos (#1007)\n\nTesting (TST):\n-  Improve encryption/decryption test (#1009)\n-  Add merger test cases with real PDFs (#1006)\n-  Add mutmut config\n\nCode Style (STY):\n-  Put pure data mappings in separate files (#1005)\n-  Make encryption module private, apply pre-commit (#1010)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.2.1...2.3.0",
          "timestamp": "2022-06-19T12:24:49+02:00",
          "tree_id": "34c0a8d4dd81a5d74b09f7779850b696d44d4ad2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d5bc2788a8d37e4b4a508eba37df0889003c37f7"
        },
        "date": 1655634377504,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.970368542075278,
            "unit": "iter/sec",
            "range": "stddev: 0.01683671611273076",
            "extra": "mean: 1.0305362928000021 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.38871593615071,
            "unit": "iter/sec",
            "range": "stddev: 0.006408496772547005",
            "extra": "mean: 69.49890486666467 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2654517970276444,
            "unit": "iter/sec",
            "range": "stddev: 0.021913973484801574",
            "extra": "mean: 3.7671622916000045 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "6b9f472d10fa1355612f9a8063a3b902a1db077d",
          "message": "REL: 2.3.1\n\nBUG: Add _codecs subpackage to distribution\n\nThank you @nyanpasu64 for reporting it!\n\nCloses #1011\n\nCo-authored-by: nyanpasu64 <nyanpasu64@tuta.io>",
          "timestamp": "2022-06-19T14:50:17+02:00",
          "tree_id": "7796988bdc6783bbceeaffce757e27be0d0d331b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6b9f472d10fa1355612f9a8063a3b902a1db077d"
        },
        "date": 1655643241148,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9884793004422833,
            "unit": "iter/sec",
            "range": "stddev: 0.007503590918017239",
            "extra": "mean: 1.011654973000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.273160212105111,
            "unit": "iter/sec",
            "range": "stddev: 0.0042718063289290936",
            "extra": "mean: 70.0615690666666 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2695782110540451,
            "unit": "iter/sec",
            "range": "stddev: 0.015477909058436072",
            "extra": "mean: 3.709498612999994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "56158e01e32020224d6b22d64016a495f728d991",
          "message": "DEV: Update Bug report template",
          "timestamp": "2022-06-19T17:40:18+02:00",
          "tree_id": "10600173be1c4e9310fa0f640ac6e7b4105a06bf",
          "url": "https://github.com/py-pdf/PyPDF2/commit/56158e01e32020224d6b22d64016a495f728d991"
        },
        "date": 1655653291398,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0691827573997352,
            "unit": "iter/sec",
            "range": "stddev: 0.010670390002485885",
            "extra": "mean: 935.2937962000169 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 16.34173925100038,
            "unit": "iter/sec",
            "range": "stddev: 0.006097956768186264",
            "extra": "mean: 61.19299694117832 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2890268472337094,
            "unit": "iter/sec",
            "range": "stddev: 0.02909568686044038",
            "extra": "mean: 3.459886199399989 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4c9fd44f065b6e27120736ed666d05cdac6b1991",
          "message": "PI: Remove ord_ calls (#1014)",
          "timestamp": "2022-06-19T22:23:27+02:00",
          "tree_id": "935bf716cff37c439c69b509376aa5a49be01eda",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4c9fd44f065b6e27120736ed666d05cdac6b1991"
        },
        "date": 1655670266722,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9990369002553112,
            "unit": "iter/sec",
            "range": "stddev: 0.015945721384096324",
            "extra": "mean: 1.000964028200002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.474246082983356,
            "unit": "iter/sec",
            "range": "stddev: 0.005593586881796989",
            "extra": "mean: 69.0882270666691 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2742561889890145,
            "unit": "iter/sec",
            "range": "stddev: 0.019605854741076324",
            "extra": "mean: 3.6462258288000045 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5834669a98dc2835c3d83ce4ebc531ef572cba27",
          "message": "DOC: Mention crypto extra_requires for installation (#1017)",
          "timestamp": "2022-06-22T07:24:15+02:00",
          "tree_id": "2282b5196ed778f706b5fba9127c2c07e8464173",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5834669a98dc2835c3d83ce4ebc531ef572cba27"
        },
        "date": 1655875521014,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9995013331926472,
            "unit": "iter/sec",
            "range": "stddev: 0.010332128563654138",
            "extra": "mean: 1.0004989156000021 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.427088028098494,
            "unit": "iter/sec",
            "range": "stddev: 0.005755342482397343",
            "extra": "mean: 69.31405686666494 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2712474041186713,
            "unit": "iter/sec",
            "range": "stddev: 0.007728486226955288",
            "extra": "mean: 3.686671226400006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "187224a2be5241b99b80a4f7059e3a4d95c5423d",
          "message": "DOC: Adjust PdfWriter.add_uri docstring",
          "timestamp": "2022-06-22T22:50:36+02:00",
          "tree_id": "e45c1bf4c803b154435e96f94a1a4d4dd5ef5e55",
          "url": "https://github.com/py-pdf/PyPDF2/commit/187224a2be5241b99b80a4f7059e3a4d95c5423d"
        },
        "date": 1655931123727,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7734757310115775,
            "unit": "iter/sec",
            "range": "stddev: 0.01632604896847123",
            "extra": "mean: 1.292865386599999 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.731648054818706,
            "unit": "iter/sec",
            "range": "stddev: 0.008910405761890528",
            "extra": "mean: 93.18233274999936 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21657330372165354,
            "unit": "iter/sec",
            "range": "stddev: 0.023027537481113143",
            "extra": "mean: 4.617374269200002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7d820f043ad56e0cc9dabb3921f1d64416777452",
          "message": "DEV: Adjust string formatting to be able to use mutmut (#1020)\n\nRelates to https://github.com/davidhalter/parso/issues/207\r\n\r\nAdditionally, make Makefile more consistent",
          "timestamp": "2022-06-23T20:27:15+02:00",
          "tree_id": "446bda930cd860f557a7176e8224f0d9dfc77db8",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7d820f043ad56e0cc9dabb3921f1d64416777452"
        },
        "date": 1656009040122,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1177823776370903,
            "unit": "iter/sec",
            "range": "stddev: 0.009965719155220187",
            "extra": "mean: 894.6285251999825 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.997578169926758,
            "unit": "iter/sec",
            "range": "stddev: 0.006213659726971437",
            "extra": "mean: 62.50946170588885 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.299768344251522,
            "unit": "iter/sec",
            "range": "stddev: 0.02201908622077705",
            "extra": "mean: 3.3359092752000037 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a412e2606c768b1b6af23b689025027e828ae850",
          "message": "BUG: Fix missing page for bookmark (#1016)\n\nRemove code duplication\r\n\r\nCloses #968 (introduced with #339)",
          "timestamp": "2022-06-23T21:26:09+02:00",
          "tree_id": "9abc4ac7a0b4867f30c20eb2c5ae37707bf3b857",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a412e2606c768b1b6af23b689025027e828ae850"
        },
        "date": 1656012435157,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9990275603593304,
            "unit": "iter/sec",
            "range": "stddev: 0.006161241369827674",
            "extra": "mean: 1.000973386199996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.258959304094551,
            "unit": "iter/sec",
            "range": "stddev: 0.006712363415944278",
            "extra": "mean: 70.1313454000001 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26998509436970625,
            "unit": "iter/sec",
            "range": "stddev: 0.01744498293439069",
            "extra": "mean: 3.7039081818 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a8c4dd9604485adc33afd283a1595b625581051d",
          "message": "DEV: Use /n line endings everywhere (#1027)",
          "timestamp": "2022-06-26T08:17:11+02:00",
          "tree_id": "746d9791e58f6ddf5e2c0ef79008e64e20c542a1",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a8c4dd9604485adc33afd283a1595b625581051d"
        },
        "date": 1656224318480,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7653366876534142,
            "unit": "iter/sec",
            "range": "stddev: 0.015333996015553216",
            "extra": "mean: 1.3066144824000048 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.30617606595212,
            "unit": "iter/sec",
            "range": "stddev: 0.008863717779954471",
            "extra": "mean: 97.02919818182015 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20876632096339717,
            "unit": "iter/sec",
            "range": "stddev: 0.05974816728304044",
            "extra": "mean: 4.790044655600025 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3c750c1faa64a4f1d5bc867e2d388ce4ce2c3b44",
          "message": "ENH: Add PdfReader.pdf_header (#1013)\n\nThe new attribute will return the first bytes of the PDF file. This is typically something like `\"%PDF-1.4\"`.\r\nThat can be used to get the PDF version of the file - at least the version the file claims to have.",
          "timestamp": "2022-06-26T08:38:12+02:00",
          "tree_id": "3bc9948e0c5d25da463df27e770c3c3252d5e9cb",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3c750c1faa64a4f1d5bc867e2d388ce4ce2c3b44"
        },
        "date": 1656225554187,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0068956278439363,
            "unit": "iter/sec",
            "range": "stddev: 0.018307786448851063",
            "extra": "mean: 993.1515961999935 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.385260519703731,
            "unit": "iter/sec",
            "range": "stddev: 0.006175751785531681",
            "extra": "mean: 69.51559887499315 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.271437167340339,
            "unit": "iter/sec",
            "range": "stddev: 0.056585051987500454",
            "extra": "mean: 3.6840938542000004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "595739faff13ba94f6d298798699db4301ebd3cd",
          "message": "ROB: Deal with invalid Destinations (#1028)\n\nIssue: An\r\n        AttributeError: 'NoneType' object has no attribute 'get_object'\r\n    was raised when trying to write a page that was merged.\r\n\r\nFix: Guard IndirectObject.get_object access\r\n\r\nCloses #997",
          "timestamp": "2022-06-26T09:29:11+02:00",
          "tree_id": "344cb3f835de5ee6c3244726b3f3a00a3efbf0c0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/595739faff13ba94f6d298798699db4301ebd3cd"
        },
        "date": 1656228616557,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0234472577316578,
            "unit": "iter/sec",
            "range": "stddev: 0.006483203371674798",
            "extra": "mean: 977.0899207999975 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.594254733055925,
            "unit": "iter/sec",
            "range": "stddev: 0.005065133531328095",
            "extra": "mean: 68.52011413333798 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2769250542889588,
            "unit": "iter/sec",
            "range": "stddev: 0.010892202134586451",
            "extra": "mean: 3.6110853262000093 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a40946c28841746ae848fb31158b5763afd2b943",
          "message": "DOC: get_form_text_fields does not extract dropdown data (#1029)\n\nSee #391",
          "timestamp": "2022-06-26T11:18:18+02:00",
          "tree_id": "421671c4b77cd03f8a8e3172a43c6ac2afa945e2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a40946c28841746ae848fb31158b5763afd2b943"
        },
        "date": 1656235174535,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8091602826919645,
            "unit": "iter/sec",
            "range": "stddev: 0.02515166351861388",
            "extra": "mean: 1.2358490912000009 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.431596468516,
            "unit": "iter/sec",
            "range": "stddev: 0.005759437112195673",
            "extra": "mean: 87.47684566666791 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22130012988910142,
            "unit": "iter/sec",
            "range": "stddev: 0.029128260060408008",
            "extra": "mean: 4.5187501720000025 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "exiledkingcc@gmail.com",
            "name": "exiledkingcc",
            "username": "exiledkingcc"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e83cdbe1cf7b7d189ed6fc899036ee31210a805f",
          "message": "ENH: Support R6 decrypting (#1015)\n\nSee #327, #377\r\nCloses #416",
          "timestamp": "2022-06-26T19:38:47+02:00",
          "tree_id": "0b3efc6256892b8a41a614a45313d95e88ddf1fb",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e83cdbe1cf7b7d189ed6fc899036ee31210a805f"
        },
        "date": 1656265186244,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1379811226433858,
            "unit": "iter/sec",
            "range": "stddev: 0.006011312198758261",
            "extra": "mean: 878.7491990000035 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.906947233164585,
            "unit": "iter/sec",
            "range": "stddev: 0.004930396495399016",
            "extra": "mean: 62.86561370588369 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.31084345393951257,
            "unit": "iter/sec",
            "range": "stddev: 0.006827447296995757",
            "extra": "mean: 3.2170534310000023 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "53efd73431775ab1d3eeaf546ccf73244869fb72",
          "message": "REL: 2.4.0\n\nNew Features (ENH):\n-  Support R6 decrypting (#1015)\n-  Add PdfReader.pdf_header (#1013)\n\nPerformance Improvements (PI):\n-  Remove ord_ calls (#1014)\n\nBug Fixes (BUG):\n-  Fix missing page for bookmark (#1016)\n\nRobustness (ROB):\n-  Deal with invalid Destinations (#1028)\n\nDocumentation (DOC):\n-  get_form_text_fields does not extract dropdown data (#1029)\n-  Adjust PdfWriter.add_uri docstring\n-  Mention crypto extra_requires for installation (#1017)\n\nDeveloper Experience (DEV):\n-  Use /n line endings everywhere (#1027)\n-  Adjust string formatting to be able to use mutmut (#1020)\n-  Update Bug report template\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.3.1...2.4.0",
          "timestamp": "2022-06-26T21:24:02+02:00",
          "tree_id": "2d3aab105edd67d922e353cd65b733e697dabbe4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/53efd73431775ab1d3eeaf546ccf73244869fb72"
        },
        "date": 1656271501092,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1719093686226723,
            "unit": "iter/sec",
            "range": "stddev: 0.010889952088712698",
            "extra": "mean: 853.3083076000025 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 16.21055379503692,
            "unit": "iter/sec",
            "range": "stddev: 0.004957855265430124",
            "extra": "mean: 61.688207117647245 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.3169960438870894,
            "unit": "iter/sec",
            "range": "stddev: 0.012915675499338955",
            "extra": "mean: 3.154613501600005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c7d24504282431efc4e7ae90bf55177e6940f5bb",
          "message": "DOC: Add CHANGELOG to the rendered docs (#1023)\n\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-06-28T07:20:10+02:00",
          "tree_id": "c0cac9073dd9490d56322506eb076b5afb9aac39",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c7d24504282431efc4e7ae90bf55177e6940f5bb"
        },
        "date": 1656393674429,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0171262973270403,
            "unit": "iter/sec",
            "range": "stddev: 0.008635347698013418",
            "extra": "mean: 983.1620740000062 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.138630409798562,
            "unit": "iter/sec",
            "range": "stddev: 0.005903963251785021",
            "extra": "mean: 70.7282085333361 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2787629132915852,
            "unit": "iter/sec",
            "range": "stddev: 0.020932752690622343",
            "extra": "mean: 3.5872777629999972 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "harry.karvonen@gmail.com",
            "name": "Harry Karvonen",
            "username": "Hatell"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ed832b3d91017a73673fb72ec1a78e96dd1a1ac9",
          "message": "PI: Check duplicate objects in writer._sweep_indirect_references (#207)\n\nThis check can reduce the file size significantly when writing PDFs and there are objects used multiple times, for example images.\r\n\r\nIf you read- and write a file again, this can already reduce the file size:\r\n\r\n```python\r\nfrom PyPDF2 import PdfReader, PdfWriter\r\n\r\nreader = PdfReader(\"big-old-file.pdf\")\r\nwriter = PdfWriter()\r\n\r\nfor page in reader.pages:\r\n    writer.add_page(page)\r\n\r\nwriter.add_metadata(reader.metadata)\r\n\r\nwith open(\"smaller-new-file.pdf\", \"wb\") as fp:\r\n    writer.write(fp)\r\n```\r\n\r\nFor the following files, the size was reduced significantly:\r\n\r\n* https://corpora.tika.apache.org/base/docs/govdocs1/958/958893.pdf : 5.7 MB ➔ 0.8 MB (-4.9 MB / -86%)\r\n* https://corpora.tika.apache.org/base/docs/govdocs1/949/949428.pdf : 6.7 MB ➔ 1.9 MB (-4.8 MB / -72%)\r\n* https://corpora.tika.apache.org/base/docs/govdocs1/911/911140.pdf : 8.8 MB ➔ 4.3 MB (-4.5 MB / -51%)\r\n\r\nCo-authored-by: Harry Karvonen <harry.karvonen@onebyte.fi>",
          "timestamp": "2022-06-28T17:27:36+02:00",
          "tree_id": "9edb4ff3f54851daf42611821153d2abaf22b824",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ed832b3d91017a73673fb72ec1a78e96dd1a1ac9"
        },
        "date": 1656430119809,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.148674161928067,
            "unit": "iter/sec",
            "range": "stddev: 0.007063714386839335",
            "extra": "mean: 870.5688986000041 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 17.87383759261543,
            "unit": "iter/sec",
            "range": "stddev: 0.0055493042269585775",
            "extra": "mean: 55.947694210511884 msec\nrounds: 19"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.3083825701534602,
            "unit": "iter/sec",
            "range": "stddev: 0.02027037595796119",
            "extra": "mean: 3.2427254221999986 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a89ff74d8c0203278a039d9496a3d8df4d134f84",
          "message": "STY: Docstring formatting (#1033)\n\nSee PEP-257 for some guides.\r\n\r\nflake8-naming was used to find those spots.\r\n\r\nThe \"rtype\" (return type) was removed from the docstrings as it already is in the type annotation in a more readable way + linked with the used type. It's also checked by mypy in the function signature.",
          "timestamp": "2022-06-28T17:32:35+02:00",
          "tree_id": "a09aa81bab2a49a259fb8a15e5e463ded0e75158",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a89ff74d8c0203278a039d9496a3d8df4d134f84"
        },
        "date": 1656430444558,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8667548510101643,
            "unit": "iter/sec",
            "range": "stddev: 0.00858566442630517",
            "extra": "mean: 1.1537287606000064 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.590327197220496,
            "unit": "iter/sec",
            "range": "stddev: 0.005896558608058444",
            "extra": "mean: 73.58174571429898 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23435479981000262,
            "unit": "iter/sec",
            "range": "stddev: 0.022095817530280906",
            "extra": "mean: 4.267034431599972 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "2c8914e2446c0ff026d2c900343fa1325cc2202a",
          "message": "DOC: File size reduction",
          "timestamp": "2022-06-28T18:32:07+02:00",
          "tree_id": "1793ce3009d39150328c4a7f009ecf4de2c5b4a3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2c8914e2446c0ff026d2c900343fa1325cc2202a"
        },
        "date": 1656433995309,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9901343188750673,
            "unit": "iter/sec",
            "range": "stddev: 0.008918080728143162",
            "extra": "mean: 1.0099639825999986 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.468334248487432,
            "unit": "iter/sec",
            "range": "stddev: 0.006586866566815495",
            "extra": "mean: 64.648202187497 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2686346937168512,
            "unit": "iter/sec",
            "range": "stddev: 0.027168105901579854",
            "extra": "mean: 3.7225273704000017 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "99034948+behzadfhm@users.noreply.github.com",
            "name": "Behzad Fahimi",
            "username": "behzadfhm"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "08c54d98e8cf7b2cf1fdb0a5bc38502d8a18998a",
          "message": "DOC: Fix inconsistent variable names in add-watermark.md (#1039)",
          "timestamp": "2022-06-29T12:32:11+02:00",
          "tree_id": "af46f949f1fe0979d25385aefe7269d26fe5309c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/08c54d98e8cf7b2cf1fdb0a5bc38502d8a18998a"
        },
        "date": 1656498798446,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.013853716923474,
            "unit": "iter/sec",
            "range": "stddev: 0.00776502494203068",
            "extra": "mean: 986.335586000007 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.51798068567379,
            "unit": "iter/sec",
            "range": "stddev: 0.004607006823694248",
            "extra": "mean: 64.44137418750628 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2765528983650209,
            "unit": "iter/sec",
            "range": "stddev: 0.020454923381853823",
            "extra": "mean: 3.615944746599996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f2ffa7af8f52eed3c37d9d6bc376db9f481b2a03",
          "message": "DOC: Compression of content streams (#1040)",
          "timestamp": "2022-06-29T13:37:35+02:00",
          "tree_id": "21c1d85f6b74d81b1f31e2e226be9ba1b4f88899",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f2ffa7af8f52eed3c37d9d6bc376db9f481b2a03"
        },
        "date": 1656502717482,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0091244868587101,
            "unit": "iter/sec",
            "range": "stddev: 0.007709364274456624",
            "extra": "mean: 990.9580165999998 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.402657272402028,
            "unit": "iter/sec",
            "range": "stddev: 0.004012592866452533",
            "extra": "mean: 64.92386231249637 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27375560805445426,
            "unit": "iter/sec",
            "range": "stddev: 0.018975984706865057",
            "extra": "mean: 3.6528932032000028 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0215cc77349f2540286527eea1c89a960c74c5ad",
          "message": "DOC: Remove hyphen from lossless (#1041)\n\nSigned-off-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-06-29T16:28:39+02:00",
          "tree_id": "30f6e7db84a44af794cc1b52e5a6fcbf05a1b18d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0215cc77349f2540286527eea1c89a960c74c5ad"
        },
        "date": 1656513506547,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0035401180258077,
            "unit": "iter/sec",
            "range": "stddev: 0.004281845081860131",
            "extra": "mean: 996.4723702000356 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.308966260322267,
            "unit": "iter/sec",
            "range": "stddev: 0.004248368468312421",
            "extra": "mean: 65.3211969374965 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27416175551273797,
            "unit": "iter/sec",
            "range": "stddev: 0.013860823522779732",
            "extra": "mean: 3.647481750799989 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eedf0e019f3e42572788f5073f2a8314378c9235",
          "message": "ENH: Add writer.pdf_header property (getter and setter) (#1038)\n\nWhen writing a PDF, set the version to the highest PDF version of the\r\nwritten ones\r\n\r\nCloses #162\r\n\r\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-06-29T22:13:23+02:00",
          "tree_id": "c34c3c1b373498a82182b12953e8b9cfa80adea5",
          "url": "https://github.com/py-pdf/PyPDF2/commit/eedf0e019f3e42572788f5073f2a8314378c9235"
        },
        "date": 1656533683329,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.746499346406679,
            "unit": "iter/sec",
            "range": "stddev: 0.026041546432880803",
            "extra": "mean: 1.3395859015999974 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.757915446767734,
            "unit": "iter/sec",
            "range": "stddev: 0.006353879923949406",
            "extra": "mean: 85.04908923077018 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20447614164306585,
            "unit": "iter/sec",
            "range": "stddev: 0.06699320087045386",
            "extra": "mean: 4.890546114400001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a85c7e702195c51214bbaa141a27b63b7eb981a5",
          "message": "DOC: How to surppress exceptions/warnings/log messages (#1037)",
          "timestamp": "2022-06-29T22:14:58+02:00",
          "tree_id": "92ee3792c08b8bcde74f79c8835d8c91448b1e9d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a85c7e702195c51214bbaa141a27b63b7eb981a5"
        },
        "date": 1656533762877,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0041741739004093,
            "unit": "iter/sec",
            "range": "stddev: 0.011278539429591899",
            "extra": "mean: 995.8431773999962 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.426389468806706,
            "unit": "iter/sec",
            "range": "stddev: 0.005089479526809303",
            "extra": "mean: 64.82398243750254 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27345833628825417,
            "unit": "iter/sec",
            "range": "stddev: 0.022080465486302134",
            "extra": "mean: 3.6568641993999904 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d1f2ed2e2db91c27cae21166a0176b76927beb71",
          "message": "MAINT: Deduplicate Code / add mutmut config (#1022)",
          "timestamp": "2022-06-29T22:32:23+02:00",
          "tree_id": "1e9aaf1ded9b43ab2b622aa0d00a69e79231443c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d1f2ed2e2db91c27cae21166a0176b76927beb71"
        },
        "date": 1656534805592,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0126441187160529,
            "unit": "iter/sec",
            "range": "stddev: 0.010238856321756255",
            "extra": "mean: 987.5137587999973 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.853910489796181,
            "unit": "iter/sec",
            "range": "stddev: 0.005157479699348695",
            "extra": "mean: 63.07592064706151 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27502633682316846,
            "unit": "iter/sec",
            "range": "stddev: 0.007235098119165882",
            "extra": "mean: 3.6360154141999943 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "84c3e33011f4dfc561065f68f1d5fc4624e79e84",
          "message": "STY: Use unnecessary one-line function / class attribute (#1043)",
          "timestamp": "2022-06-30T07:37:36+02:00",
          "tree_id": "7e4f5ed42a433e505e2ef3423045ff81ee561361",
          "url": "https://github.com/py-pdf/PyPDF2/commit/84c3e33011f4dfc561065f68f1d5fc4624e79e84"
        },
        "date": 1656567539413,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7599485299019875,
            "unit": "iter/sec",
            "range": "stddev: 0.013724561890913691",
            "extra": "mean: 1.3158785899999998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.830839665806483,
            "unit": "iter/sec",
            "range": "stddev: 0.0049775014142990626",
            "extra": "mean: 84.52485438461329 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2105165492752596,
            "unit": "iter/sec",
            "range": "stddev: 0.04621042711955402",
            "extra": "mean: 4.750220367199998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f1281b945c5be175cca6f9d61933ea45b44d45fa",
          "message": "PI: Remove b_ call in FloatObject.write_to_stream (#1044)\n\nAlso in writer.encrypt",
          "timestamp": "2022-06-30T08:10:59+02:00",
          "tree_id": "dce839116c8c68e44256b1f1be4a4f6741939094",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f1281b945c5be175cca6f9d61933ea45b44d45fa"
        },
        "date": 1656569533565,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8885055972096039,
            "unit": "iter/sec",
            "range": "stddev: 0.007059985487706229",
            "extra": "mean: 1.125485312799998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.57571454156501,
            "unit": "iter/sec",
            "range": "stddev: 0.006415192657544882",
            "extra": "mean: 73.66094778571559 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.235245603671324,
            "unit": "iter/sec",
            "range": "stddev: 0.06429349665714058",
            "extra": "mean: 4.250876464399994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "97f36bd097b9c677ef283bc39559b73aea76620b",
          "message": "MAINT: Handle XML error when reading XmpInformation (#1030)\n\nCloses #585",
          "timestamp": "2022-06-30T08:42:06+02:00",
          "tree_id": "3d3807875f44a4361d87088d5215d6ba81e768bc",
          "url": "https://github.com/py-pdf/PyPDF2/commit/97f36bd097b9c677ef283bc39559b73aea76620b"
        },
        "date": 1656571404625,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7724089784705354,
            "unit": "iter/sec",
            "range": "stddev: 0.03303557119633455",
            "extra": "mean: 1.294650926999998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.88787137326124,
            "unit": "iter/sec",
            "range": "stddev: 0.008583035786284533",
            "extra": "mean: 84.11934892307525 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23791658516058833,
            "unit": "iter/sec",
            "range": "stddev: 0.0715725539707955",
            "extra": "mean: 4.203153804199999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "66f00fcc1e921e63c4370aac47876da54d5d85ac",
          "message": "REL: 2.4.1\n\nNew Features (ENH):\n-  Add writer.pdf_header property (getter and setter) (#1038)\n\nPerformance Improvements (PI):\n-  Remove b_ call in FloatObject.write_to_stream (#1044)\n-  Check duplicate objects in writer._sweep_indirect_references (#207)\n\nDocumentation (DOC):\n-  How to surppress exceptions/warnings/log messages (#1037)\n-  Remove hyphen from lossless (#1041)\n-  Compression of content streams (#1040)\n-  Fix inconsistent variable names in add-watermark.md (#1039)\n-  File size reduction\n-  Add CHANGELOG to the rendered docs (#1023)\n\nMaintenance (MAINT):\n-  Handle XML error when reading XmpInformation (#1030)\n-  Deduplicate Code / add mutmut config (#1022)\n\nCode Style (STY):\n-  Use unnecessary one-line function / class attribute (#1043)\n-  Docstring formatting (#1033)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.4.0...2.4.1",
          "timestamp": "2022-06-30T08:44:39+02:00",
          "tree_id": "8cdaeb8ef2c762be05b3bee60e2794ac836f39d3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/66f00fcc1e921e63c4370aac47876da54d5d85ac"
        },
        "date": 1656571655132,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0389104949130572,
            "unit": "iter/sec",
            "range": "stddev: 0.005625843425303861",
            "extra": "mean: 962.5468266000013 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 16.10249057174322,
            "unit": "iter/sec",
            "range": "stddev: 0.0046015854190562",
            "extra": "mean: 62.102194411764344 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.28054329948271867,
            "unit": "iter/sec",
            "range": "stddev: 0.014699524143170321",
            "extra": "mean: 3.5645121513999998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4c43c0e4ad0224e4c277144e7235002521b0b1f9",
          "message": "TST: Increase test coverage (#1045)",
          "timestamp": "2022-07-03T16:34:52+02:00",
          "tree_id": "3f118730f2be9ddd5cdb06395ba1880084f47599",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4c43c0e4ad0224e4c277144e7235002521b0b1f9"
        },
        "date": 1656858962658,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8831321766451183,
            "unit": "iter/sec",
            "range": "stddev: 0.01741926438250307",
            "extra": "mean: 1.1323333317996003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.477219037454146,
            "unit": "iter/sec",
            "range": "stddev: 0.0064037445184355795",
            "extra": "mean: 74.19928378554427 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23813576825856742,
            "unit": "iter/sec",
            "range": "stddev: 0.06664910168698623",
            "extra": "mean: 4.1992851696020805 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0e18938fbb7ee56a57b20352e06df719683d7b42",
          "message": "ENH: Add PdfReader.xfa attribute (#1026)\n\nCloses #408\r\n\r\nCo-authored-by: George Alverson <George.Alverson@cern.ch>",
          "timestamp": "2022-07-03T16:52:01+02:00",
          "tree_id": "2ef11b0339bca68a1ea22194d8c25d1fd4e083e4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0e18938fbb7ee56a57b20352e06df719683d7b42"
        },
        "date": 1656859984043,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0501157454691517,
            "unit": "iter/sec",
            "range": "stddev: 0.011650141812943863",
            "extra": "mean: 952.2759794000024 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.782468476774657,
            "unit": "iter/sec",
            "range": "stddev: 0.003862412851988108",
            "extra": "mean: 63.36144447059035 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2808997606548474,
            "unit": "iter/sec",
            "range": "stddev: 0.011666032470771259",
            "extra": "mean: 3.5599887934000036 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3531603c52f84fdc5511bb7535be44c9bb9972e8",
          "message": "STY: Minimize diff for #879 (#1049)",
          "timestamp": "2022-07-03T17:06:17+02:00",
          "tree_id": "716c11911eb732ac08fc15779acafc78eb6d34a2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3531603c52f84fdc5511bb7535be44c9bb9972e8"
        },
        "date": 1656860842459,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0241342877650392,
            "unit": "iter/sec",
            "range": "stddev: 0.007717074942633117",
            "extra": "mean: 976.4344500000021 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.893362344765436,
            "unit": "iter/sec",
            "range": "stddev: 0.005512288415076764",
            "extra": "mean: 62.919348235293675 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27372076973262904,
            "unit": "iter/sec",
            "range": "stddev: 0.009998121806416953",
            "extra": "mean: 3.653358132000001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5d213ea31e9ee3b1b30d63d40411f38056ec12f6",
          "message": "TST: No pycryptodome (#1050)\n\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-07-03T21:13:23+02:00",
          "tree_id": "a3c9fe0184a1e28794fee201402e7159e1b3b2fa",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5d213ea31e9ee3b1b30d63d40411f38056ec12f6"
        },
        "date": 1656875677162,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8873823874609047,
            "unit": "iter/sec",
            "range": "stddev: 0.013403901620652976",
            "extra": "mean: 1.1269099028 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.849658741243115,
            "unit": "iter/sec",
            "range": "stddev: 0.0056485114246848005",
            "extra": "mean: 72.20394514285644 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2314203588113097,
            "unit": "iter/sec",
            "range": "stddev: 0.08350474105742015",
            "extra": "mean: 4.321140996999998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4097db98a7abd21308b40445c22e8e97bc3b5cda",
          "message": "TST: Invalid XML in xmp information (#1051)\n\nSee #1030",
          "timestamp": "2022-07-03T21:27:14+02:00",
          "tree_id": "eae9323cf5f9a1129cb5d1971d2e484bcccaba7f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4097db98a7abd21308b40445c22e8e97bc3b5cda"
        },
        "date": 1656876504834,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8861843927608105,
            "unit": "iter/sec",
            "range": "stddev: 0.00906952037229707",
            "extra": "mean: 1.1284333239999966 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.654239616140092,
            "unit": "iter/sec",
            "range": "stddev: 0.005914188660457808",
            "extra": "mean: 73.23732614285916 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23433005823722422,
            "unit": "iter/sec",
            "range": "stddev: 0.006942725508818936",
            "extra": "mean: 4.267484963399997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "04d576ceece98eb5dddddc3eeb0dad9fb6479f8a",
          "message": "TST: IndexError of VirtualList (#1052)",
          "timestamp": "2022-07-03T22:00:51+02:00",
          "tree_id": "9ec87bf3297f51f93284960270d743f742012aef",
          "url": "https://github.com/py-pdf/PyPDF2/commit/04d576ceece98eb5dddddc3eeb0dad9fb6479f8a"
        },
        "date": 1656878523663,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8990020477276282,
            "unit": "iter/sec",
            "range": "stddev: 0.010998084721664506",
            "extra": "mean: 1.112344518599997 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.808855761036249,
            "unit": "iter/sec",
            "range": "stddev: 0.005646733394771124",
            "extra": "mean: 72.41729635714275 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.24074166712894207,
            "unit": "iter/sec",
            "range": "stddev: 0.030220821747183282",
            "extra": "mean: 4.153830169599999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "harry.karvonen@gmail.com",
            "name": "Harry Karvonen",
            "username": "Hatell"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "32ab2a3423739b3327a2781782b0134b1c0aaa9f",
          "message": "DEV: Added {posargs} to tox.ini (#1055)\n\nThis allows adding options from command line. \r\n\r\nFor example, run only one test in py39 env using an option -k:\r\n$ tox -e py39 -- -k test_issue585\r\n\r\nFor example, run only one test in all envs using an option -k:\r\n$ tox -- -k test_issue585\r\n\r\nCo-authored-by: Harry Karvonen <harry.karvonen@onebyte.fi>",
          "timestamp": "2022-07-04T16:23:50+02:00",
          "tree_id": "1c627f160aa6da92db717da26700865f968d6585",
          "url": "https://github.com/py-pdf/PyPDF2/commit/32ab2a3423739b3327a2781782b0134b1c0aaa9f"
        },
        "date": 1656944715972,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7357501827849161,
            "unit": "iter/sec",
            "range": "stddev: 0.027845418127010125",
            "extra": "mean: 1.3591569848000062 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.3349138101134,
            "unit": "iter/sec",
            "range": "stddev: 0.007323175467311111",
            "extra": "mean: 88.22299108333453 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2029259698016985,
            "unit": "iter/sec",
            "range": "stddev: 0.01740625486775476",
            "extra": "mean: 4.927905486799995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4a62a47a984a78449347f52512c017ca0f306f09",
          "message": "TST: Simplify pathlib PdfReader test (#1056)\n\nThe Path constructor allows a variable amount of arguments to it which it joins together similar to os.path.join works, so it's not necessary to use os.path.join before passing the args to Path.",
          "timestamp": "2022-07-04T18:55:00+02:00",
          "tree_id": "2c2f2febb8b573555d1d857d730340d1cbf86d9a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4a62a47a984a78449347f52512c017ca0f306f09"
        },
        "date": 1656953804772,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8443208421023759,
            "unit": "iter/sec",
            "range": "stddev: 0.0119143774685313",
            "extra": "mean: 1.184383885999995 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.576837008355191,
            "unit": "iter/sec",
            "range": "stddev: 0.005294070132828775",
            "extra": "mean: 73.65485785714299 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.24253251798305825,
            "unit": "iter/sec",
            "range": "stddev: 0.061842954221642585",
            "extra": "mean: 4.1231584462 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "70605ae240cf1a4bb6578fcf75e95d0682b5fb92",
          "message": "TST: Scale page (indirect rect object) (#1057)",
          "timestamp": "2022-07-04T22:46:14+02:00",
          "tree_id": "b64edcc17ae220c58c3467ae2936acf46f9764c7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/70605ae240cf1a4bb6578fcf75e95d0682b5fb92"
        },
        "date": 1656967643409,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.943260964750468,
            "unit": "iter/sec",
            "range": "stddev: 0.0068350588749124",
            "extra": "mean: 1.0601520017999917 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.692621584947602,
            "unit": "iter/sec",
            "range": "stddev: 0.005062419971178204",
            "extra": "mean: 68.06137313333429 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25076831958788104,
            "unit": "iter/sec",
            "range": "stddev: 0.032498839979054006",
            "extra": "mean: 3.987744551000003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "harry.karvonen@gmail.com",
            "name": "Harry Karvonen",
            "username": "Hatell"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "02c601c86819578d9796479a1b8953accefea92b",
          "message": "BUG: Resolve IndirectObject when it refers to a free entry (#1054)\n\nFrom the PDF 1.7 docs https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf:\r\n\r\nSection 7.3.10 Indirect Objects:\r\nAn indirect reference to an undefined object shall not be considered an error by a conforming reader;\r\nit shall be treated as a reference to the null object.\r\n\r\nAnd section 7.5.4 Cross-Reference Table:\r\nThere are two ways an entry may be a member of the free entries list. Using the basic mechanism the free\r\nentries in the cross-reference table may form a linked list, with each free entry containing the object number of\r\nthe next. The first entry in the table (object number 0) shall always be free and shall have a generation number\r\nof 65,535; it is shall be the head of the linked list of free objects. The last free entry (the tail of the linked list)\r\nlinks back to object number 0. Using the second mechanism, the table may contain other free entries that link\r\nback to object number 0 and have a generation number of 65,535, even though these entries are not in the\r\nlinked list itself.\r\n\r\nThose entries form a linked list. The correct way to handle this is to resolve the indirect reference to the NullObject.\r\n\r\nSee \"3.4.3 Cross-Reference Table\" in the PDF 1.7 standard for free cross-reference entries in general.\r\n\r\nCo-authored-by: Harry Karvonen <harry.karvonen@onebyte.fi>\r\n\r\nCloses #521\r\nCloses #1034",
          "timestamp": "2022-07-05T10:20:44+02:00",
          "tree_id": "4f5b338e32b74c288d8f4f8782009960bb8c94ad",
          "url": "https://github.com/py-pdf/PyPDF2/commit/02c601c86819578d9796479a1b8953accefea92b"
        },
        "date": 1657009318683,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0497777182183352,
            "unit": "iter/sec",
            "range": "stddev: 0.005951886660807513",
            "extra": "mean: 952.5826112000004 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 16.12849695722835,
            "unit": "iter/sec",
            "range": "stddev: 0.004810048194116284",
            "extra": "mean: 62.00205776470866 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2795944767368405,
            "unit": "iter/sec",
            "range": "stddev: 0.026536790501431994",
            "extra": "mean: 3.576608564199995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ffacabc7a01a975d03a444fcfa03154c5b131164",
          "message": "MAINT: Remove PyPDF2._utils.bytes_type (#1053)",
          "timestamp": "2022-07-05T10:53:45+02:00",
          "tree_id": "2505a6e399744a9e7369b552c1cce0db8b1c191d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ffacabc7a01a975d03a444fcfa03154c5b131164"
        },
        "date": 1657011285184,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0477506638022656,
            "unit": "iter/sec",
            "range": "stddev: 0.0066571024461532825",
            "extra": "mean: 954.4255466000095 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 15.794999419276637,
            "unit": "iter/sec",
            "range": "stddev: 0.0038192099736281565",
            "extra": "mean: 63.31117675000186 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27885055962922584,
            "unit": "iter/sec",
            "range": "stddev: 0.019240813512194845",
            "extra": "mean: 3.5861502352000003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1e9c4ddec01f6d5b658a687437d0caf0b09db768",
          "message": "STY: DOC of compress_content_streams (#1061)",
          "timestamp": "2022-07-05T11:42:35+02:00",
          "tree_id": "98b5aae27e744067313a2d017067da6f8e6cc6ae",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1e9c4ddec01f6d5b658a687437d0caf0b09db768"
        },
        "date": 1657014220316,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9915143750740664,
            "unit": "iter/sec",
            "range": "stddev: 0.03529954170487882",
            "extra": "mean: 1.0085582469999992 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 16.081104022731697,
            "unit": "iter/sec",
            "range": "stddev: 0.005517978471816257",
            "extra": "mean: 62.184785235294434 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2777667745871043,
            "unit": "iter/sec",
            "range": "stddev: 0.015032280746965563",
            "extra": "mean: 3.6001426070000035 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "621a51f9552731928e73689ae17161214f9cddcf",
          "message": "BUG: Wrong page inserted when PdfMerger.merge is done (#1063)\n\nCaused-by: #207\r\n\r\nWhy it wasn't detected by the tests: We don't have any tests that check\r\nfor the correct result of a merge. We just check for exceptions\r\n\r\nHow we prevent it in future: Unit test was added\r\n\r\nRisk of the fix:\r\n- We will have bigger file sizes again as #207 was effectively reverted\r\n- We will need to adjust this test if we change the way we write PDFs\r\n\r\nCloses: #1062",
          "timestamp": "2022-07-05T14:34:37+02:00",
          "tree_id": "e4f5b6e44d7d87b09071878b7b536c2a94885be5",
          "url": "https://github.com/py-pdf/PyPDF2/commit/621a51f9552731928e73689ae17161214f9cddcf"
        },
        "date": 1657024539267,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0467339357431968,
            "unit": "iter/sec",
            "range": "stddev: 0.00445794756712191",
            "extra": "mean: 955.352612400003 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.971924397819953,
            "unit": "iter/sec",
            "range": "stddev: 0.0043864352662166695",
            "extra": "mean: 71.57210213333467 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2797901876661233,
            "unit": "iter/sec",
            "range": "stddev: 0.011401319073286491",
            "extra": "mean: 3.5741067560000035 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "a34569089e6699b2461d71143dbb2a0a0ff1796b",
          "message": "REL: 2.4.2\n\nNew Features (ENH):\n-  Add PdfReader.xfa attribute (#1026)\n\nBug Fixes (BUG):\n-  Wrong page inserted when PdfMerger.merge is done (#1063)\n-  Resolve IndirectObject when it refers to a free entry (#1054)\n\nDeveloper Experience (DEV):\n-  Added {posargs} to tox.ini (#1055)\n\nMaintenance (MAINT):\n-  Remove PyPDF2._utils.bytes_type (#1053)\n\nTesting (TST):\n-  Scale page (indirect rect object) (#1057)\n-  Simplify pathlib PdfReader test (#1056)\n-  IndexError of VirtualList (#1052)\n-  Invalid XML in xmp information (#1051)\n-  No pycryptodome (#1050)\n-  Increase test coverage (#1045)\n\nCode Style (STY):\n-  DOC of compress_content_streams (#1061)\n-  Minimize diff for #879 (#1049)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.4.1...2.4.2",
          "timestamp": "2022-07-05T14:37:03+02:00",
          "tree_id": "495569c09f8e7dfb53c139a92e6a8fd7a1217c7f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a34569089e6699b2461d71143dbb2a0a0ff1796b"
        },
        "date": 1657024750786,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.425680099634246,
            "unit": "iter/sec",
            "range": "stddev: 0.0057479501024147745",
            "extra": "mean: 701.4196243999947 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 20.867720689040873,
            "unit": "iter/sec",
            "range": "stddev: 0.0033925636589958296",
            "extra": "mean: 47.92090209091074 msec\nrounds: 22"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.3728863476947458,
            "unit": "iter/sec",
            "range": "stddev: 0.07816821817936107",
            "extra": "mean: 2.6817822808000074 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a1aaf91e6d8cde09e5efbbd17e82937be180001f",
          "message": "DEV: Speed-up for CI (#1069)\n\n- pytest: Set pytest testpaths and norecursedirs\r\n- dependencies: Cache pip packages (pycryptodome)",
          "timestamp": "2022-07-07T07:12:28+02:00",
          "tree_id": "323f08856d592e7019d461c1c8e3fb0cc504028d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a1aaf91e6d8cde09e5efbbd17e82937be180001f"
        },
        "date": 1657170806647,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0449442374556912,
            "unit": "iter/sec",
            "range": "stddev: 0.007404496750385735",
            "extra": "mean: 956.9888651999989 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.100198643598358,
            "unit": "iter/sec",
            "range": "stddev: 0.006030902905776551",
            "extra": "mean: 70.92098666666733 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27532792111705123,
            "unit": "iter/sec",
            "range": "stddev: 0.01775698611713741",
            "extra": "mean: 3.6320326537999974 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ff5fd88fec3a350d513f85f1ddf50c9b80e00d29",
          "message": "DEV: Cache downloaded files (#1070)\n\nAlso: Fix pycryptodome uninstall in CI",
          "timestamp": "2022-07-07T07:37:37+02:00",
          "tree_id": "c0103dc5d910073839462165451e83afd6e84813",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ff5fd88fec3a350d513f85f1ddf50c9b80e00d29"
        },
        "date": 1657172329245,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8687574681519459,
            "unit": "iter/sec",
            "range": "stddev: 0.017326264574992093",
            "extra": "mean: 1.1510692416000041 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.483461490100849,
            "unit": "iter/sec",
            "range": "stddev: 0.006759483395572858",
            "extra": "mean: 80.10598669231136 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23940974604647547,
            "unit": "iter/sec",
            "range": "stddev: 0.12327075702392903",
            "extra": "mean: 4.176939395800014 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "810691a13d43264c2b56f1ecac7b49bae613a8bd",
          "message": "DOC: Formatting of CHANGELOG",
          "timestamp": "2022-07-07T13:24:47+02:00",
          "tree_id": "a52c1f199d917059d5bc596b8811b03579fbb997",
          "url": "https://github.com/py-pdf/PyPDF2/commit/810691a13d43264c2b56f1ecac7b49bae613a8bd"
        },
        "date": 1657193159432,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.041264120031903,
            "unit": "iter/sec",
            "range": "stddev: 0.005935327335556905",
            "extra": "mean: 960.3711304000001 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.942696595228771,
            "unit": "iter/sec",
            "range": "stddev: 0.004683809448610708",
            "extra": "mean: 71.72213733333356 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27943851654104046,
            "unit": "iter/sec",
            "range": "stddev: 0.013877451712638426",
            "extra": "mean: 3.578604740600004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "d63ab2c3f2aff08936afd7702028adbf6257d384",
          "message": "DOC: Python Version support",
          "timestamp": "2022-07-07T13:26:13+02:00",
          "tree_id": "a9ac3a0fe778e22e070d08dacf26867d0add4ef2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d63ab2c3f2aff08936afd7702028adbf6257d384"
        },
        "date": 1657193244248,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0354779197434465,
            "unit": "iter/sec",
            "range": "stddev: 0.0069140408970934895",
            "extra": "mean: 965.7376376000017 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.87100669805083,
            "unit": "iter/sec",
            "range": "stddev: 0.00470584441700895",
            "extra": "mean: 72.09282078571277 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2785180052151988,
            "unit": "iter/sec",
            "range": "stddev: 0.017408741601914978",
            "extra": "mean: 3.5904321490000015 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "67d6e098ef2d802d3fd9d265992d1dc80f582d34",
          "message": "STY: Typo in Changelog",
          "timestamp": "2022-07-07T13:57:28+02:00",
          "tree_id": "79e7d5401990d56fac6842eee5ce3411fd378a68",
          "url": "https://github.com/py-pdf/PyPDF2/commit/67d6e098ef2d802d3fd9d265992d1dc80f582d34"
        },
        "date": 1657195109496,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1754966151642048,
            "unit": "iter/sec",
            "range": "stddev: 0.007759835923096524",
            "extra": "mean: 850.7042785999943 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 16.08797364293263,
            "unit": "iter/sec",
            "range": "stddev: 0.0049752366404768",
            "extra": "mean: 62.15823211764741 msec\nrounds: 17"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.31268246127729743,
            "unit": "iter/sec",
            "range": "stddev: 0.02018035792712163",
            "extra": "mean: 3.1981326867999997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "67d962d54e34453a0fb33df5a1939e68cf850130",
          "message": "TST: Image extraction (#1077)",
          "timestamp": "2022-07-09T10:21:29+02:00",
          "tree_id": "b1966200e5ebde0be6e48fa71d292d51ccbbc317",
          "url": "https://github.com/py-pdf/PyPDF2/commit/67d962d54e34453a0fb33df5a1939e68cf850130"
        },
        "date": 1657354953739,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0245601934492583,
            "unit": "iter/sec",
            "range": "stddev: 0.016923357985925695",
            "extra": "mean: 976.0285500000009 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.024536255288538,
            "unit": "iter/sec",
            "range": "stddev: 0.005939213865019135",
            "extra": "mean: 71.30360546666263 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2756547062261239,
            "unit": "iter/sec",
            "range": "stddev: 0.03183663892842056",
            "extra": "mean: 3.6277269258000047 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9b048a266894d0ab0a549915c519220007b1d1e3",
          "message": "MAINT: Issue #416 was fixed by #1015 (#1078)",
          "timestamp": "2022-07-09T10:33:45+02:00",
          "tree_id": "71242b62c1760b1ac61e033588a90ab5f469b0d4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9b048a266894d0ab0a549915c519220007b1d1e3"
        },
        "date": 1657355683512,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0301912417289814,
            "unit": "iter/sec",
            "range": "stddev: 0.005131405789687868",
            "extra": "mean: 970.6935562000012 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.7904056771807,
            "unit": "iter/sec",
            "range": "stddev: 0.00544463967014928",
            "extra": "mean: 72.51418293333624 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2745404691962211,
            "unit": "iter/sec",
            "range": "stddev: 0.02000852063352502",
            "extra": "mean: 3.642450247600016 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f4f74c7c9415dc96333cf6fd712868edf7fcff33",
          "message": "BUG: Column default for CCITTFaxDecode (#1079)",
          "timestamp": "2022-07-09T10:43:52+02:00",
          "tree_id": "7bf236219aac3e4fccd9b64ff108e76a5a614635",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f4f74c7c9415dc96333cf6fd712868edf7fcff33"
        },
        "date": 1657356290579,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0500447314120365,
            "unit": "iter/sec",
            "range": "stddev: 0.007942194826694537",
            "extra": "mean: 952.3403814000005 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.215345994433285,
            "unit": "iter/sec",
            "range": "stddev: 0.005469558949859523",
            "extra": "mean: 70.3465114666642 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2769179652491972,
            "unit": "iter/sec",
            "range": "stddev: 0.02870064265297541",
            "extra": "mean: 3.6111777692000033 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f776f54c673674c31e81b8c4dba88f60e51c1006",
          "message": "ENH: Add support for indexed color spaces / BitsPerComponent for decoding PNGs (#1067)\n\nCloses #535\r\nCloses #536\r\n\r\nCo-authored-by: Christopher Egner <chris@science.clinic>",
          "timestamp": "2022-07-09T11:28:09+02:00",
          "tree_id": "f707cb14a56c221b6c117fc6d9bc94457cc369d3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f776f54c673674c31e81b8c4dba88f60e51c1006"
        },
        "date": 1657358967522,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8671449720400788,
            "unit": "iter/sec",
            "range": "stddev: 0.01704221892288181",
            "extra": "mean: 1.1532097079999915 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.861176728266669,
            "unit": "iter/sec",
            "range": "stddev: 0.007274560817846208",
            "extra": "mean: 84.30866708333203 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2296303151227268,
            "unit": "iter/sec",
            "range": "stddev: 0.07440090977009457",
            "extra": "mean: 4.354825709599998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3a8199cdf9e51407e6583aa36ad7ec417d04f87d",
          "message": "TST: Image extraction (#1080)",
          "timestamp": "2022-07-09T13:48:49+02:00",
          "tree_id": "2617c9ac584c0ab85d7fb29b2cfb5a11b0a8c055",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3a8199cdf9e51407e6583aa36ad7ec417d04f87d"
        },
        "date": 1657367390369,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0430483648035938,
            "unit": "iter/sec",
            "range": "stddev: 0.007244875131890901",
            "extra": "mean: 958.7283138000032 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.034292186675634,
            "unit": "iter/sec",
            "range": "stddev: 0.0046229960041713055",
            "extra": "mean: 71.25403880000553 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.28038781641415506,
            "unit": "iter/sec",
            "range": "stddev: 0.014385723573318167",
            "extra": "mean: 3.5664887754000008 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "439c7499e82b268a469d8971b27ccc4ff3dbb7ef",
          "message": "ROB: Guard against None-value in _get_outlines (#1060)\n\nSee #1059",
          "timestamp": "2022-07-09T13:49:37+02:00",
          "tree_id": "e15defe461f9dd900bcfb007f8339099fa84bba1",
          "url": "https://github.com/py-pdf/PyPDF2/commit/439c7499e82b268a469d8971b27ccc4ff3dbb7ef"
        },
        "date": 1657367455052,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7940974203838788,
            "unit": "iter/sec",
            "range": "stddev: 0.02347240210431548",
            "extra": "mean: 1.2592913342000087 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.1744341008032,
            "unit": "iter/sec",
            "range": "stddev: 0.007954584680552096",
            "extra": "mean: 89.48999036363924 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21399615976572653,
            "unit": "iter/sec",
            "range": "stddev: 0.04480082188996308",
            "extra": "mean: 4.6729810529999956 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8edaca8f1d747ccdb2abe770da55270fd31c6295",
          "message": "BUG: Let Page.scale also scale the crop-/trim-/bleed-/artbox (#1066)\n\nCloses #272\r\n\r\nCo-authored-by: Brian Painter <brianpainter@tindallcorp.com>",
          "timestamp": "2022-07-09T13:50:51+02:00",
          "tree_id": "5973fb374c27ef6e60382475174af1d6ce0aa872",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8edaca8f1d747ccdb2abe770da55270fd31c6295"
        },
        "date": 1657367521499,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9140571551193449,
            "unit": "iter/sec",
            "range": "stddev: 0.00994067322391346",
            "extra": "mean: 1.0940234911999938 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.660256934723575,
            "unit": "iter/sec",
            "range": "stddev: 0.006098691467236528",
            "extra": "mean: 78.98733850000131 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.244218284124805,
            "unit": "iter/sec",
            "range": "stddev: 0.016555680011455607",
            "extra": "mean: 4.094697510400005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9794ef65b7ed84916c8279909026c5d970687275",
          "message": "DOC: OCR vs PDF text extraction (#1081)\n\nCloses #1073",
          "timestamp": "2022-07-09T15:04:15+02:00",
          "tree_id": "6e231e889c9059bed6038933cadbd1286a4d9d82",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9794ef65b7ed84916c8279909026c5d970687275"
        },
        "date": 1657371919755,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0285001710939805,
            "unit": "iter/sec",
            "range": "stddev: 0.01152277735210349",
            "extra": "mean: 972.2895806000054 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.023815851778105,
            "unit": "iter/sec",
            "range": "stddev: 0.006535877293702384",
            "extra": "mean: 71.3072683333337 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27412252294605693,
            "unit": "iter/sec",
            "range": "stddev: 0.02078884313271755",
            "extra": "mean: 3.648003780399995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b42e0dbdf400a0c96391c2b391708ac8eb83a311",
          "message": "DOC: Stamps and watermarks (#1082)\n\nCloses #307\r\nCloses #410",
          "timestamp": "2022-07-09T15:48:51+02:00",
          "tree_id": "450432965125876936d7d6414055512c03ce0083",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b42e0dbdf400a0c96391c2b391708ac8eb83a311"
        },
        "date": 1657374608239,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8091174175399055,
            "unit": "iter/sec",
            "range": "stddev: 0.012322910534828013",
            "extra": "mean: 1.2359145636000108 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.275539516314105,
            "unit": "iter/sec",
            "range": "stddev: 0.005935760489898854",
            "extra": "mean: 88.68755224999585 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22000416483372376,
            "unit": "iter/sec",
            "range": "stddev: 0.03335396845884524",
            "extra": "mean: 4.545368496799989 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "harry.karvonen@gmail.com",
            "name": "Harry Karvonen",
            "username": "Hatell"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1e4c2c9b4649449241b0ae166e7e90f6bc61596d",
          "message": "PI: Use iterative DFS in PdfWriter._sweep_indirect_references (#1072)\n\n* Recursive Depth-first search (DFS) was changed to iterative DFS\r\n* Removed PdfWriter.external_reference_map and calculate hash from every referred object and use that to detect duplicate objects.\r\n* In several cases, the warning \"Unable to resolve .*, returning NullObject instead\" is no longer necessary.\r\n* Bugfix: Recalculate all parents hashes when a dictionary or array object value changes\r\n\r\nCloses #351\r\nCloses #1036",
          "timestamp": "2022-07-10T14:06:48+02:00",
          "tree_id": "71407213de13b6b7f1226e2e321d46e5f3aea4b2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1e4c2c9b4649449241b0ae166e7e90f6bc61596d"
        },
        "date": 1657454880818,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9489710604009811,
            "unit": "iter/sec",
            "range": "stddev: 0.026955488948409385",
            "extra": "mean: 1.0537729143999996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.84893789082983,
            "unit": "iter/sec",
            "range": "stddev: 0.006420936732895826",
            "extra": "mean: 84.39574999999986 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2579198140478857,
            "unit": "iter/sec",
            "range": "stddev: 0.0184237342150669",
            "extra": "mean: 3.8771740112000033 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e51141d7ed735703bb07f5ffa7e5d2f4d9a79347",
          "message": "ENH: Add PageObject._get_fonts (#1083)\n\nAdd possibility to get names of fonts\r\n\r\nSee #153\r\n\r\nCo-authored-by: tiarno <jtim.arnold@gmail.com>",
          "timestamp": "2022-07-10T15:53:04+02:00",
          "tree_id": "ab246a1f3a0fc9c700a39aa01c02f78d187aad96",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e51141d7ed735703bb07f5ffa7e5d2f4d9a79347"
        },
        "date": 1657461248070,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.4432589149770836,
            "unit": "iter/sec",
            "range": "stddev: 0.004607637363015814",
            "extra": "mean: 692.8763713999842 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 19.183757625006596,
            "unit": "iter/sec",
            "range": "stddev: 0.00322877802375587",
            "extra": "mean: 52.12743090000629 msec\nrounds: 20"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.38267671883616955,
            "unit": "iter/sec",
            "range": "stddev: 0.02559102476699079",
            "extra": "mean: 2.6131717733999835 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c5c0b5547cc607e6c1a340873dfbc987ed0e752b",
          "message": "MAINT: Set page.rotate(angle: int) (#1092)\n\nCloses #1021\r\n\r\nCo-authored-by: probel_hero <93727145+SXHRYU@users.noreply.github.com>",
          "timestamp": "2022-07-10T16:02:21+02:00",
          "tree_id": "294dfbb37aab5dc7d01328969372873eb129d93f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c5c0b5547cc607e6c1a340873dfbc987ed0e752b"
        },
        "date": 1657461808618,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9858302514927426,
            "unit": "iter/sec",
            "range": "stddev: 0.03437761411849744",
            "extra": "mean: 1.0143734162000015 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.243561454322077,
            "unit": "iter/sec",
            "range": "stddev: 0.013930276317956186",
            "extra": "mean: 81.67558138461354 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2637072187334048,
            "unit": "iter/sec",
            "range": "stddev: 0.07955456147981202",
            "extra": "mean: 3.792084284999993 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "46ba4aeae2009ef94f2bf89047af01d28fc0807e",
          "message": "STY: Apply black",
          "timestamp": "2022-07-10T16:14:39+02:00",
          "tree_id": "13477cc3349539c484e4f1e1c76ca54a74fd5b25",
          "url": "https://github.com/py-pdf/PyPDF2/commit/46ba4aeae2009ef94f2bf89047af01d28fc0807e"
        },
        "date": 1657462554667,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9282931177279148,
            "unit": "iter/sec",
            "range": "stddev: 0.016877930404253585",
            "extra": "mean: 1.0772459483999994 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.68091775022726,
            "unit": "iter/sec",
            "range": "stddev: 0.007181095272067105",
            "extra": "mean: 85.60971161538606 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2488436492550186,
            "unit": "iter/sec",
            "range": "stddev: 0.05111446603990091",
            "extra": "mean: 4.018587587000002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "8f47939c5d056970153ffcf428412c52727645f1",
          "message": "REL: 2.5.0\n\nNew Features (ENH):\n-  Add PageObject._get_fonts (#1083)\n-  Add support for indexed color spaces / BitsPerComponent for decoding PNGs (#1067)\n\nPerformance Improvements (PI):\n-  Use iterative DFS in PdfWriter._sweep_indirect_references (#1072)\n\nBug Fixes (BUG):\n-  Let Page.scale also scale the crop-/trim-/bleed-/artbox (#1066)\n-  Column default for CCITTFaxDecode (#1079)\n\nRobustness (ROB):\n-  Guard against None-value in _get_outlines (#1060)\n\nDocumentation (DOC):\n-  Stamps and watermarks (#1082)\n-  OCR vs PDF text extraction (#1081)\n-  Python Version support\n-  Formatting of CHANGELOG\n\nDeveloper Experience (DEV):\n-  Cache downloaded files (#1070)\n-  Speed-up for CI (#1069)\n\nMaintenance (MAINT):\n-  Set page.rotate(angle: int) (#1092)\n-  Issue #416 was fixed by #1015 (#1078)\n\nTesting (TST):\n-  Image extraction (#1080)\n-  Image extraction (#1077)\n\nCode Style (STY):\n-  Apply black\n-  Typo in Changelog\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.4.2...2.4.3",
          "timestamp": "2022-07-10T16:18:19+02:00",
          "tree_id": "428da4f2fbab382fac5e7bb7f1a435df9ab81220",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8f47939c5d056970153ffcf428412c52727645f1"
        },
        "date": 1657462811997,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0359888593620326,
            "unit": "iter/sec",
            "range": "stddev: 0.006811872858583174",
            "extra": "mean: 965.2613451999912 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.92483433069683,
            "unit": "iter/sec",
            "range": "stddev: 0.004693594979469746",
            "extra": "mean: 77.37043078571405 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27798380332696093,
            "unit": "iter/sec",
            "range": "stddev: 0.00977305022263045",
            "extra": "mean: 3.5973318877999985 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b2279eeb40fa0557e6e61e3bada0de0373e6da28",
          "message": "DOC: Watermark and stamp (#1095)\n\nSee #307",
          "timestamp": "2022-07-11T07:59:54+02:00",
          "tree_id": "a4c15d67578d14d9faf500b66af51942f1d7689e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b2279eeb40fa0557e6e61e3bada0de0373e6da28"
        },
        "date": 1657519288240,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0281486756210116,
            "unit": "iter/sec",
            "range": "stddev: 0.010667752083935732",
            "extra": "mean: 972.621979400003 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.053193647503116,
            "unit": "iter/sec",
            "range": "stddev: 0.0065112207015371485",
            "extra": "mean: 76.60960428571327 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.277841806360311,
            "unit": "iter/sec",
            "range": "stddev: 0.01931916743074996",
            "extra": "mean: 3.599170380799998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d7b64dc817a948b275f221d326746ee07130e2de",
          "message": "MAINT: Use add_bookmark_destination in add_bookmark_dict (#1099)\n\nRe-use code\r\n\r\nSee #1098",
          "timestamp": "2022-07-12T07:47:11+02:00",
          "tree_id": "47d9469880066927561c72d4b02846fc28def03d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d7b64dc817a948b275f221d326746ee07130e2de"
        },
        "date": 1657604901746,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9698349404610689,
            "unit": "iter/sec",
            "range": "stddev: 0.01871675039972224",
            "extra": "mean: 1.031103292200001 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.138948501772013,
            "unit": "iter/sec",
            "range": "stddev: 0.007415669602696842",
            "extra": "mean: 82.379458142855 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2535416047031901,
            "unit": "iter/sec",
            "range": "stddev: 0.08128608835123619",
            "extra": "mean: 3.944125861200001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c420beb32c89f17822fb0e25d23db3f25ebd9af9",
          "message": "MAINT: Use add_bookmark_destination in add_bookmark (#1100)\n\nReduce code duplication\r\n\r\nSee #1098",
          "timestamp": "2022-07-12T08:20:59+02:00",
          "tree_id": "c2ae4c70f7d843fd279fe2ce3c1e25ce5f8228a3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c420beb32c89f17822fb0e25d23db3f25ebd9af9"
        },
        "date": 1657606922533,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0457068949005572,
            "unit": "iter/sec",
            "range": "stddev: 0.005784208750178398",
            "extra": "mean: 956.2909117999993 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.182532990117588,
            "unit": "iter/sec",
            "range": "stddev: 0.006423671315346597",
            "extra": "mean: 75.85795542857048 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2761141790346218,
            "unit": "iter/sec",
            "range": "stddev: 0.01556251562206628",
            "extra": "mean: 3.6216901410000046 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d376d0e71939decbe21de8e93d016f09b3ce2210",
          "message": "STY: Simplify code (#1101)",
          "timestamp": "2022-07-12T09:33:40+02:00",
          "tree_id": "3e025f97068fc3bd08a712ca8dc115498b4192cd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d376d0e71939decbe21de8e93d016f09b3ce2210"
        },
        "date": 1657611285271,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0355050211036876,
            "unit": "iter/sec",
            "range": "stddev: 0.00948496836767645",
            "extra": "mean: 965.7123621999972 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.013706586070336,
            "unit": "iter/sec",
            "range": "stddev: 0.006234061509155801",
            "extra": "mean: 76.84205828571423 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27742335483101765,
            "unit": "iter/sec",
            "range": "stddev: 0.02233486697769969",
            "extra": "mean: 3.604599189600002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "af5a0c3394a33eae154c63f5ccaa403ca54dbf1b",
          "message": "STY: Use IntFlag for permissions_flag / update_page_form_field_values (#1094)",
          "timestamp": "2022-07-12T09:39:18+02:00",
          "tree_id": "6baa1dac6254031379c6b9e4ab5f5bbacca401e3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/af5a0c3394a33eae154c63f5ccaa403ca54dbf1b"
        },
        "date": 1657611625991,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9407199716353059,
            "unit": "iter/sec",
            "range": "stddev: 0.040010764193426196",
            "extra": "mean: 1.0630155946000002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.620911095183994,
            "unit": "iter/sec",
            "range": "stddev: 0.0053748369496096375",
            "extra": "mean: 79.23358246153794 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2614913010553103,
            "unit": "iter/sec",
            "range": "stddev: 0.041766541713557294",
            "extra": "mean: 3.824218993000005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "682eff93a1250403ed08c058e65d8576772ca858",
          "message": "ENH: Extract Text Enhancement (whitespaces) (#1084)\n\n* ENH : extract width from CIDFontType0/2\r\n* ENH  : improve cr/lf and space extraction\r\n* BUG : fix error in decoding #1075\r\n* FIX: in ToUnicode  ignore comments (starting with %)\r\n* FIX: extend utf16 for min of 4 characters\r\n\r\nImproves #234\r\nImproves #957\r\nCloses #1003\r\nCloses #1019\r\n\r\nUsed https://tug.ctan.org/info/symbols/comprehensive/symbols-a4.pdf for testing",
          "timestamp": "2022-07-13T07:18:05+02:00",
          "tree_id": "0d624d18e71b9360b6635edf29d5993c0b999c67",
          "url": "https://github.com/py-pdf/PyPDF2/commit/682eff93a1250403ed08c058e65d8576772ca858"
        },
        "date": 1657689566939,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8090096765778556,
            "unit": "iter/sec",
            "range": "stddev: 0.01361006369669548",
            "extra": "mean: 1.2360791581999877 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.1964833513567,
            "unit": "iter/sec",
            "range": "stddev: 0.007659916808256996",
            "extra": "mean: 98.0730282727274 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20846552263282994,
            "unit": "iter/sec",
            "range": "stddev: 0.00942761138488269",
            "extra": "mean: 4.79695628980001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mtd91429@users.noreply.github.com",
            "name": "mtd91429",
            "username": "mtd91429"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5e1cc57677c2ee9b80d9ed27a41321d3cae2d7c3",
          "message": "ENH: Add color and font_format to PdfReader.outlines[i] (#1104)",
          "timestamp": "2022-07-14T20:50:10+02:00",
          "tree_id": "008b47ff9b87319b14a12a88101f3835e80858c2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5e1cc57677c2ee9b80d9ed27a41321d3cae2d7c3"
        },
        "date": 1657824676988,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0360648962397507,
            "unit": "iter/sec",
            "range": "stddev: 0.005887555483642308",
            "extra": "mean: 965.1905046000081 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.862439922276632,
            "unit": "iter/sec",
            "range": "stddev: 0.004883350595671598",
            "extra": "mean: 77.74574699999854 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2653099397099824,
            "unit": "iter/sec",
            "range": "stddev: 0.013698385087942395",
            "extra": "mean: 3.769176537800007 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "dkg@fifthhorseman.net",
            "name": "dkg",
            "username": "dkg"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bb2d1dbf20dbe6a77d60be46cbd8646fde6b418c",
          "message": "BUG: Avoid IndexError in _cmap.parse_to_unicode (#1110)\n\nThe code within the if block assumes that `lst` has index 0 and index 1.\r\n\r\nFixes #1091\r\nRelated to #1111",
          "timestamp": "2022-07-14T20:57:11+02:00",
          "tree_id": "1f6e758987072f3a2e793f40c246e2dfea43caeb",
          "url": "https://github.com/py-pdf/PyPDF2/commit/bb2d1dbf20dbe6a77d60be46cbd8646fde6b418c"
        },
        "date": 1657825113173,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7876358328323747,
            "unit": "iter/sec",
            "range": "stddev: 0.019815457705392062",
            "extra": "mean: 1.2696222775999844 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.964985044609621,
            "unit": "iter/sec",
            "range": "stddev: 0.007086859656120921",
            "extra": "mean: 100.35137990908797 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2046891864008162,
            "unit": "iter/sec",
            "range": "stddev: 0.050061393739731015",
            "extra": "mean: 4.885455932400015 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "jlshin@users.noreply.github.com",
            "name": "Joanne Shin",
            "username": "jlshin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9bbe827ab534cdbbb6e2687e0a41dda4b269d387",
          "message": "BUG: None-check in DictionaryObject.read_from_stream (#1113)\n\nGuard pdf.strict with check if pdf is None in DictionaryObject.read_from_stream\r\n\r\nCloses #1107",
          "timestamp": "2022-07-15T07:41:59+02:00",
          "tree_id": "9d7f83c7287d3fde8dc334655e8456c4dfbdd230",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9bbe827ab534cdbbb6e2687e0a41dda4b269d387"
        },
        "date": 1657863779535,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0297822044723288,
            "unit": "iter/sec",
            "range": "stddev: 0.0068546757139756114",
            "extra": "mean: 971.0791230000041 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.890984100231147,
            "unit": "iter/sec",
            "range": "stddev: 0.004642750765818542",
            "extra": "mean: 77.57359657142615 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2681369338361097,
            "unit": "iter/sec",
            "range": "stddev: 0.012699612982499702",
            "extra": "mean: 3.729437738000013 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "harry.karvonen@gmail.com",
            "name": "Harry Karvonen",
            "username": "Hatell"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dd2d69a8d89a1370753f1418b3e0df9a7908d928",
          "message": "BUG: Prevent deduplication of PageObject (#1105)\n\nMake sure that PageObject is not deduplicated if it is not exactly same page object.\r\nAdobe Reader/Acrobat doesn't like it if same page is referred more than one time.\r\n\r\nCloses #1102\r\n\r\nCo-authored-by: Harry Karvonen <harry.karvonen@onebyte.fi>",
          "timestamp": "2022-07-16T06:53:39+02:00",
          "tree_id": "f35bde6862ab4d0eff65cfc03d8b21b047aa0620",
          "url": "https://github.com/py-pdf/PyPDF2/commit/dd2d69a8d89a1370753f1418b3e0df9a7908d928"
        },
        "date": 1657947284097,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0291048562174767,
            "unit": "iter/sec",
            "range": "stddev: 0.0071036458656652205",
            "extra": "mean: 971.7182791999903 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.528717531234342,
            "unit": "iter/sec",
            "range": "stddev: 0.006771865300383582",
            "extra": "mean: 79.8166290769171 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2634419608894469,
            "unit": "iter/sec",
            "range": "stddev: 0.020287965559171853",
            "extra": "mean: 3.7959025077999966 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mtd91429@users.noreply.github.com",
            "name": "mtd91429",
            "username": "mtd91429"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ed5ecd9d55cd669045fe47eadef4d049c7959b7d",
          "message": "MAINT: Destination.color returns ArrayObject instead of tuple as fallback (#1119)",
          "timestamp": "2022-07-16T20:14:19+02:00",
          "tree_id": "c0f28b6e661a4b9d34b5aaa59ca74982c0da6626",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ed5ecd9d55cd669045fe47eadef4d049c7959b7d"
        },
        "date": 1657995335678,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8338303045331391,
            "unit": "iter/sec",
            "range": "stddev: 0.008833898300457544",
            "extra": "mean: 1.1992847879999986 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.597719317814308,
            "unit": "iter/sec",
            "range": "stddev: 0.008320518758290056",
            "extra": "mean: 94.35992499999912 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21210706015047634,
            "unit": "iter/sec",
            "range": "stddev: 0.028979365953499033",
            "extra": "mean: 4.714600255599999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5ddf4cb32505cb034496ac4be13747a61fb6ce46",
          "message": "TST: Add MCVE showing outline title issue (#1123)\n\nSee #1121",
          "timestamp": "2022-07-17T09:36:49+02:00",
          "tree_id": "4265a285712229e214a36918c3c06c56bc9dd04e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5ddf4cb32505cb034496ac4be13747a61fb6ce46"
        },
        "date": 1658043471685,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0473415403936719,
            "unit": "iter/sec",
            "range": "stddev: 0.006523724805097256",
            "extra": "mean: 954.7983741999985 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.152208396846627,
            "unit": "iter/sec",
            "range": "stddev: 0.005882755330687307",
            "extra": "mean: 76.0328585000037 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2630152355914438,
            "unit": "iter/sec",
            "range": "stddev: 0.015997462929725766",
            "extra": "mean: 3.8020611154000052 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b1d4ea1fb4364336f84f1f3add19163aab2084a6",
          "message": "TST: Add xfail test for IndexError when extracting text (#1124)\n\nSee #1091",
          "timestamp": "2022-07-17T09:58:31+02:00",
          "tree_id": "8423c822241c9d368a2b911d6a14d8a439f782cc",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b1d4ea1fb4364336f84f1f3add19163aab2084a6"
        },
        "date": 1658044787752,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8795717110052204,
            "unit": "iter/sec",
            "range": "stddev: 0.008923554331270947",
            "extra": "mean: 1.1369169648000024 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.051615537038819,
            "unit": "iter/sec",
            "range": "stddev: 0.007869031555584724",
            "extra": "mean: 90.48450850000715 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22263520216104246,
            "unit": "iter/sec",
            "range": "stddev: 0.038017984879417176",
            "extra": "mean: 4.491652668999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "8a010a5c899be2361ecd7dba29d2438425819ed4",
          "message": "DOC: Explanation for git submodule",
          "timestamp": "2022-07-17T10:00:36+02:00",
          "tree_id": "0f0bf0bff738847badf402da376e219fbd76fbf8",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8a010a5c899be2361ecd7dba29d2438425819ed4"
        },
        "date": 1658044917432,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8032782741304431,
            "unit": "iter/sec",
            "range": "stddev: 0.07455169657511858",
            "extra": "mean: 1.244898601400007 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.689016792694536,
            "unit": "iter/sec",
            "range": "stddev: 0.005394803102884785",
            "extra": "mean: 93.55397408332777 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21130135716563975,
            "unit": "iter/sec",
            "range": "stddev: 0.0704876467000344",
            "extra": "mean: 4.732577269800009 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cd87bbb4083347dc64aafa2571f5ebbe61f445f0",
          "message": "TST: Add xfail for decryption fail (#1125)\n\nSee #1088",
          "timestamp": "2022-07-17T10:13:15+02:00",
          "tree_id": "a9c3c2175df51fe0440bbaed925b97dddedcb035",
          "url": "https://github.com/py-pdf/PyPDF2/commit/cd87bbb4083347dc64aafa2571f5ebbe61f445f0"
        },
        "date": 1658045657682,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0464141677386083,
            "unit": "iter/sec",
            "range": "stddev: 0.010046435565147864",
            "extra": "mean: 955.6445534000047 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.170096026246021,
            "unit": "iter/sec",
            "range": "stddev: 0.0053375530845930575",
            "extra": "mean: 75.92959064285866 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26735655025789623,
            "unit": "iter/sec",
            "range": "stddev: 0.00848971993714356",
            "extra": "mean: 3.7403235456000035 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "baeb7d23278de0f8d00ca9f2b656bf0674f08937",
          "message": "STY: Apply black and isort",
          "timestamp": "2022-07-17T10:16:36+02:00",
          "tree_id": "6c7e3d41a127b3f2118bf3860d30bccb1ad05e29",
          "url": "https://github.com/py-pdf/PyPDF2/commit/baeb7d23278de0f8d00ca9f2b656bf0674f08937"
        },
        "date": 1658045874186,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9144163236193118,
            "unit": "iter/sec",
            "range": "stddev: 0.008799021195886917",
            "extra": "mean: 1.0935937758000023 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.13432318518005,
            "unit": "iter/sec",
            "range": "stddev: 0.005712366095135803",
            "extra": "mean: 89.81237416666825 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23812457046125562,
            "unit": "iter/sec",
            "range": "stddev: 0.08659099363942872",
            "extra": "mean: 4.199482640800002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "dkg@fifthhorseman.net",
            "name": "dkg",
            "username": "dkg"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ae0ff49058e6c57a8edcfcd3d956665ddaa8a787",
          "message": "BUG: Avoid a crash when a ToUnicode CMap has an empty dstString in beginbfchar (#1118)\n\nThis is not a principled fix, but it is a hack to avoid a crash when\r\nencountering an empty dstString in a `beginbfchar` table in a\r\nToUnicode CMap.\r\n\r\nWe take narrow aim at the issue of zero-length (empty) hex\r\nstring representations.\r\n\r\nWe take advantage of the fact that no angle-bracket-delimited hex\r\nstring contains a . character.  when we encounter an empty hex string,\r\nrather than replacing it with the empty string, we replace it with a\r\nliteral \".\".  Then, when we encounter a \".\", we remember that it was\r\nsupposed to be an empty string.\r\n\r\nOne consequence of this fix is that the exported cmap can now return\r\nan empty string, so we also have to clean up\r\n`PageObject::process_operation` so that it doesn't try to read the\r\nfinal character from an empty string.\r\n\r\nCloses #1111",
          "timestamp": "2022-07-17T14:14:10+02:00",
          "tree_id": "3da253fd5a9c122d03179fb67dcd3317eea5c0dd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ae0ff49058e6c57a8edcfcd3d956665ddaa8a787"
        },
        "date": 1658060113156,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1783886200608842,
            "unit": "iter/sec",
            "range": "stddev: 0.005444331459133562",
            "extra": "mean: 848.6164776000066 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.767755325067798,
            "unit": "iter/sec",
            "range": "stddev: 0.006068474692919121",
            "extra": "mean: 67.71509806250187 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2969403924377845,
            "unit": "iter/sec",
            "range": "stddev: 0.019202664714317568",
            "extra": "mean: 3.3676792563999927 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0b693e1122d568f29f266340121915b3813eb8c2",
          "message": "TST: Add test for arab text (#1127)",
          "timestamp": "2022-07-17T20:41:45+02:00",
          "tree_id": "81b9287586f0ea59604fa581b6db2c1b1fa5eaac",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0b693e1122d568f29f266340121915b3813eb8c2"
        },
        "date": 1658083375360,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8711878951465271,
            "unit": "iter/sec",
            "range": "stddev: 0.011247861746166665",
            "extra": "mean: 1.1478580058000092 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.952956264232837,
            "unit": "iter/sec",
            "range": "stddev: 0.008813528513059077",
            "extra": "mean: 91.29955199999529 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21958835334165433,
            "unit": "iter/sec",
            "range": "stddev: 0.03255510766917822",
            "extra": "mean: 4.5539755856 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e24b0a046635995c08c91ccf9d6900560d7fb390",
          "message": "MAINT: Text extraction improvements (#1126)\n\nCredits to pubpub-zz, see\r\nhttps://github.com/py-pdf/PyPDF2/pull/1118#issuecomment-1186148575\r\n\r\nCo-authored-by: pubpub-zz <4083478+pubpub-zz@users.noreply.github.com>",
          "timestamp": "2022-07-17T20:53:18+02:00",
          "tree_id": "64671b1863424f02f7824dfe93b5c82266482d1c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e24b0a046635995c08c91ccf9d6900560d7fb390"
        },
        "date": 1658084060549,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0262185993617878,
            "unit": "iter/sec",
            "range": "stddev: 0.008474045287202959",
            "extra": "mean: 974.4512530000009 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.009941850940857,
            "unit": "iter/sec",
            "range": "stddev: 0.0061688519951541235",
            "extra": "mean: 76.86429435714055 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26243625848034563,
            "unit": "iter/sec",
            "range": "stddev: 0.028449458487934356",
            "extra": "mean: 3.810449081200005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mtd91429@users.noreply.github.com",
            "name": "mtd91429",
            "username": "mtd91429"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7fba86b65e25809367ff169e779dbccb517e1b25",
          "message": "BUG: Use `build_destination` for named destination outlines (#1128)\n\nCloses #1121",
          "timestamp": "2022-07-17T21:04:58+02:00",
          "tree_id": "3bce533bed49a6d5c2b859775ca06217730530b0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7fba86b65e25809367ff169e779dbccb517e1b25"
        },
        "date": 1658084776550,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7905968772881199,
            "unit": "iter/sec",
            "range": "stddev: 0.04227312329487738",
            "extra": "mean: 1.2648671260000015 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.075012045890803,
            "unit": "iter/sec",
            "range": "stddev: 0.005759740950072237",
            "extra": "mean: 99.25546445454229 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21190527373531154,
            "unit": "iter/sec",
            "range": "stddev: 0.08780883134982091",
            "extra": "mean: 4.71908972519999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "1800514a7e066c3a042b7d5ed93960b34c7fac2f",
          "message": "TST: Remove xfail from test_outline_title_issue_1121",
          "timestamp": "2022-07-17T21:05:42+02:00",
          "tree_id": "109b072bfc5335e7da9a18acfb4543c42d6ac4c7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1800514a7e066c3a042b7d5ed93960b34c7fac2f"
        },
        "date": 1658084808894,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0510647686456955,
            "unit": "iter/sec",
            "range": "stddev: 0.00674003346608484",
            "extra": "mean: 951.4161541999997 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.108113546456766,
            "unit": "iter/sec",
            "range": "stddev: 0.007022864826012699",
            "extra": "mean: 76.28862814285802 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26495497451209293,
            "unit": "iter/sec",
            "range": "stddev: 0.017662484147484774",
            "extra": "mean: 3.774226175000004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "33634d40ffce9351f96fb35f491c2b3fe98b2406",
          "message": "REL: 2.6.0\n\nNew Features (ENH):\n-  Add color and font_format to PdfReader.outlines[i] (#1104)\n-  Extract Text Enhancement (whitespaces) (#1084)\n\nBug Fixes (BUG):\n-  Use `build_destination` for named destination outlines (#1128)\n-  Avoid a crash when a ToUnicode CMap has an empty dstString in beginbfchar (#1118)\n-  Prevent deduplication of PageObject (#1105)\n-  None-check in DictionaryObject.read_from_stream (#1113)\n-  Avoid IndexError in _cmap.parse_to_unicode (#1110)\n\nDocumentation (DOC):\n-  Explanation for git submodule\n-  Watermark and stamp (#1095)\n\nMaintenance (MAINT):\n-  Text extraction improvements (#1126)\n-  Destination.color returns ArrayObject instead of tuple as fallback (#1119)\n-  Use add_bookmark_destination in add_bookmark (#1100)\n-  Use add_bookmark_destination in add_bookmark_dict (#1099)\n\nTesting (TST):\n-  Remove xfail from test_outline_title_issue_1121\n-  Add test for arab text (#1127)\n-  Add xfail for decryption fail (#1125)\n-  Add xfail test for IndexError when extracting text (#1124)\n-  Add MCVE showing outline title issue (#1123)\n\nCode Style (STY):\n-  Apply black and isort\n-  Use IntFlag for permissions_flag / update_page_form_field_values (#1094)\n-  Simplify code (#1101)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.5.0...2.6.0",
          "timestamp": "2022-07-17T21:17:03+02:00",
          "tree_id": "8f8b7e691906f7eb569b24fb6d7cea64c58f0e1c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/33634d40ffce9351f96fb35f491c2b3fe98b2406"
        },
        "date": 1658085489432,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.049645300280839,
            "unit": "iter/sec",
            "range": "stddev: 0.0075047709437715115",
            "extra": "mean: 952.7027841999995 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.129986949580701,
            "unit": "iter/sec",
            "range": "stddev: 0.005521591952281133",
            "extra": "mean: 76.1615380000004 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26549255757661444,
            "unit": "iter/sec",
            "range": "stddev: 0.031049336278416446",
            "extra": "mean: 3.7665839265999965 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mtd91429@users.noreply.github.com",
            "name": "mtd91429",
            "username": "mtd91429"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "25cba33f88c6708ebc50169808f02b80e96fb0ab",
          "message": "ENH: Add `outline_count` property (#1129)\n\nEnables retrieval of \"/Count\" attribute of outline item in PdfReader.outlines by implementing property outline_count.\r\n\r\nCloses #1122",
          "timestamp": "2022-07-18T07:45:36+02:00",
          "tree_id": "675069f3197a523cc4dd897dd7627d350ffd16fc",
          "url": "https://github.com/py-pdf/PyPDF2/commit/25cba33f88c6708ebc50169808f02b80e96fb0ab"
        },
        "date": 1658123227051,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.791820744082733,
            "unit": "iter/sec",
            "range": "stddev: 0.018431316882015103",
            "extra": "mean: 1.2629121016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.208826618872974,
            "unit": "iter/sec",
            "range": "stddev: 0.00814933017028937",
            "extra": "mean: 97.95445033333294 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20813095733572187,
            "unit": "iter/sec",
            "range": "stddev: 0.0167676422578944",
            "extra": "mean: 4.804667276800001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "df95aae5215c7dcf7bfb14504b153427bbf8f44a",
          "message": "STY: Re-use code via get_outlines_property in tests (#1130)",
          "timestamp": "2022-07-18T07:56:53+02:00",
          "tree_id": "96ec8049a0619c0b2c766ab0b67bce5676aa7a63",
          "url": "https://github.com/py-pdf/PyPDF2/commit/df95aae5215c7dcf7bfb14504b153427bbf8f44a"
        },
        "date": 1658123875856,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0432245397351165,
            "unit": "iter/sec",
            "range": "stddev: 0.008178004344528672",
            "extra": "mean: 958.5664082000108 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.012240498456364,
            "unit": "iter/sec",
            "range": "stddev: 0.0067863186403710135",
            "extra": "mean: 76.85071607142747 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26116145147791925,
            "unit": "iter/sec",
            "range": "stddev: 0.024493586094480612",
            "extra": "mean: 3.829049020599996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f2983e142f504d1fde7874af78975431e287043b",
          "message": "DOC: Fix type in signature of PdfWriter.add_uri (#1131)",
          "timestamp": "2022-07-18T08:53:13+02:00",
          "tree_id": "27f4e984c8cef3695ef21c2ba8fc3192578f323a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f2983e142f504d1fde7874af78975431e287043b"
        },
        "date": 1658127287232,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0520343233368676,
            "unit": "iter/sec",
            "range": "stddev: 0.0041459235668808775",
            "extra": "mean: 950.539329199998 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.99488524751043,
            "unit": "iter/sec",
            "range": "stddev: 0.004322561202045019",
            "extra": "mean: 76.95335364285582 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27021007157059634,
            "unit": "iter/sec",
            "range": "stddev: 0.016566891658991",
            "extra": "mean: 3.700824303799999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c63a0ff24965bdbe9339ca5d837b5460f93c3c13",
          "message": "DOC: Contributors file (#1132)\n\nWe value the work of our contributors - of all of them. The CONTRIBUTORS file might give them more visibility and be more robust when the project is vendored into other projects.\r\n\r\nIt is by far not complete - I hope that people add themselves in PRs :-) \r\n\r\nSee #798",
          "timestamp": "2022-07-20T22:54:06+02:00",
          "tree_id": "4a796e854aeeaf63d058737ea9e4c8840a8adc33",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c63a0ff24965bdbe9339ca5d837b5460f93c3c13"
        },
        "date": 1658350513756,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0612077280848211,
            "unit": "iter/sec",
            "range": "stddev: 0.005518801364676714",
            "extra": "mean: 942.3225760000037 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.258551595532452,
            "unit": "iter/sec",
            "range": "stddev: 0.0046758783943127566",
            "extra": "mean: 81.57570592307522 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27165791803443434,
            "unit": "iter/sec",
            "range": "stddev: 0.014166988155820145",
            "extra": "mean: 3.6811001395999936 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "tim.gates@iress.com",
            "name": "Tim Gates",
            "username": "timgates42"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d41201b9f76fd93484f259e359877d9b87e1d201",
          "message": "STY: Fixing typos (#1137)\n\nThere were typos in:\r\n- docs/meta/project-governance.md\r\n- tests/test_reader.py\r\n- tests/test_writer.py\r\n\r\nFixes:\r\n- Should read `inducing` rather than `indiducing`.\r\n- Should read `decisions` rather than `decisons`.\r\n\r\nSigned-off-by: Tim Gates <tim.gates@iress.com>",
          "timestamp": "2022-07-20T22:54:58+02:00",
          "tree_id": "20c05c6ed7777e2eb7246f12873abdf57401dd51",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d41201b9f76fd93484f259e359877d9b87e1d201"
        },
        "date": 1658350566848,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0584495422797122,
            "unit": "iter/sec",
            "range": "stddev: 0.012902924704329783",
            "extra": "mean: 944.7781496000061 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.22202586336415,
            "unit": "iter/sec",
            "range": "stddev: 0.004792635076554576",
            "extra": "mean: 81.8194963076888 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2705726481189021,
            "unit": "iter/sec",
            "range": "stddev: 0.011946226159717214",
            "extra": "mean: 3.695865073400006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2abae354f4ce8e1cf44f90eba8a89da5f275dd03",
          "message": "ROB: Cope with invalid parent xref (#1133)\n\nRebuild the xref table if the parent chained xref is invalid\r\n\r\nCloses #1089",
          "timestamp": "2022-07-20T23:05:03+02:00",
          "tree_id": "63bc744618691d0186c2cace0569481ba687c0e6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2abae354f4ce8e1cf44f90eba8a89da5f275dd03"
        },
        "date": 1658351168258,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.052918574625751,
            "unit": "iter/sec",
            "range": "stddev: 0.008087750563953543",
            "extra": "mean: 949.7410570000056 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.39700570048084,
            "unit": "iter/sec",
            "range": "stddev: 0.005286807845390452",
            "extra": "mean: 80.6646398461536 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27131232219369605,
            "unit": "iter/sec",
            "range": "stddev: 0.01122033816115988",
            "extra": "mean: 3.6857891005999988 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fd00f205f0ba34290cc61e2594e55c21f4c99c23",
          "message": "ROB: Cope with missing /W entry (#1136)\n\nCloses #1134",
          "timestamp": "2022-07-20T23:08:31+02:00",
          "tree_id": "f1d30606bfc981931ed3c7ff02aa1299391ad075",
          "url": "https://github.com/py-pdf/PyPDF2/commit/fd00f205f0ba34290cc61e2594e55c21f4c99c23"
        },
        "date": 1658351379285,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0469899895494643,
            "unit": "iter/sec",
            "range": "stddev: 0.0075504236224868924",
            "extra": "mean: 955.1189696000008 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.321069203581754,
            "unit": "iter/sec",
            "range": "stddev: 0.004981099320817892",
            "extra": "mean: 81.16178746153771 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2708219699910275,
            "unit": "iter/sec",
            "range": "stddev: 0.010728867243752703",
            "extra": "mean: 3.692462616799999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "c667ae4355507cccde493f000238bb1724159f15",
          "message": "DOC: Recognize Lightup1 as a contributor",
          "timestamp": "2022-07-21T08:17:31+02:00",
          "tree_id": "dd17b605e0547f5b535e01a9bd631727a023f3fd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c667ae4355507cccde493f000238bb1724159f15"
        },
        "date": 1658384322320,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0543950606797508,
            "unit": "iter/sec",
            "range": "stddev: 0.00835982998412014",
            "extra": "mean: 948.4111196000072 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.269625499819403,
            "unit": "iter/sec",
            "range": "stddev: 0.006557823728018607",
            "extra": "mean: 81.5020800769118 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2675409440982168,
            "unit": "iter/sec",
            "range": "stddev: 0.025168821179455975",
            "extra": "mean: 3.737745649999988 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fa96d66f6a82321ed13f2410754309f4c4c1db1c",
          "message": "DEV: Add .git-blame-ignore-revs (#1141)\n\nSee https://docs.github.com/en/repositories/working-with-files/using-files/viewing-a-file#ignore-commits-in-the-blame-view",
          "timestamp": "2022-07-21T08:19:28+02:00",
          "tree_id": "ea1633f8baf144620b2dde8850f26286df6800aa",
          "url": "https://github.com/py-pdf/PyPDF2/commit/fa96d66f6a82321ed13f2410754309f4c4c1db1c"
        },
        "date": 1658384425149,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1753790372310273,
            "unit": "iter/sec",
            "range": "stddev: 0.013793510034000976",
            "extra": "mean: 850.789377999979 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.998161401222049,
            "unit": "iter/sec",
            "range": "stddev: 0.005985472840893236",
            "extra": "mean: 71.43795326668396 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.3026753744029591,
            "unit": "iter/sec",
            "range": "stddev: 0.08469432525084206",
            "extra": "mean: 3.303869705199986 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e1f9772693b788deae6b0fcdcb5ff49577706549",
          "message": "BUG: Add deprecated EncodedStreamObject functions back until PyPDF2==3.0.0 (#1139)\n\nAccidentally, PyPDF2 did not follow the deprecation process:\r\nhttps://pypdf2.readthedocs.io/en/latest/dev/deprecations.html\r\n\r\nISSUE: The EncodedStreamObject.getData / setData were removed\r\nAFFECTS: PyPDF2>=1.28.3,<=2.6.0\r\nFIX: Add the getData / setData methods back with deprecation warnings\r\n\r\nCloses #1138",
          "timestamp": "2022-07-21T18:12:15+02:00",
          "tree_id": "c7e95639a866503b18bd2db13508a853184200cd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e1f9772693b788deae6b0fcdcb5ff49577706549"
        },
        "date": 1658420005839,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0455819351367865,
            "unit": "iter/sec",
            "range": "stddev: 0.011089372748378153",
            "extra": "mean: 956.4052001999983 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.235745291320878,
            "unit": "iter/sec",
            "range": "stddev: 0.005902954999637591",
            "extra": "mean: 81.72775553846525 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2685975306553702,
            "unit": "iter/sec",
            "range": "stddev: 0.007212211107266255",
            "extra": "mean: 3.7230424180000057 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "j4c0bh3rrm4nn@gmail.com",
            "name": "KourFrost",
            "username": "KourFrost"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7cba98a57789c4058898b47875d2dda0a48d6bb5",
          "message": "BUG: Make reader.get_fields also return dropdowns with options (#1114)\n\nAdded /Opt to the checked field_attributes within reader.get_fields\r\n\r\nCloses #391",
          "timestamp": "2022-07-21T18:31:44+02:00",
          "tree_id": "097cdc34059f595a34dc6d2b434febda0bebc3cb",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7cba98a57789c4058898b47875d2dda0a48d6bb5"
        },
        "date": 1658421165741,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0404229678102017,
            "unit": "iter/sec",
            "range": "stddev: 0.0044982655612011355",
            "extra": "mean: 961.1475629999973 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.17814333458148,
            "unit": "iter/sec",
            "range": "stddev: 0.006523894539040963",
            "extra": "mean: 82.11432338461358 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26695582451658223,
            "unit": "iter/sec",
            "range": "stddev: 0.009123891115513599",
            "extra": "mean: 3.7459381222000045 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0f520528b881688e7324ee5aab3c379dac678e1f",
          "message": "STY: Variable naming / opening PDF with PdfReader (#1144)",
          "timestamp": "2022-07-21T18:53:15+02:00",
          "tree_id": "6d5405e51617a97e341a3bac1ab4970eb2441d7c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0f520528b881688e7324ee5aab3c379dac678e1f"
        },
        "date": 1658422463653,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9211263296360976,
            "unit": "iter/sec",
            "range": "stddev: 0.00985425999628602",
            "extra": "mean: 1.0856274191999944 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.865024098974253,
            "unit": "iter/sec",
            "range": "stddev: 0.007481799107634444",
            "extra": "mean: 92.03845209090775 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2399999405376148,
            "unit": "iter/sec",
            "range": "stddev: 0.08863718826884263",
            "extra": "mean: 4.166667698999999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "6899c7448ee6d3546b4e3afa60754bd595556ead",
          "message": "REL: 2.7.0\n\nNew Features (ENH):\n-  Add `outline_count` property (#1129)\n\nBug Fixes (BUG):\n-  Make reader.get_fields also return dropdowns with options (#1114)\n-  Add deprecated EncodedStreamObject functions back until PyPDF2==3.0.0 (#1139)\n\nRobustness (ROB):\n-  Cope with missing /W entry (#1136)\n-  Cope with invalid parent xref (#1133)\n\nDocumentation (DOC):\n-  Contributors file (#1132)\n-  Fix type in signature of PdfWriter.add_uri (#1131)\n\nDeveloper Experience (DEV):\n-  Add .git-blame-ignore-revs (#1141)\n\nCode Style (STY):\n-  Fixing typos (#1137)\n-  Re-use code via get_outlines_property in tests (#1130)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.6.0...2.7.0",
          "timestamp": "2022-07-21T19:03:11+02:00",
          "tree_id": "bb3c8bba93828e4f5504757b157d15a35a18f295",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6899c7448ee6d3546b4e3afa60754bd595556ead"
        },
        "date": 1658423128254,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.6644086089855754,
            "unit": "iter/sec",
            "range": "stddev: 0.8352411072064482",
            "extra": "mean: 1.5050978967999953 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 4.173459058231012,
            "unit": "iter/sec",
            "range": "stddev: 0.0023414165503309018",
            "extra": "mean: 239.60939499999938 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.09085221938711806,
            "unit": "iter/sec",
            "range": "stddev: 0.08896515118510831",
            "extra": "mean: 11.006885761800003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "6899c7448ee6d3546b4e3afa60754bd595556ead",
          "message": "REL: 2.7.0\n\nNew Features (ENH):\n-  Add `outline_count` property (#1129)\n\nBug Fixes (BUG):\n-  Make reader.get_fields also return dropdowns with options (#1114)\n-  Add deprecated EncodedStreamObject functions back until PyPDF2==3.0.0 (#1139)\n\nRobustness (ROB):\n-  Cope with missing /W entry (#1136)\n-  Cope with invalid parent xref (#1133)\n\nDocumentation (DOC):\n-  Contributors file (#1132)\n-  Fix type in signature of PdfWriter.add_uri (#1131)\n\nDeveloper Experience (DEV):\n-  Add .git-blame-ignore-revs (#1141)\n\nCode Style (STY):\n-  Fixing typos (#1137)\n-  Re-use code via get_outlines_property in tests (#1130)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.6.0...2.7.0",
          "timestamp": "2022-07-21T19:03:11+02:00",
          "tree_id": "bb3c8bba93828e4f5504757b157d15a35a18f295",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6899c7448ee6d3546b4e3afa60754bd595556ead"
        },
        "date": 1658423228164,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0622521746025002,
            "unit": "iter/sec",
            "range": "stddev: 0.007922873952649866",
            "extra": "mean: 941.3960487999987 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.159882156449015,
            "unit": "iter/sec",
            "range": "stddev: 0.004214308642453213",
            "extra": "mean: 82.23763907692543 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27242552177198925,
            "unit": "iter/sec",
            "range": "stddev: 0.01275817258528066",
            "extra": "mean: 3.6707280341999877 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "91357f047b697345cba9eb736b7e22862d9bcdaa",
          "message": "DOC: Recognize KourFrost as a contributor",
          "timestamp": "2022-07-22T07:41:11+02:00",
          "tree_id": "1486168d71fbf2ce6e7c95c1e0eb76011613eb6f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/91357f047b697345cba9eb736b7e22862d9bcdaa"
        },
        "date": 1658468540485,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0515562338549123,
            "unit": "iter/sec",
            "range": "stddev: 0.008238510654214387",
            "extra": "mean: 950.9714914000256 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.257217301527719,
            "unit": "iter/sec",
            "range": "stddev: 0.0062637754931676145",
            "extra": "mean: 81.5845860769199 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2674599031702353,
            "unit": "iter/sec",
            "range": "stddev: 0.01498053624153225",
            "extra": "mean: 3.738878194999984 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1a65a4663cdd05e09d005a425ba674b0238fe0a0",
          "message": "ENH: Add writer.add_annotation, page.annotations, and generic.AnnotationBuilder (#1120)\n\n* Add `page.annotations` (getter and setter)\r\n* Add `writer.add_annotation(page_number, annotation_dictionary)`\r\n* Add AnnotationBuilder to generate the `annotation_dictionary` for the different subtypes of annotations. Similarly, we could have an AnnotationsParser.\r\n\r\nSee #107\r\n\r\nCloses #981",
          "timestamp": "2022-07-22T18:34:35+02:00",
          "tree_id": "327fe8c087ce13a89782bd362c17438e5159c516",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1a65a4663cdd05e09d005a425ba674b0238fe0a0"
        },
        "date": 1658507737626,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0555700475119205,
            "unit": "iter/sec",
            "range": "stddev: 0.006355115240418405",
            "extra": "mean: 947.3554146000026 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.269059041570799,
            "unit": "iter/sec",
            "range": "stddev: 0.005830062953548805",
            "extra": "mean: 81.505843 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26919006397413214,
            "unit": "iter/sec",
            "range": "stddev: 0.027940308210069778",
            "extra": "mean: 3.7148473655999994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "aaac604bce06519906f834b4e5b0d5edd6ae4924",
          "message": "TST: Test CryptRC4 encryption class; test image extraction filters (#1147)",
          "timestamp": "2022-07-22T20:24:33+02:00",
          "tree_id": "239969255e6e9c5abfac6e024166785739a3905a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/aaac604bce06519906f834b4e5b0d5edd6ae4924"
        },
        "date": 1658514338694,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.054967256019145,
            "unit": "iter/sec",
            "range": "stddev: 0.0074270191738517516",
            "extra": "mean: 947.8967183999998 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.274950224581255,
            "unit": "iter/sec",
            "range": "stddev: 0.00625585159293243",
            "extra": "mean: 81.46672546153756 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2685618945931708,
            "unit": "iter/sec",
            "range": "stddev: 0.018636486308825393",
            "extra": "mean: 3.7235364366 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f233c1ad5adebe405e1184afa73442c92491aa8f",
          "message": "TST: Decrypt file which is not encrypted (#1149)",
          "timestamp": "2022-07-22T23:37:53+02:00",
          "tree_id": "25eff3cbb21e36d7149c62c07ba109569fcc5413",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f233c1ad5adebe405e1184afa73442c92491aa8f"
        },
        "date": 1658525938789,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0515267475418226,
            "unit": "iter/sec",
            "range": "stddev: 0.009708495693387878",
            "extra": "mean: 950.9981579999959 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.343637705239221,
            "unit": "iter/sec",
            "range": "stddev: 0.0053759792817521185",
            "extra": "mean: 81.01339523077164 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26719548180922115,
            "unit": "iter/sec",
            "range": "stddev: 0.030585110944694214",
            "extra": "mean: 3.7425782548 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mtd91429@users.noreply.github.com",
            "name": "mtd91429",
            "username": "mtd91429"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "89c0ff2e95f76960ffa7958e956270d41d3fea79",
          "message": "ROB: Handle outlines without valid destination (#1076)\n\nAdjust `PdfReader._build_outline(...)` and `PdfReader._build_destination(...)` to handle outline items with and without valid destinations\r\n\r\nCloses #193 : PdfReadError: Unexpected destination '/__WKANCHOR_2'\r\nCloses #956 : ValueError: Unresolved bookmark\r\n\r\n#1059 no longer throws an exception, but the outlines are not extracted either.\r\n\r\nCloses #1068 : Skip NameObject when building outline",
          "timestamp": "2022-07-23T08:21:12+02:00",
          "tree_id": "c12163130cd57fc3f0b19a9e0fcf77a03ea53c3b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/89c0ff2e95f76960ffa7958e956270d41d3fea79"
        },
        "date": 1658557344322,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9137757277601906,
            "unit": "iter/sec",
            "range": "stddev: 0.008605869575894995",
            "extra": "mean: 1.0943604317999984 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.740298361231524,
            "unit": "iter/sec",
            "range": "stddev: 0.007111796066819849",
            "extra": "mean: 93.10728309090811 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23514327285023232,
            "unit": "iter/sec",
            "range": "stddev: 0.009329513540225797",
            "extra": "mean: 4.2527263819999686 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a6d27d754776fe1501ccffed26f0e5becf3d2faa",
          "message": "MAINT: Reduce PdfReader.read complexity (#1151)",
          "timestamp": "2022-07-23T10:00:07+02:00",
          "tree_id": "6cec162f6539533737bc11d44e66eb54577b58ef",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a6d27d754776fe1501ccffed26f0e5becf3d2faa"
        },
        "date": 1658563285088,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8806508696834627,
            "unit": "iter/sec",
            "range": "stddev: 0.01058624684947752",
            "extra": "mean: 1.1355237750000016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.191441739578694,
            "unit": "iter/sec",
            "range": "stddev: 0.007834459537219469",
            "extra": "mean: 98.12154409090888 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2247520796073603,
            "unit": "iter/sec",
            "range": "stddev: 0.022519079174650174",
            "extra": "mean: 4.449347039399993 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "27702c2e098fcf62b37d34ee52cfeeb6c3cc4f12",
          "message": "ROB: Cope with null params for FitH /FitV destination (#1152)\n\niaw PDF specifications, page 583\r\n\r\nCloses #1145",
          "timestamp": "2022-07-23T16:34:28+02:00",
          "tree_id": "57c3a8c6cf476d4f2c58cd8d358f184ffd2d1b43",
          "url": "https://github.com/py-pdf/PyPDF2/commit/27702c2e098fcf62b37d34ee52cfeeb6c3cc4f12"
        },
        "date": 1658586927635,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0592912684441653,
            "unit": "iter/sec",
            "range": "stddev: 0.007315416636626577",
            "extra": "mean: 944.0274170000009 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.451894798365847,
            "unit": "iter/sec",
            "range": "stddev: 0.004598691486666011",
            "extra": "mean: 80.30906269230907 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26655999741647496,
            "unit": "iter/sec",
            "range": "stddev: 0.014119233750709323",
            "extra": "mean: 3.7515006365999994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b429b395316021ff97ab41b9626287adb221f6fe",
          "message": "DEV: Introduce _utils.logger_warning (#1148)\n\n- Exceptions: User code should handle the issue\r\n- warnings.warn: User should re-write something, e.g. deprecations\r\n- _utils.logger_warning: User might want to know in case of errors / post mortem analysis (or for developing PyPDF2 itself)",
          "timestamp": "2022-07-24T07:21:45+02:00",
          "tree_id": "6b6e04b53068c5b6b011678ac350b5fee0ff4f26",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b429b395316021ff97ab41b9626287adb221f6fe"
        },
        "date": 1658640187628,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8893118391174807,
            "unit": "iter/sec",
            "range": "stddev: 0.037962210275045906",
            "extra": "mean: 1.1244649581999966 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.582198160252936,
            "unit": "iter/sec",
            "range": "stddev: 0.005161624958010947",
            "extra": "mean: 94.49832490909412 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22734933739596463,
            "unit": "iter/sec",
            "range": "stddev: 0.06454507003077448",
            "extra": "mean: 4.398517327800005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c52988489fa5d1b83e327bbeba02a7eca2e211bb",
          "message": "TST: Add workflow tests found by arc testing (#1154)\n\nDone with https://github.com/py-pdf/pdf-crawler/blob/main/get_coverage_by_pdf.py",
          "timestamp": "2022-07-24T07:26:48+02:00",
          "tree_id": "3c188a77922002ae24d978a2b43d3b086faa4b8e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c52988489fa5d1b83e327bbeba02a7eca2e211bb"
        },
        "date": 1658640478191,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9309114818418303,
            "unit": "iter/sec",
            "range": "stddev: 0.010324034729472605",
            "extra": "mean: 1.0742159909999998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.860639365514578,
            "unit": "iter/sec",
            "range": "stddev: 0.007535369392613841",
            "extra": "mean: 92.07561049999195 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23519172537438499,
            "unit": "iter/sec",
            "range": "stddev: 0.03520633305970928",
            "extra": "mean: 4.2518502655999955 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "102260d8d5d21559371f7154ec647db5ce659dc2",
          "message": "MAINT: Add diagnostic output to exception in read_from_stream (#1159)\n\nCo-authored-by: speedplane <mes65@cornell.edu>",
          "timestamp": "2022-07-24T08:21:49+02:00",
          "tree_id": "31b7a520c6c779668cad4ade444e374c748daedc",
          "url": "https://github.com/py-pdf/PyPDF2/commit/102260d8d5d21559371f7154ec647db5ce659dc2"
        },
        "date": 1658643790822,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8477372503769978,
            "unit": "iter/sec",
            "range": "stddev: 0.009419933420346183",
            "extra": "mean: 1.1796107809999967 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.703609099853143,
            "unit": "iter/sec",
            "range": "stddev: 0.006542810520033091",
            "extra": "mean: 103.05443981818416 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21664344304417912,
            "unit": "iter/sec",
            "range": "stddev: 0.03308381427900485",
            "extra": "mean: 4.615879372800009 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "exiledkingcc@gmail.com",
            "name": "exiledkingcc",
            "username": "exiledkingcc"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2bf40f4a70a35434086eab2054d11425380b919c",
          "message": "BUG: Ignore if '/Perms' verify failed (#1157)\n\nIt seems to be save to ignore the /Perms entry:\r\n\r\nQpdf ignores it:\r\nhttps://github.com/qpdf/qpdf/blob/main/libqpdf/QPDF_encryption.cc#L1064\r\n\r\npdfbox ignores it:\r\nhttps://github.com/apache/pdfbox/blob/dc1a75027d5bebf95a3330f6298a533e78e0b99e/pdfbox/src/main/java/org/apache/pdfbox/pdmodel/encryption/StandardSecurityHandler.java#L311\r\n\r\nCloses #378",
          "timestamp": "2022-07-24T08:26:50+02:00",
          "tree_id": "23cea4cac48140defb8a9d6abd3f7baea9ba499d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2bf40f4a70a35434086eab2054d11425380b919c"
        },
        "date": 1658644071100,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0609824723666696,
            "unit": "iter/sec",
            "range": "stddev: 0.006591941236200268",
            "extra": "mean: 942.5226392000241 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.293976048102211,
            "unit": "iter/sec",
            "range": "stddev: 0.005641008316898288",
            "extra": "mean: 81.34064976923128 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26909782747276006,
            "unit": "iter/sec",
            "range": "stddev: 0.011094370329913793",
            "extra": "mean: 3.716120673999967 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "35bec4034e503cac97c23de9f923154785d48767",
          "message": "ROB: Cope with utf16 character for space calculation (#1155)\n\nSee #1143\r\n\r\nCo-authored-by: Martin Thoma <info@martin-thoma.de>",
          "timestamp": "2022-07-24T08:28:50+02:00",
          "tree_id": "734adbadd0c44c8db659ec28c7a85808f18e3047",
          "url": "https://github.com/py-pdf/PyPDF2/commit/35bec4034e503cac97c23de9f923154785d48767"
        },
        "date": 1658644211981,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8821578955468429,
            "unit": "iter/sec",
            "range": "stddev: 0.022878981461502336",
            "extra": "mean: 1.1335839140000075 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.805938436915897,
            "unit": "iter/sec",
            "range": "stddev: 0.007955383512216935",
            "extra": "mean: 101.97902081817615 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2226384273964435,
            "unit": "iter/sec",
            "range": "stddev: 0.08989962279164848",
            "extra": "mean: 4.4915876009999804 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fa5e3f76da2048b50c9d1dd94d7a938a11ac53e8",
          "message": "BUG: Set /AS for /Btn form fields in writer (#1161)\n\nCloses #434\r\n\r\nCo-authored-by: liuzhuoling <liuzhuoling@mycapital.net>",
          "timestamp": "2022-07-24T10:01:55+02:00",
          "tree_id": "3415c1773510211fbcd8d90de2ddd636cee28c2b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/fa5e3f76da2048b50c9d1dd94d7a938a11ac53e8"
        },
        "date": 1658649785248,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9017165730790321,
            "unit": "iter/sec",
            "range": "stddev: 0.011343821025849481",
            "extra": "mean: 1.1089959194000016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.460030018707617,
            "unit": "iter/sec",
            "range": "stddev: 0.00899577327067763",
            "extra": "mean: 95.6020200909093 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23230634885298665,
            "unit": "iter/sec",
            "range": "stddev: 0.037344257841753124",
            "extra": "mean: 4.304660655799995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2de09730c13e3e380f0038d241e5ee81b0509a40",
          "message": "MAINT: Break up parse_to_unicode (#1162)\n\nJust move parts in separate functions for easier readability",
          "timestamp": "2022-07-24T11:19:38+02:00",
          "tree_id": "8160317deafe1e8b4f48e7afcc93fbf5ab8f3d26",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2de09730c13e3e380f0038d241e5ee81b0509a40"
        },
        "date": 1658654442640,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9880444212227384,
            "unit": "iter/sec",
            "range": "stddev: 0.03738436161627342",
            "extra": "mean: 1.012100244200019 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.799681534671311,
            "unit": "iter/sec",
            "range": "stddev: 0.00861358717725552",
            "extra": "mean: 92.59532299999762 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26232882077697,
            "unit": "iter/sec",
            "range": "stddev: 0.029886540448272887",
            "extra": "mean: 3.8120096642000023 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "ec30171a9da60755763ed8b2c24c96298f9ee902",
          "message": "REL: 2.8.0\n\nNew Features (ENH):\n-  Add writer.add_annotation, page.annotations, and generic.AnnotationBuilder (#1120)\n\nBug Fixes (BUG):\n-  Set /AS for /Btn form fields in writer (#1161)\n-  Ignore if /Perms verify failed (#1157)\n\nRobustness (ROB):\n-  Cope with utf16 character for space calculation (#1155)\n-  Cope with null params for FitH / FitV destination (#1152)\n-  Handle outlines without valid destination (#1076)\n\nDeveloper Experience (DEV):\n-  Introduce _utils.logger_warning (#1148)\n\nMaintenance (MAINT):\n-  Break up parse_to_unicode (#1162)\n-  Add diagnostic output to exception in read_from_stream (#1159)\n-  Reduce PdfReader.read complexity (#1151)\n\nTesting (TST):\n-  Add workflow tests found by arc testing (#1154)\n-  Decrypt file which is not encrypted (#1149)\n-  Test CryptRC4 encryption class; test image extraction filters (#1147)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.7.0...2.8.0",
          "timestamp": "2022-07-24T11:23:39+02:00",
          "tree_id": "b05293953884c1fe33d9cc251bd40d91d699d3f2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ec30171a9da60755763ed8b2c24c96298f9ee902"
        },
        "date": 1658654721494,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0641401747345502,
            "unit": "iter/sec",
            "range": "stddev: 0.005341469481196329",
            "extra": "mean: 939.7258216000068 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.462070442402817,
            "unit": "iter/sec",
            "range": "stddev: 0.005153701438757066",
            "extra": "mean: 80.24348799999156 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27005025847083536,
            "unit": "iter/sec",
            "range": "stddev: 0.03938884544385699",
            "extra": "mean: 3.703014415400003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "db3439b3a603bd370c97994df24d8ecf8711faf6",
          "message": "MAINT: Package updates; solve mypy strict remarks (#1163)",
          "timestamp": "2022-07-24T12:53:27+02:00",
          "tree_id": "23effe67a32caa7e62164c62f64b5d914e365703",
          "url": "https://github.com/py-pdf/PyPDF2/commit/db3439b3a603bd370c97994df24d8ecf8711faf6"
        },
        "date": 1658660073077,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0468793279103554,
            "unit": "iter/sec",
            "range": "stddev: 0.007089254665890252",
            "extra": "mean: 955.2199316000156 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.320559591020908,
            "unit": "iter/sec",
            "range": "stddev: 0.005862814668828236",
            "extra": "mean: 81.16514453846636 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2677695691064615,
            "unit": "iter/sec",
            "range": "stddev: 0.0198383528365381",
            "extra": "mean: 3.7345543160000148 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ab7a9ada067d88f03b226072c6fce6b55f89a6b5",
          "message": "DOC: Typo in warning message (#1166)",
          "timestamp": "2022-07-24T18:19:49+02:00",
          "tree_id": "16b0eb143a5b246e9e11ae4bdaf6cbbdac7f600b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ab7a9ada067d88f03b226072c6fce6b55f89a6b5"
        },
        "date": 1658679649522,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0398039123308456,
            "unit": "iter/sec",
            "range": "stddev: 0.018245393733899225",
            "extra": "mean: 961.7197897999631 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.220053255725908,
            "unit": "iter/sec",
            "range": "stddev: 0.004947983307686634",
            "extra": "mean: 81.83270392307278 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27173990724170605,
            "unit": "iter/sec",
            "range": "stddev: 0.015534713529506593",
            "extra": "mean: 3.6799894801999926 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0b2728737809fa6fe253b2a4505e86cd093d7006",
          "message": "ROB: Cope with empty DecodeParams (#1165)\n\nSee #1143, 2nd part",
          "timestamp": "2022-07-24T19:40:00+02:00",
          "tree_id": "9437dfd494657aff5ac00765aac790fc8c5bdbef",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0b2728737809fa6fe253b2a4505e86cd093d7006"
        },
        "date": 1658684467336,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0465086380074604,
            "unit": "iter/sec",
            "range": "stddev: 0.005895982682673883",
            "extra": "mean: 955.5582856000001 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.318682111606961,
            "unit": "iter/sec",
            "range": "stddev: 0.006432360609824816",
            "extra": "mean: 81.17751484615191 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26679495324841795,
            "unit": "iter/sec",
            "range": "stddev: 0.024946486839636",
            "extra": "mean: 3.748196837399996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ebcf88940e876a4661e7cedcde247d908a4dcd5e",
          "message": "TST: Add test from #325 (#1169)\n\nCloses #325",
          "timestamp": "2022-07-25T20:31:28+02:00",
          "tree_id": "239a82e29ca5b62d7b6bb36f06216a5c8f98c0ec",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ebcf88940e876a4661e7cedcde247d908a4dcd5e"
        },
        "date": 1658773962672,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9023486024973394,
            "unit": "iter/sec",
            "range": "stddev: 0.009590623164206395",
            "extra": "mean: 1.1082191485999986 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.640619324358319,
            "unit": "iter/sec",
            "range": "stddev: 0.006788291945663519",
            "extra": "mean: 85.9060821538483 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23099538373632347,
            "unit": "iter/sec",
            "range": "stddev: 0.09527709614801189",
            "extra": "mean: 4.329090840800004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "844f2380d68ef047c2f9403699a933875633af11",
          "message": "ROB: Fix loading of file from #134 (#1167)\n\nSee #134\r\n\r\na) cmap : strip lines when processing cmap from fonts\r\nb) look for %EOF up to beginning of file",
          "timestamp": "2022-07-25T20:35:59+02:00",
          "tree_id": "c6d9f657d07d818254e032ef72f3a7a2b3c8c6fd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/844f2380d68ef047c2f9403699a933875633af11"
        },
        "date": 1658774222861,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1820799592710876,
            "unit": "iter/sec",
            "range": "stddev: 0.006819451899795098",
            "extra": "mean: 845.9664611999983 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.099016081552099,
            "unit": "iter/sec",
            "range": "stddev: 0.005102897096419803",
            "extra": "mean: 70.92693519999973 msec\nrounds: 15"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.30479174395027026,
            "unit": "iter/sec",
            "range": "stddev: 0.02328166731650192",
            "extra": "mean: 3.2809287648000067 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "exiledkingcc@gmail.com",
            "name": "exiledkingcc",
            "username": "exiledkingcc"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3b73b34b1014a1ccf2c8ab21153b41071fa52ef0",
          "message": "BUG: u_hash in AlgV4.compute_key (#1170)\n\nCloses #1088",
          "timestamp": "2022-07-25T22:38:14+02:00",
          "tree_id": "8cfcf4a7266b86e120e5147b68e4c624efe2086c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3b73b34b1014a1ccf2c8ab21153b41071fa52ef0"
        },
        "date": 1658781570947,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8078772640080191,
            "unit": "iter/sec",
            "range": "stddev: 0.035561962876283625",
            "extra": "mean: 1.2378117871999847 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.506503712428124,
            "unit": "iter/sec",
            "range": "stddev: 0.009736227287374956",
            "extra": "mean: 105.19114390000937 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21973363867313425,
            "unit": "iter/sec",
            "range": "stddev: 0.10202723485163538",
            "extra": "mean: 4.550964549800017 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "5b75160144a45eb75441158046edc3c5805b0749",
          "message": "REL: 2.8.1\n\nBug Fixes (BUG):\n-  u_hash in AlgV4.compute_key (#1170)\n\nRobustness (ROB):\n-  Fix loading of file from #134 (#1167)\n-  Cope with empty DecodeParams (#1165)\n\nDocumentation (DOC):\n-  Typo in warning message (#1166)\n\nMaintenance (MAINT):\n-  Package updates; solve mypy strict remarks (#1163)\n\nTesting (TST):\n-  Add test from #325 (#1169)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.8.0...2.8.1",
          "timestamp": "2022-07-25T22:41:21+02:00",
          "tree_id": "038afadd407c468e0c9f84e45f01d5b750aa90e9",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5b75160144a45eb75441158046edc3c5805b0749"
        },
        "date": 1658781767501,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0477892067900123,
            "unit": "iter/sec",
            "range": "stddev: 0.013319141629088416",
            "extra": "mean: 954.3904380000072 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.26889897257622,
            "unit": "iter/sec",
            "range": "stddev: 0.006095524318308341",
            "extra": "mean: 81.50690638460937 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26925845962162914,
            "unit": "iter/sec",
            "range": "stddev: 0.027211792882892966",
            "extra": "mean: 3.713903739199998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d8bd12f3e1d6b5a5b0a488413dbe8ec598b84355",
          "message": "BUG: Incomplete Graphic State save/restore (#1172)\n\nGraphic state shall store also the font, font size, ...\r\n\r\nSee #1142",
          "timestamp": "2022-07-27T19:18:30+02:00",
          "tree_id": "542550eb9452feaadfd88752ec408b9e11bb0bdd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d8bd12f3e1d6b5a5b0a488413dbe8ec598b84355"
        },
        "date": 1658942387202,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.893808343592129,
            "unit": "iter/sec",
            "range": "stddev: 0.00943189730336303",
            "extra": "mean: 1.1188080835999998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.243903811854517,
            "unit": "iter/sec",
            "range": "stddev: 0.007456852139132779",
            "extra": "mean: 88.93708241666864 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22701892369674181,
            "unit": "iter/sec",
            "range": "stddev: 0.02971548734296278",
            "extra": "mean: 4.4049191306000015 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9c8252d5bc876c0048b6dfe3b531bc8fa6cfd81e",
          "message": "BUG: Named Dest in PDF1.1 (#1174)\n\nNamed destinations are stored in a dictionary in PDF 1.1\r\n\r\nCloses #1173",
          "timestamp": "2022-07-27T21:31:58+02:00",
          "tree_id": "15d053117b796543eac501c0ebcf3baa8e9a408e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/9c8252d5bc876c0048b6dfe3b531bc8fa6cfd81e"
        },
        "date": 1658950389778,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8896778938373943,
            "unit": "iter/sec",
            "range": "stddev: 0.010469479957112225",
            "extra": "mean: 1.1240023011999996 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.239758125162997,
            "unit": "iter/sec",
            "range": "stddev: 0.007327894456982603",
            "extra": "mean: 88.96988608333582 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22530790301573322,
            "unit": "iter/sec",
            "range": "stddev: 0.02278210376226497",
            "extra": "mean: 4.438370721200002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7b852acb3350033a9f76fbc61f6e0d27f561b444",
          "message": "DOC: We now have CMAP support (#1177)",
          "timestamp": "2022-07-28T19:42:44+02:00",
          "tree_id": "13cc12afa1b77cdc584d16a72a27dd8f0213eb50",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7b852acb3350033a9f76fbc61f6e0d27f561b444"
        },
        "date": 1659030225969,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0541763000986601,
            "unit": "iter/sec",
            "range": "stddev: 0.005649541919640726",
            "extra": "mean: 948.6079319999988 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.025241393868319,
            "unit": "iter/sec",
            "range": "stddev: 0.004640254247969051",
            "extra": "mean: 76.77400899999854 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.27080216376394733,
            "unit": "iter/sec",
            "range": "stddev: 0.015921388475102383",
            "extra": "mean: 3.692732680199998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8d5037c590fbab28d9980962070d28a94dfd9be5",
          "message": "DOC: Mention pyHanko for signing PDF documents (#1178)",
          "timestamp": "2022-07-29T08:47:25+02:00",
          "tree_id": "83c06a077c93925f21926c89becb84221872089e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8d5037c590fbab28d9980962070d28a94dfd9be5"
        },
        "date": 1659077309328,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0492996251858635,
            "unit": "iter/sec",
            "range": "stddev: 0.007126754767050424",
            "extra": "mean: 953.0166370000074 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.214918775643191,
            "unit": "iter/sec",
            "range": "stddev: 0.005561519090434753",
            "extra": "mean: 75.67205042857543 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2662433115298449,
            "unit": "iter/sec",
            "range": "stddev: 0.01926811668724168",
            "extra": "mean: 3.7559628981999937 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "85ca871b007c23e0b5dcb8ab5915b63b1d9ac7e7",
          "message": "DOC: Table extraction (#1179)",
          "timestamp": "2022-07-29T18:54:31+02:00",
          "tree_id": "4ee7aa00534dd9c49e9613ca05e67d7127561674",
          "url": "https://github.com/py-pdf/PyPDF2/commit/85ca871b007c23e0b5dcb8ab5915b63b1d9ac7e7"
        },
        "date": 1659113732557,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0504553503768406,
            "unit": "iter/sec",
            "range": "stddev: 0.006218302359875822",
            "extra": "mean: 951.9681152000032 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.10995098075079,
            "unit": "iter/sec",
            "range": "stddev: 0.0060288971955193655",
            "extra": "mean: 76.27793585714316 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26552561392948915,
            "unit": "iter/sec",
            "range": "stddev: 0.021714019649266624",
            "extra": "mean: 3.766115009400005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mathieu.kniewallner@gmail.com",
            "name": "Mathieu Kniewallner",
            "username": "mkniewallner"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2d480685a72d665826dbd53f973173b34cf4c872",
          "message": "DOC: Update changelog url in package metadata (#1180)",
          "timestamp": "2022-07-29T19:43:02+02:00",
          "tree_id": "d687ea5c57c531c05e045ab4917d002b69098a74",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2d480685a72d665826dbd53f973173b34cf4c872"
        },
        "date": 1659116646258,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0245871684866337,
            "unit": "iter/sec",
            "range": "stddev: 0.008666911868785154",
            "extra": "mean: 976.0028534000185 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.766850066939233,
            "unit": "iter/sec",
            "range": "stddev: 0.006424162417966386",
            "extra": "mean: 78.32785649998186 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26051526300987404,
            "unit": "iter/sec",
            "range": "stddev: 0.01859651774856864",
            "extra": "mean: 3.8385466879999965 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mtd91429@users.noreply.github.com",
            "name": "mtd91429",
            "username": "mtd91429"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8c532a0ff13395b706d0ae1f183dd24bab577bfc",
          "message": "MAINT: Consistent terminology for outline items (#1156)\n\nThis PR makes sure PyPDF2 uses a consistent nomenclature for the outline:\r\n\r\n* **Outline**: A document has exactly one outline (also called \"table of contents\", in short toc). That outline might be empty.\r\n* **Outline Item**: An element within an outline. This is also called a \"bookmark\" by some PDF viewers.\r\n\r\nThis means that some names will be deprecated to ensure consistency:\r\n\r\n## PdfReader\r\n\r\n* `outlines` ➔ `outline`\r\n* `_build_outline()` ➔ `_build_outline_item()`\r\n\r\n## PdfWriter\r\n\r\n* Keep `get_outline_root()`\r\n* `add_bookmark_dict()` ➔ `add_outline()` \r\n* `add_bookmark()` ➔ `add_outline_item()`\r\n\r\n\r\n## PdfMerger\r\n\r\n* `find_bookmark()` ➔ `find_outline_item()`\r\n* `_write_bookmarks()` ➔ `_write_outline()`\r\n* `_write_bookmark_on_page()` ➔ `_write_outline_item_on_page()`\r\n* `_associate_bookmarks_to_pages()` ➔ `_associate_outline_items_to_pages()`\r\n* Keep `_trim_outline()`\r\n\r\n## generic.py\r\n\r\n* `Bookmark` ➔ `OutlineItem`\r\n\r\nCloses #1048\r\nCloses #1098",
          "timestamp": "2022-07-30T07:09:41+02:00",
          "tree_id": "eb04db67e26aeed926e00abce2a61e2000fa30a4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8c532a0ff13395b706d0ae1f183dd24bab577bfc"
        },
        "date": 1659157841776,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.062528375803113,
            "unit": "iter/sec",
            "range": "stddev: 0.007770576699827226",
            "extra": "mean: 941.1513356000014 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.014772555173414,
            "unit": "iter/sec",
            "range": "stddev: 0.004673416187843098",
            "extra": "mean: 76.83576457142901 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2726392306888314,
            "unit": "iter/sec",
            "range": "stddev: 0.01477706425287276",
            "extra": "mean: 3.6678507251999988 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8a27fa4eea0c072cd7c8718a4c04869223c31ef6",
          "message": "ENH: Add capability to filter text extraction by orientation  (#1175)\n\nCloses #1071",
          "timestamp": "2022-07-30T08:37:42+02:00",
          "tree_id": "6846bfc0b3ff2d752519e8fbbc645be15daeb874",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8a27fa4eea0c072cd7c8718a4c04869223c31ef6"
        },
        "date": 1659163136956,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8773266320865186,
            "unit": "iter/sec",
            "range": "stddev: 0.02100957944505252",
            "extra": "mean: 1.1398263353999993 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.77057854695802,
            "unit": "iter/sec",
            "range": "stddev: 0.005850627026893956",
            "extra": "mean: 92.84552316666723 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21958151773332513,
            "unit": "iter/sec",
            "range": "stddev: 0.0525692812831815",
            "extra": "mean: 4.554117351600004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "89033cb37aec3a520da01b95da0a8fdd8dcf38fb",
          "message": "STY: Apply pre-commit (#1188)",
          "timestamp": "2022-07-31T11:07:56+02:00",
          "tree_id": "efc4ce39a00642c3fd5186c6580136e7fea2ae5e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/89033cb37aec3a520da01b95da0a8fdd8dcf38fb"
        },
        "date": 1659258544248,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0466323414184588,
            "unit": "iter/sec",
            "range": "stddev: 0.009602274647424785",
            "extra": "mean: 955.4453463999977 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.164645242755816,
            "unit": "iter/sec",
            "range": "stddev: 0.006367816898442541",
            "extra": "mean: 75.96102907142718 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2621244132533348,
            "unit": "iter/sec",
            "range": "stddev: 0.024899133568500716",
            "extra": "mean: 3.8149823115999966 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2a5a199757f97b0f85a08055414bf56871f23140",
          "message": "MAINT: Consistant usage of warnings / log messages (#1164)",
          "timestamp": "2022-07-31T11:19:25+02:00",
          "tree_id": "b3423a318ac0c1f98a761d61d07569c76d6f7573",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2a5a199757f97b0f85a08055414bf56871f23140"
        },
        "date": 1659259226990,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0475587716260744,
            "unit": "iter/sec",
            "range": "stddev: 0.006660857091282424",
            "extra": "mean: 954.6003785999985 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.095097675926946,
            "unit": "iter/sec",
            "range": "stddev: 0.006469720437700362",
            "extra": "mean: 76.36445521428418 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2590650996867825,
            "unit": "iter/sec",
            "range": "stddev: 0.024834464174909723",
            "extra": "mean: 3.860033641000004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ab01f14f9bdebecd4efe552093605d5bb81f42c5",
          "message": "ENH: Add link annotation (#1189)\n\n* Add AnnotationBuilder.link(...)\r\n* Allow creating a RectangleObject from a RectangleObject. This is useful to create a copy or to ensure we have a RectangleObject with little code.\r\n* Deprecate `writer.add_link` by `writer.add_annotation(AnnotationBuilder.link(...))`.\r\n* Add test for reading an external link annotation.\r\n\r\nCloses #284",
          "timestamp": "2022-07-31T17:03:24+02:00",
          "tree_id": "403339d8e7f83b4ea19dab88aa70f0208d06fb54",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ab01f14f9bdebecd4efe552093605d5bb81f42c5"
        },
        "date": 1659279860721,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1834915384504299,
            "unit": "iter/sec",
            "range": "stddev: 0.0070573752637748234",
            "extra": "mean: 844.9574564000017 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.930138856935008,
            "unit": "iter/sec",
            "range": "stddev: 0.005614028936784909",
            "extra": "mean: 66.97861350000123 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2957016560542493,
            "unit": "iter/sec",
            "range": "stddev: 0.020408633587563348",
            "extra": "mean: 3.3817869447999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "42ae3127528a5edfecce504ab685cdd942700f54",
          "message": "ENH: Add support for pathlib.Path in PdfMerger.merge (#1190)\n\nReplace many os.path usages with pathlib",
          "timestamp": "2022-07-31T20:55:52+02:00",
          "tree_id": "086c9a7f91c301f61c2e5e0d0892129a8d0a8e3f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/42ae3127528a5edfecce504ab685cdd942700f54"
        },
        "date": 1659293825782,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.831176231253874,
            "unit": "iter/sec",
            "range": "stddev: 0.018119702539614424",
            "extra": "mean: 1.203114288400002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.493327068664627,
            "unit": "iter/sec",
            "range": "stddev: 0.0075104885590176074",
            "extra": "mean: 95.29865918181652 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2090701518387571,
            "unit": "iter/sec",
            "range": "stddev: 0.03630057659255962",
            "extra": "mean: 4.783083530599998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mtd91429@users.noreply.github.com",
            "name": "mtd91429",
            "username": "mtd91429"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7c7ef7759e031aa0639d1abd496c94d0188bed92",
          "message": "ENH: Add ability to add hex encoded colors to outline items (#1186)",
          "timestamp": "2022-07-31T21:06:47+02:00",
          "tree_id": "89784066eca59a7960c18f5d5518e95d7f04a515",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7c7ef7759e031aa0639d1abd496c94d0188bed92"
        },
        "date": 1659294468323,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.04086401132344,
            "unit": "iter/sec",
            "range": "stddev: 0.009063730443882935",
            "extra": "mean: 960.7402975999889 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.108772912187534,
            "unit": "iter/sec",
            "range": "stddev: 0.006352729714921886",
            "extra": "mean: 76.28479085714243 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2560913926833716,
            "unit": "iter/sec",
            "range": "stddev: 0.022737388676111657",
            "extra": "mean: 3.904855956000006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "0a6676fe064837222d391a7c73c7b0f3df782ac1",
          "message": "REL: 2.9.0\n\nNew Features (ENH):\n-  Add ability to add hex encoded colors to outline items (#1186)\n-  Add support for pathlib.Path in PdfMerger.merge (#1190)\n-  Add link annotation (#1189)\n-  Add capability to filter text extraction by orientation  (#1175)\n\nBug Fixes (BUG):\n-  Named Dest in PDF1.1 (#1174)\n-  Incomplete Graphic State save/restore (#1172)\n\nDocumentation (DOC):\n-  Update changelog url in package metadata (#1180)\n-  Table extraction (#1179)\n-  Mention pyHanko for signing PDF documents (#1178)\n-  We now have CMAP support (#1177)\n\nMaintenance (MAINT):\n-  Consistant usage of warnings / log messages (#1164)\n-  Consistent terminology for outline items (#1156)\n\nCode Style (STY):\n-  Apply pre-commit (#1188)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.8.1...2.9.0",
          "timestamp": "2022-07-31T21:16:03+02:00",
          "tree_id": "b8707a3138f2b6f54c2c5b92ddc04290ad111772",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0a6676fe064837222d391a7c73c7b0f3df782ac1"
        },
        "date": 1659295076345,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.040979676900055,
            "unit": "iter/sec",
            "range": "stddev: 0.008674631566280306",
            "extra": "mean: 960.6335475999985 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.045597412832,
            "unit": "iter/sec",
            "range": "stddev: 0.006150326114245457",
            "extra": "mean: 76.6542127857152 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2609130965165412,
            "unit": "iter/sec",
            "range": "stddev: 0.01687489248183051",
            "extra": "mean: 3.832693771800001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4aa9ec9637c8a154d58bf3b49185df79dfbf8e12",
          "message": "ENH: \"with\" support for PdfMerger and PdfWriter (#1193)\n\nCloses #1108\r\nCloses #1117\r\n\r\nFull credit for this PR goes to JianzhengLuo\r\n\r\nCo-authored-by: JianzhengLuo <jianzheng.luo.china@gmail.com>",
          "timestamp": "2022-08-03T13:47:28+02:00",
          "tree_id": "f23ccf439511e00993e26c887f834689bc713fc7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4aa9ec9637c8a154d58bf3b49185df79dfbf8e12"
        },
        "date": 1659527317434,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0413838092507133,
            "unit": "iter/sec",
            "range": "stddev: 0.0053684202406900396",
            "extra": "mean: 960.2607522000085 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.857895196206655,
            "unit": "iter/sec",
            "range": "stddev: 0.006027653775457083",
            "extra": "mean: 77.77322685714694 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25904612415983774,
            "unit": "iter/sec",
            "range": "stddev: 0.07621903459691846",
            "extra": "mean: 3.8603163944000016 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "chilledgeek@gmail.com",
            "name": "Ern Chow",
            "username": "chilledgeek"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d0a058ad24847f657b0922a186630535cab7a811",
          "message": "MAINT: Introduce WrongPasswordError / FileNotDecryptedError / EmptyFileError  (#1201)\n\nSome cases of PdfReadError were replaced by more specific exceptions:\r\n\r\n* FileNotDecryptedError\r\n    * WrongPasswordError\r\n* EmptyFileError\r\n\r\nThis enables PyPDF2 users to handle those specific issues more conveniently.",
          "timestamp": "2022-08-04T20:31:29+02:00",
          "tree_id": "a5de23c69f38bf44f855eefa65345a54642da77a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d0a058ad24847f657b0922a186630535cab7a811"
        },
        "date": 1659637952974,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0484843940628137,
            "unit": "iter/sec",
            "range": "stddev: 0.006682155018680735",
            "extra": "mean: 953.7576388000019 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.261086642822868,
            "unit": "iter/sec",
            "range": "stddev: 0.005970304318552824",
            "extra": "mean: 75.40860164285387 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2603981709914533,
            "unit": "iter/sec",
            "range": "stddev: 0.0392991121014089",
            "extra": "mean: 3.8402727491999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "43197dc4ccbf1f2efefa1f41edf376c30c4de963",
          "message": "ENH: Add AnnotationBuilder.text(...) to build text annotations (#1202)",
          "timestamp": "2022-08-04T22:25:54+02:00",
          "tree_id": "c162d2baccf0c3638d849f7422a65f912d964b93",
          "url": "https://github.com/py-pdf/PyPDF2/commit/43197dc4ccbf1f2efefa1f41edf376c30c4de963"
        },
        "date": 1659644825072,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.883069710523824,
            "unit": "iter/sec",
            "range": "stddev: 0.05227592414190219",
            "extra": "mean: 1.1324134301999949 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.251790361079332,
            "unit": "iter/sec",
            "range": "stddev: 0.00774013617053834",
            "extra": "mean: 88.87474507693145 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22532698468803616,
            "unit": "iter/sec",
            "range": "stddev: 0.11937259987699297",
            "extra": "mean: 4.437994860600003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "223da14bb249503574f1699b17d46cd4b7fc7885",
          "message": "DEV: Add flake8-print (#1203)",
          "timestamp": "2022-08-04T22:46:59+02:00",
          "tree_id": "de68807158b5045fcd4e74e99dab8f12a13e6fbc",
          "url": "https://github.com/py-pdf/PyPDF2/commit/223da14bb249503574f1699b17d46cd4b7fc7885"
        },
        "date": 1659646096504,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8349902849932428,
            "unit": "iter/sec",
            "range": "stddev: 0.017248055602281497",
            "extra": "mean: 1.1976187244000003 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.547084735296867,
            "unit": "iter/sec",
            "range": "stddev: 0.007247789356955628",
            "extra": "mean: 94.81292936363741 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21240549114687624,
            "unit": "iter/sec",
            "range": "stddev: 0.02312717404637299",
            "extra": "mean: 4.7079762138 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "759cbc344fb8f484dc55ba4a9f394d19f9189591",
          "message": "DOC: Fix AnnotationBuilder parameter formatting (#1204)",
          "timestamp": "2022-08-05T13:33:22+02:00",
          "tree_id": "5c5bd548b89da9af1d36e20ac87724e140b3f799",
          "url": "https://github.com/py-pdf/PyPDF2/commit/759cbc344fb8f484dc55ba4a9f394d19f9189591"
        },
        "date": 1659699273564,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0506608214869269,
            "unit": "iter/sec",
            "range": "stddev: 0.006666497538104555",
            "extra": "mean: 951.7819448000068 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.337958416496448,
            "unit": "iter/sec",
            "range": "stddev: 0.005500971636413434",
            "extra": "mean: 74.97399292857259 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2624989302984843,
            "unit": "iter/sec",
            "range": "stddev: 0.025766723318749025",
            "extra": "mean: 3.8095393335999974 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a6b8fa6e4cd654d22760ccf62760b89de287c7d6",
          "message": "DOC: Example for orientation parameter of extract_text (#1206)\n\nIntroduced by 8a27fa4eea0c072cd7c8718a4c04869223c31ef6 (#1175)",
          "timestamp": "2022-08-05T20:18:27+02:00",
          "tree_id": "3addce30d9190b90b88e63192f6e8c0ab2247619",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a6b8fa6e4cd654d22760ccf62760b89de287c7d6"
        },
        "date": 1659723574321,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0220956120407398,
            "unit": "iter/sec",
            "range": "stddev: 0.00588781616447542",
            "extra": "mean: 978.3820497999955 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.449751450432633,
            "unit": "iter/sec",
            "range": "stddev: 0.005352428818516371",
            "extra": "mean: 80.32288869230797 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2571066723141527,
            "unit": "iter/sec",
            "range": "stddev: 0.022949357524360853",
            "extra": "mean: 3.889436205599998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cb3f66e2617eb3154646a3300dfc77ac0eb7984c",
          "message": "DOC: Page vs Content scaling (#1208)\n\nCloses #1035",
          "timestamp": "2022-08-06T09:35:16+02:00",
          "tree_id": "5cf6cb430a80c49fda913d66ec0263ff2ce1245d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/cb3f66e2617eb3154646a3300dfc77ac0eb7984c"
        },
        "date": 1659771408543,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8727506197901839,
            "unit": "iter/sec",
            "range": "stddev: 0.0076444594354889055",
            "extra": "mean: 1.145802680999995 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.978123410442048,
            "unit": "iter/sec",
            "range": "stddev: 0.009640330061560263",
            "extra": "mean: 91.09024945454988 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21741475334191615,
            "unit": "iter/sec",
            "range": "stddev: 0.022381595789916508",
            "extra": "mean: 4.5995038728 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5b6bffb6c65cb982f0ad118405fc28458011f3d0",
          "message": "BUG: Allow IndirectObjects as stream filters (#1211)\n\nSee 'TABLE 3.4 Entries common to all stream dictionaries'\r\n\r\nand\r\n\r\n> Any object in a PDF file may be labeled as an indirect object.\r\n\r\nCloses #399",
          "timestamp": "2022-08-06T15:48:39+02:00",
          "tree_id": "476130414b16443849ff8590240dc4975a9454ad",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5b6bffb6c65cb982f0ad118405fc28458011f3d0"
        },
        "date": 1659793780790,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0449193490870716,
            "unit": "iter/sec",
            "range": "stddev: 0.006233377303075084",
            "extra": "mean: 957.0116591999977 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.058932087546047,
            "unit": "iter/sec",
            "range": "stddev: 0.004441237064559221",
            "extra": "mean: 76.57593999999993 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2655745992550426,
            "unit": "iter/sec",
            "range": "stddev: 0.017607373278194585",
            "extra": "mean: 3.7654203482000073 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "4963760000a14c3b0539ec053ba805065472833e",
          "message": "STY: Minor documentation formatting change",
          "timestamp": "2022-08-06T15:54:12+02:00",
          "tree_id": "081e8ecf48754718c06d0cc9703020aed30de50a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4963760000a14c3b0539ec053ba805065472833e"
        },
        "date": 1659794127657,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9047628226480979,
            "unit": "iter/sec",
            "range": "stddev: 0.02617747467181989",
            "extra": "mean: 1.1052620365999986 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.189853843218703,
            "unit": "iter/sec",
            "range": "stddev: 0.005697146425427655",
            "extra": "mean: 89.36667216668089 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23107319398659204,
            "unit": "iter/sec",
            "range": "stddev: 0.07546537338014762",
            "extra": "mean: 4.327633087799984 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "406d5f103c2543913ae4b39d1d33dddb29bfb081",
          "message": "DOC: Font scrambling",
          "timestamp": "2022-08-06T15:58:22+02:00",
          "tree_id": "176b28f5820526e41a1c47d490ef42b81d3e9022",
          "url": "https://github.com/py-pdf/PyPDF2/commit/406d5f103c2543913ae4b39d1d33dddb29bfb081"
        },
        "date": 1659794367930,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.035843837349023,
            "unit": "iter/sec",
            "range": "stddev: 0.007611730782135815",
            "extra": "mean: 965.3964854000037 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.084145410164783,
            "unit": "iter/sec",
            "range": "stddev: 0.007642617556960101",
            "extra": "mean: 76.42837714285277 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2614420034508712,
            "unit": "iter/sec",
            "range": "stddev: 0.01660144494266108",
            "extra": "mean: 3.8249400891999925 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "93514bee4092cc101280d68a42799278bb9088d9",
          "message": "TST: Killing Security Mutants (#1212)\n\n* Killed 2340\r\n* Killed 2341\r\n* Killed 2342\r\n* Killed 2383\r\n\r\nSee #1025",
          "timestamp": "2022-08-07T09:43:33+02:00",
          "tree_id": "8fb352491ce61476619164d46c05496c09e6da60",
          "url": "https://github.com/py-pdf/PyPDF2/commit/93514bee4092cc101280d68a42799278bb9088d9"
        },
        "date": 1659858275213,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0226548165178975,
            "unit": "iter/sec",
            "range": "stddev: 0.01138474254571245",
            "extra": "mean: 977.8470544000015 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.022963348482426,
            "unit": "iter/sec",
            "range": "stddev: 0.006754752024650987",
            "extra": "mean: 76.78743871428699 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25437188274427874,
            "unit": "iter/sec",
            "range": "stddev: 0.03334755852351238",
            "extra": "mean: 3.931252106999989 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dbdc9016da2728a0f3a5ec671a611695acae2247",
          "message": "STY: Apply pylint (#1213)",
          "timestamp": "2022-08-07T11:37:31+02:00",
          "tree_id": "7c46e354311c637c5f7edb201b340dc07010e033",
          "url": "https://github.com/py-pdf/PyPDF2/commit/dbdc9016da2728a0f3a5ec671a611695acae2247"
        },
        "date": 1659865116703,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0035235459837533,
            "unit": "iter/sec",
            "range": "stddev: 0.018336563681687887",
            "extra": "mean: 996.4888257999974 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.000270114969156,
            "unit": "iter/sec",
            "range": "stddev: 0.004639376756499262",
            "extra": "mean: 76.92147864285914 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26698418966767495,
            "unit": "iter/sec",
            "range": "stddev: 0.015896426263139148",
            "extra": "mean: 3.745540143200003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "20e99d9cca0c893a35d0bc959160597eae4c2153",
          "message": "TST: Add workflow tests (#1214)",
          "timestamp": "2022-08-07T12:23:35+02:00",
          "tree_id": "4d61620d24af95b11349515f9b7fe9123da2a31c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/20e99d9cca0c893a35d0bc959160597eae4c2153"
        },
        "date": 1659867886994,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.908784819293121,
            "unit": "iter/sec",
            "range": "stddev: 0.032951644625594224",
            "extra": "mean: 1.1003704933999985 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.314627291245746,
            "unit": "iter/sec",
            "range": "stddev: 0.0049927428757165345",
            "extra": "mean: 88.38117016666658 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22742090859640393,
            "unit": "iter/sec",
            "range": "stddev: 0.046242480972763955",
            "extra": "mean: 4.397133078800005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "6cc253e838b8adcce0ff80a6e804c4536f3f6c98",
          "message": "REL: 2.10.0\n\nNew Features (ENH):\n-  \"with\" support for PdfMerger and PdfWriter (#1193)\n-  Add AnnotationBuilder.text(...) to build text annotations (#1202)\n\nBug Fixes (BUG):\n-  Allow IndirectObjects as stream filters (#1211)\n\nDocumentation (DOC):\n-  Font scrambling\n-  Page vs Content scaling (#1208)\n-  Example for orientation parameter of extract_text (#1206)\n-  Fix AnnotationBuilder parameter formatting (#1204)\n\nDeveloper Experience (DEV):\n-  Add flake8-print (#1203)\n\nMaintenance (MAINT):\n-  Introduce WrongPasswordError / FileNotDecryptedError / EmptyFileError  (#1201)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.9.0...2.10.0",
          "timestamp": "2022-08-07T12:27:41+02:00",
          "tree_id": "7db532f7b4b224df414247f2d4edc28e15b3f9b2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6cc253e838b8adcce0ff80a6e804c4536f3f6c98"
        },
        "date": 1659868166805,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7635515912566374,
            "unit": "iter/sec",
            "range": "stddev: 0.019779712001904218",
            "extra": "mean: 1.3096691978000081 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.278153140363944,
            "unit": "iter/sec",
            "range": "stddev: 0.007090964569568568",
            "extra": "mean: 107.78007054545924 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19671741604230863,
            "unit": "iter/sec",
            "range": "stddev: 0.08593192599019665",
            "extra": "mean: 5.083433994400002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "83fbfb218f031d8363d0e4cf4b19587081a70897",
          "message": "TST: Don't check coverage for deprecated code (#1216)",
          "timestamp": "2022-08-08T13:54:56+02:00",
          "tree_id": "da399fcf6fc47471f8facb86e8351031b4feaf58",
          "url": "https://github.com/py-pdf/PyPDF2/commit/83fbfb218f031d8363d0e4cf4b19587081a70897"
        },
        "date": 1659959757735,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0425320558022224,
            "unit": "iter/sec",
            "range": "stddev: 0.007711792582092435",
            "extra": "mean: 959.2031194000128 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.204127649537224,
            "unit": "iter/sec",
            "range": "stddev: 0.005911119958980822",
            "extra": "mean: 75.73389371429228 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25884870661564374,
            "unit": "iter/sec",
            "range": "stddev: 0.019156165375267632",
            "extra": "mean: 3.863260562799985 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c3c807a37753949a275f9a8bc578457e58bdacbf",
          "message": "TST: 100% coverage for utils.py (#1217)",
          "timestamp": "2022-08-08T14:23:38+02:00",
          "tree_id": "0c236803a7f59b71345ccd36f4dec19413b2c059",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c3c807a37753949a275f9a8bc578457e58bdacbf"
        },
        "date": 1659961479046,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0503371876781957,
            "unit": "iter/sec",
            "range": "stddev: 0.004821036098367318",
            "extra": "mean: 952.0752114000004 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.997148978821174,
            "unit": "iter/sec",
            "range": "stddev: 0.004918663364879477",
            "extra": "mean: 76.939950571429 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26604193125401293,
            "unit": "iter/sec",
            "range": "stddev: 0.013870446832068364",
            "extra": "mean: 3.7588059720000104 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f172e43e934863be647d16cffa722fad698a215b",
          "message": "TST: Writer exception non-binary stream (#1218)",
          "timestamp": "2022-08-08T19:02:44+02:00",
          "tree_id": "3ff3b2cd794ef5436ef5cef866845b68377498d4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f172e43e934863be647d16cffa722fad698a215b"
        },
        "date": 1659978229437,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0379366633041969,
            "unit": "iter/sec",
            "range": "stddev: 0.008115188736743063",
            "extra": "mean: 963.4499245999962 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.848900362395833,
            "unit": "iter/sec",
            "range": "stddev: 0.008287524333627144",
            "extra": "mean: 77.82767176922351 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.259688567213296,
            "unit": "iter/sec",
            "range": "stddev: 0.021645078327103752",
            "extra": "mean: 3.8507663649999926 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2df8a4ca1f7ff60fa6c40dc4a4337136b27697c1",
          "message": "TST: Increase PdfReader coverage (#1219)",
          "timestamp": "2022-08-08T21:18:12+02:00",
          "tree_id": "e73bfa7398fdc1eba6ccf3c75dc89df0e5a9ad78",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2df8a4ca1f7ff60fa6c40dc4a4337136b27697c1"
        },
        "date": 1659986368499,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9205694414189726,
            "unit": "iter/sec",
            "range": "stddev: 0.009173646178667179",
            "extra": "mean: 1.0862841574000028 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.408871957539896,
            "unit": "iter/sec",
            "range": "stddev: 0.0069895596404613465",
            "extra": "mean: 87.65108449999914 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2270943453044839,
            "unit": "iter/sec",
            "range": "stddev: 0.027092047218313393",
            "extra": "mean: 4.403456187599997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "658bf285c109cb26d71807c314f0989627b6364b",
          "message": "BUG: Fix stream truncated prematurely (#1223)\n\nObserved in case of  \\0 - \\9 in streams\r\n\r\nCloses  #454",
          "timestamp": "2022-08-11T21:51:51+02:00",
          "tree_id": "a86ee9605d1f51d915ccb2e9c0688fc4de57487d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/658bf285c109cb26d71807c314f0989627b6364b"
        },
        "date": 1660247595430,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9192267930742712,
            "unit": "iter/sec",
            "range": "stddev: 0.009851972685622254",
            "extra": "mean: 1.0878708143999916 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.68715132114419,
            "unit": "iter/sec",
            "range": "stddev: 0.006428911785915929",
            "extra": "mean: 85.56405000000449 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22951618608493277,
            "unit": "iter/sec",
            "range": "stddev: 0.02240910280131804",
            "extra": "mean: 4.356991186799997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d52b8e0d526e53ba6aa41b0af7f188c0d2050a32",
          "message": "TST: PdfReader coverage (#1225)",
          "timestamp": "2022-08-12T22:48:05+02:00",
          "tree_id": "431f802b0b8064862a36571083ad81d7bb95f347",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d52b8e0d526e53ba6aa41b0af7f188c0d2050a32"
        },
        "date": 1660337359525,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8928576493944339,
            "unit": "iter/sec",
            "range": "stddev: 0.010715067874554998",
            "extra": "mean: 1.1199993645999826 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.391798507701884,
            "unit": "iter/sec",
            "range": "stddev: 0.0053679249367367425",
            "extra": "mean: 87.78245149999009 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2259552077428206,
            "unit": "iter/sec",
            "range": "stddev: 0.07735595346053589",
            "extra": "mean: 4.425655907600003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8948878c96a133e777ff66dcca0ab5f69b0ef696",
          "message": "TST: Strict get fonts (#1226)",
          "timestamp": "2022-08-13T06:04:12+02:00",
          "tree_id": "7d645a0e25d0557ce84be322668c084ba2767fe0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/8948878c96a133e777ff66dcca0ab5f69b0ef696"
        },
        "date": 1660363521436,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.046125800119858,
            "unit": "iter/sec",
            "range": "stddev: 0.005546805261089095",
            "extra": "mean: 955.9079795999935 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.831998516767875,
            "unit": "iter/sec",
            "range": "stddev: 0.004797719658372934",
            "extra": "mean: 77.93018357142704 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2619210666670236,
            "unit": "iter/sec",
            "range": "stddev: 0.01126909808876184",
            "extra": "mean: 3.817944133799995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "41e05f80fcea057f253d05d09b809b9abe7c3110",
          "message": "DOC: Fix docstring formatting (#1228)",
          "timestamp": "2022-08-13T07:35:15+02:00",
          "tree_id": "3e044c5f8fb881bd453ca20124e75ce814438666",
          "url": "https://github.com/py-pdf/PyPDF2/commit/41e05f80fcea057f253d05d09b809b9abe7c3110"
        },
        "date": 1660368979157,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0486193487253743,
            "unit": "iter/sec",
            "range": "stddev: 0.00849800180854959",
            "extra": "mean: 953.634892599996 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.183071541372753,
            "unit": "iter/sec",
            "range": "stddev: 0.006017000556115816",
            "extra": "mean: 75.85485649999514 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2582502188030016,
            "unit": "iter/sec",
            "range": "stddev: 0.043106602811107904",
            "extra": "mean: 3.872213563399998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a85148ae83033de50e59dae7ca621305bb53ef6a",
          "message": "MAINT: Split generic.py (#1229)\n\nThe aim of this refactoring PR is to explicitly define the interface of `PyPDF2.generic` via `__all__` and to structure this big submodule more. I hope this makes it easier to test / expand in future if necessary. Smaller modules should have less merge conflicts.\r\n\r\nThis PR should not change anything for users of PyPDF2.",
          "timestamp": "2022-08-13T22:03:13+02:00",
          "tree_id": "8e958153d88e2e2259806c34a734813fa9de958b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a85148ae83033de50e59dae7ca621305bb53ef6a"
        },
        "date": 1660421070628,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8323966235395815,
            "unit": "iter/sec",
            "range": "stddev: 0.023810611343741437",
            "extra": "mean: 1.201350380000008 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.439135403018941,
            "unit": "iter/sec",
            "range": "stddev: 0.006898163262289006",
            "extra": "mean: 95.79337381818091 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22233941901976878,
            "unit": "iter/sec",
            "range": "stddev: 0.051147426823572865",
            "extra": "mean: 4.497628015799966 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3424c71cfaa779a05a4f5d711d9f309cd431288b",
          "message": "TST: generic._base (#1230)",
          "timestamp": "2022-08-13T22:43:21+02:00",
          "tree_id": "73e9ea191fc398816472ce82620d90ecb67e334a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3424c71cfaa779a05a4f5d711d9f309cd431288b"
        },
        "date": 1660423467081,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0347755628530684,
            "unit": "iter/sec",
            "range": "stddev: 0.007253530758463796",
            "extra": "mean: 966.3931347999892 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.708632077225717,
            "unit": "iter/sec",
            "range": "stddev: 0.005813381055784986",
            "extra": "mean: 78.68667484614906 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25991393770345284,
            "unit": "iter/sec",
            "range": "stddev: 0.02184652357282759",
            "extra": "mean: 3.8474273786000026 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e11b373e45605c312ce3e94171a79068cb5de7a8",
          "message": "TST: Free-Text annotations (#1231)",
          "timestamp": "2022-08-13T23:10:46+02:00",
          "tree_id": "12b23ad6bdc70901be284a18dd1647dac3c08daf",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e11b373e45605c312ce3e94171a79068cb5de7a8"
        },
        "date": 1660425110136,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0389249782798171,
            "unit": "iter/sec",
            "range": "stddev: 0.007815873987600093",
            "extra": "mean: 962.5334080000016 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.200809924754594,
            "unit": "iter/sec",
            "range": "stddev: 0.005976024143372886",
            "extra": "mean: 75.75292771428873 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2611263662683638,
            "unit": "iter/sec",
            "range": "stddev: 0.015324081531111389",
            "extra": "mean: 3.829563495599996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b440f54ff00116cb079f2e3d459b0fa434092b48",
          "message": "TST: create_string_object (#1232)",
          "timestamp": "2022-08-14T08:54:45+02:00",
          "tree_id": "db6ded0b88e6f831e072ea6ad89594a81728df92",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b440f54ff00116cb079f2e3d459b0fa434092b48"
        },
        "date": 1660460162144,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8557300117840186,
            "unit": "iter/sec",
            "range": "stddev: 0.012006264141557196",
            "extra": "mean: 1.1685928812000044 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.68642288592819,
            "unit": "iter/sec",
            "range": "stddev: 0.007517540176653925",
            "extra": "mean: 93.57668236363668 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2142483251065412,
            "unit": "iter/sec",
            "range": "stddev: 0.032459419978530246",
            "extra": "mean: 4.6674810619999985 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f066d3173cfba5d46d22e27368b46a6953716cd7",
          "message": "BUG: TreeObject.remove_child had non-PdfObject assignment (#1233)",
          "timestamp": "2022-08-14T12:07:54+02:00",
          "tree_id": "48f35808314aad67458bf0552cbd04a342f65e76",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f066d3173cfba5d46d22e27368b46a6953716cd7"
        },
        "date": 1660471737478,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0372265248622325,
            "unit": "iter/sec",
            "range": "stddev: 0.007289506462589189",
            "extra": "mean: 964.1095518000014 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.769019996986401,
            "unit": "iter/sec",
            "range": "stddev: 0.005190036893331394",
            "extra": "mean: 78.3145456923091 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26240072534580217,
            "unit": "iter/sec",
            "range": "stddev: 0.010948658655141549",
            "extra": "mean: 3.810965075200002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dc84a42b2fee59978c531d58663fbbbb63df4d86",
          "message": "BUG: TreeObject.remove_child had an assignment issue for Count (#1234)",
          "timestamp": "2022-08-14T13:56:02+02:00",
          "tree_id": "f7e1a22e1dfc5b892d022d7e6f9062e31a79f549",
          "url": "https://github.com/py-pdf/PyPDF2/commit/dc84a42b2fee59978c531d58663fbbbb63df4d86"
        },
        "date": 1660478223708,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.043958233503568,
            "unit": "iter/sec",
            "range": "stddev: 0.0065962154201799975",
            "extra": "mean: 957.892727799998 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.859731374100132,
            "unit": "iter/sec",
            "range": "stddev: 0.004904278208549955",
            "extra": "mean: 77.76212199999983 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2635904671980776,
            "unit": "iter/sec",
            "range": "stddev: 0.018063290312803973",
            "extra": "mean: 3.7937639044000036 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fd0c802bb35996591b55fd0ed0ca4d239190a59c",
          "message": "TST: TreeObject.remove_child for middle node (#1235)",
          "timestamp": "2022-08-14T14:14:31+02:00",
          "tree_id": "d7c12cca79b228cfec1e6b25ee611396198547a8",
          "url": "https://github.com/py-pdf/PyPDF2/commit/fd0c802bb35996591b55fd0ed0ca4d239190a59c"
        },
        "date": 1660479344852,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.039123595677712,
            "unit": "iter/sec",
            "range": "stddev: 0.007968803547059047",
            "extra": "mean: 962.3494300000033 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.718752227030619,
            "unit": "iter/sec",
            "range": "stddev: 0.005796773372217702",
            "extra": "mean: 78.624064857144 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2608326600088632,
            "unit": "iter/sec",
            "range": "stddev: 0.019017640457568555",
            "extra": "mean: 3.8338757115999953 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b4852391e3ff5b4b1803c516971b38c7bf3234d5",
          "message": "TST: TreeObject.empty_tree() (#1236)",
          "timestamp": "2022-08-14T18:06:26+02:00",
          "tree_id": "58d001b49cc2f8eab9a8f96d193ae12dbcb5fd25",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b4852391e3ff5b4b1803c516971b38c7bf3234d5"
        },
        "date": 1660493271886,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8668479514802812,
            "unit": "iter/sec",
            "range": "stddev: 0.01220649866865802",
            "extra": "mean: 1.1536048488000006 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.088430107207378,
            "unit": "iter/sec",
            "range": "stddev: 0.007899081067918668",
            "extra": "mean: 90.1840919166735 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21954546682834492,
            "unit": "iter/sec",
            "range": "stddev: 0.033170375184360903",
            "extra": "mean: 4.5548651695999975 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3285673bf23247ff6b9184b2ec7189c708e3907f",
          "message": "TST: PdfWriter (#1237)",
          "timestamp": "2022-08-14T22:09:46+02:00",
          "tree_id": "a6a628348956191cdd4721f862d834d369c55edf",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3285673bf23247ff6b9184b2ec7189c708e3907f"
        },
        "date": 1660507850671,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0415860771988925,
            "unit": "iter/sec",
            "range": "stddev: 0.007685537296421868",
            "extra": "mean: 960.0742770000068 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.034225066148197,
            "unit": "iter/sec",
            "range": "stddev: 0.006057095424015961",
            "extra": "mean: 76.72109350000004 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26003902093540404,
            "unit": "iter/sec",
            "range": "stddev: 0.02350073926446205",
            "extra": "mean: 3.8455766999999925 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eee49b98e365484529479e88013a91b09d6642c1",
          "message": "TST: AlgV5.generate_values (#1238)",
          "timestamp": "2022-08-15T12:28:46+02:00",
          "tree_id": "c162a197c1030729b99e07cb1173c5c5e422bb4c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/eee49b98e365484529479e88013a91b09d6642c1"
        },
        "date": 1660559387836,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0373983684522978,
            "unit": "iter/sec",
            "range": "stddev: 0.009237625007346198",
            "extra": "mean: 963.9498484000001 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.186506096477789,
            "unit": "iter/sec",
            "range": "stddev: 0.006286552931874484",
            "extra": "mean: 75.83509935714565 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2621338128726258,
            "unit": "iter/sec",
            "range": "stddev: 0.01924520890389074",
            "extra": "mean: 3.8148455136000052 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5713f5080d94764fbb891e5c333d747d69f01468",
          "message": "TST: Decrypt AlgV4 with owner password (#1239)",
          "timestamp": "2022-08-15T13:42:28+02:00",
          "tree_id": "cbd337fab1ce9935b811a0190df393633ac08960",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5713f5080d94764fbb891e5c333d747d69f01468"
        },
        "date": 1660563813776,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0399293559183265,
            "unit": "iter/sec",
            "range": "stddev: 0.006399689931126058",
            "extra": "mean: 961.6037804000001 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.72592369036929,
            "unit": "iter/sec",
            "range": "stddev: 0.0052478141153513725",
            "extra": "mean: 78.57975769230634 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.260465324031058,
            "unit": "iter/sec",
            "range": "stddev: 0.01532811169402222",
            "extra": "mean: 3.8392826520000014 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "1423c0d76d40490e0074a1836cb5a7b06934fbcb",
          "message": "REL: 2.10.1\n\nBug Fixes (BUG):\n-  TreeObject.remove_child had a non-PdfObject assignment for Count (#1233, #1234)\n-  Fix stream truncated prematurely (#1223)\n\nDocumentation (DOC):\n-  Fix docstring formatting (#1228)\n\nMaintenance (MAINT):\n-  Split generic.py (#1229)\n\nTesting (TST):\n-  Decrypt AlgV4 with owner password (#1239)\n-  AlgV5.generate_values (#1238)\n-  TreeObject.remove_child / empty_tree (#1235, #1236)\n-  create_string_object (#1232)\n-  Free-Text annotations (#1231)\n-  generic._base (#1230)\n-  Strict get fonts (#1226)\n-  Increase PdfReader coverage (#1219, #1225)\n-  Increase PdfWriter coverage (#1237)\n-  100% coverage for utils.py (#1217)\n-  Writer exception non-binary stream (#1218)\n-  Don't check coverage for deprecated code (#1216)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.0...2.10.1",
          "timestamp": "2022-08-15T13:47:39+02:00",
          "tree_id": "cece1a835d062231c528d154746d1e21a99bd289",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1423c0d76d40490e0074a1836cb5a7b06934fbcb"
        },
        "date": 1660564206314,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0451345963578007,
            "unit": "iter/sec",
            "range": "stddev: 0.009019294671757135",
            "extra": "mean: 956.8145609999988 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.989716619394455,
            "unit": "iter/sec",
            "range": "stddev: 0.0070879080699229255",
            "extra": "mean: 76.98397350000212 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26219195758238156,
            "unit": "iter/sec",
            "range": "stddev: 0.012221154644236296",
            "extra": "mean: 3.8139995186000193 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "870198d52271fc12eeefe149f1a9ebab1dd5883a",
          "message": "BUG: Add PyPDF2.generic to distribution\n\nCloses #1243",
          "timestamp": "2022-08-15T16:16:20+02:00",
          "tree_id": "8402406e7ab3ce6a69ff58b4b63fb2156a99125e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/870198d52271fc12eeefe149f1a9ebab1dd5883a"
        },
        "date": 1660573065578,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0413138216000881,
            "unit": "iter/sec",
            "range": "stddev: 0.007996612905786609",
            "extra": "mean: 960.3252921999967 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.097581322703277,
            "unit": "iter/sec",
            "range": "stddev: 0.0061718785164480315",
            "extra": "mean: 76.34997449999454 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25903566106390824,
            "unit": "iter/sec",
            "range": "stddev: 0.012493525108583084",
            "extra": "mean: 3.8604723222000077 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "b50c3a82f330a9b21b575131537fa9ac55a21b2b",
          "message": "REL: 2.10.2\n\nBUG: Add PyPDF2.generic to PyPI distribution",
          "timestamp": "2022-08-15T16:21:20+02:00",
          "tree_id": "e2feb3f028aa5457da73700cd97935b928416048",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b50c3a82f330a9b21b575131537fa9ac55a21b2b"
        },
        "date": 1660573366143,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0323584271254942,
            "unit": "iter/sec",
            "range": "stddev: 0.008632402961802317",
            "extra": "mean: 968.6558212000136 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.073899149419068,
            "unit": "iter/sec",
            "range": "stddev: 0.006218866259959867",
            "extra": "mean: 76.48827550000144 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25712277678697854,
            "unit": "iter/sec",
            "range": "stddev: 0.03177415479147628",
            "extra": "mean: 3.8891925969999988 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "917ff2ecbf26660520d7385d55ae68ac3f1b0c4d",
          "message": "DOC: Adding WevertonGomes as a Contributor\n\nThank you for reporting the issue so quickly!",
          "timestamp": "2022-08-15T16:53:28+02:00",
          "tree_id": "7dfece31221434b8d1ef72c24e587713e4ed1aac",
          "url": "https://github.com/py-pdf/PyPDF2/commit/917ff2ecbf26660520d7385d55ae68ac3f1b0c4d"
        },
        "date": 1660575303043,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0222397266645715,
            "unit": "iter/sec",
            "range": "stddev: 0.013261486145194675",
            "extra": "mean: 978.244118200007 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.931504432261626,
            "unit": "iter/sec",
            "range": "stddev: 0.006522446003196362",
            "extra": "mean: 77.33052292857678 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25760414724360353,
            "unit": "iter/sec",
            "range": "stddev: 0.029765619904610945",
            "extra": "mean: 3.8819250804000034 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "matt.peveler@gmail.com",
            "name": "Matthew Peveler",
            "username": "MasterOdin"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "28cf36aa9546787789b2c0b59f947bc2594e50be",
          "message": "DEV: Modify CI to better verify built package contents (#1244)\n\nPR modifies the package CI job in two ways:\r\n\r\n1. Pass package to check-wheel-contents. This makes it so that check-wheel-contents verifies that each file in the package are actually in the wheel following their directory structure.\r\n2. Have CI steps that verify we can install the package, and that we can run a minimal example with it \r\n\r\nEither of these steps would have been sufficient to have caught #1242 per the example runs above.\r\n\r\nSigned-off-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-08-17T21:27:16+02:00",
          "tree_id": "0172e6bbf6c552088414f7960f433f0b3cfdf41e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/28cf36aa9546787789b2c0b59f947bc2594e50be"
        },
        "date": 1660764502047,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0289452533661347,
            "unit": "iter/sec",
            "range": "stddev: 0.012586140199654306",
            "extra": "mean: 971.8690054000035 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.919126417198093,
            "unit": "iter/sec",
            "range": "stddev: 0.007216819553615987",
            "extra": "mean: 77.4046145000012 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25941972100251603,
            "unit": "iter/sec",
            "range": "stddev: 0.016285558105022732",
            "extra": "mean: 3.8547570559999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cb6c2247566cb42596de2dbbc05cae202242336f",
          "message": "TST: Various PdfWriter (Layout, Bookmark deprecation) (#1249)",
          "timestamp": "2022-08-17T22:16:18+02:00",
          "tree_id": "1511d1885afbc09c08d62f35809aaf6a3b7683e9",
          "url": "https://github.com/py-pdf/PyPDF2/commit/cb6c2247566cb42596de2dbbc05cae202242336f"
        },
        "date": 1660767442181,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.054680557268596,
            "unit": "iter/sec",
            "range": "stddev: 0.008026268202551253",
            "extra": "mean: 948.1543896000062 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.224698505874471,
            "unit": "iter/sec",
            "range": "stddev: 0.005989623961342829",
            "extra": "mean: 75.61609057142553 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2636341285745015,
            "unit": "iter/sec",
            "range": "stddev: 0.010720166652009767",
            "extra": "mean: 3.793135605800012 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "52463ea626dba78dbcfab17074b5dc941f1319f5",
          "message": "MAINT: Remove unreachable code in read_block_backwards (#1250)\n\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-08-19T19:25:30+02:00",
          "tree_id": "b693898dfb2f88b9ff244d8ab192a49348e859c0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/52463ea626dba78dbcfab17074b5dc941f1319f5"
        },
        "date": 1660930038714,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9370789911421517,
            "unit": "iter/sec",
            "range": "stddev: 0.05490430105340881",
            "extra": "mean: 1.067145896400001 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.739179837471907,
            "unit": "iter/sec",
            "range": "stddev: 0.005446674815746214",
            "extra": "mean: 93.11698054545369 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.23100923168341247,
            "unit": "iter/sec",
            "range": "stddev: 0.11175293305201095",
            "extra": "mean: 4.328831331600003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c188fb023762950075efe5a220e465018af0f16d",
          "message": "TST: PdfReader.xmp_metadata workflow (#1257)",
          "timestamp": "2022-08-20T13:20:04+02:00",
          "tree_id": "80728ef0379658306309f3c6059830bfb7bc7c67",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c188fb023762950075efe5a220e465018af0f16d"
        },
        "date": 1660994470505,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0404101392819682,
            "unit": "iter/sec",
            "range": "stddev: 0.01010084526429312",
            "extra": "mean: 961.159414200003 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.211902473461977,
            "unit": "iter/sec",
            "range": "stddev: 0.005882423431378663",
            "extra": "mean: 75.68932649999839 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26055705281183156,
            "unit": "iter/sec",
            "range": "stddev: 0.045464232085244555",
            "extra": "mean: 3.837931037400003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7f0a6b01b271b415188934003e383641aa308481",
          "message": "MAINT: password param of _security._alg32(...) is only a string, not bytes (#1259)\n\nAdjust type annotations",
          "timestamp": "2022-08-20T17:10:46+02:00",
          "tree_id": "989b0ba77debeba7eabd1e3b4d7dc544385dbe8b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7f0a6b01b271b415188934003e383641aa308481"
        },
        "date": 1661008312744,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0455140627967872,
            "unit": "iter/sec",
            "range": "stddev: 0.008802420271973132",
            "extra": "mean: 956.4672877999982 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.060588126156821,
            "unit": "iter/sec",
            "range": "stddev: 0.007695772341006107",
            "extra": "mean: 76.56623042857242 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.261173405591114,
            "unit": "iter/sec",
            "range": "stddev: 0.021487444768067545",
            "extra": "mean: 3.828873761999998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0983fe4b198eb121799a9f403bf3f6ff5604e9dd",
          "message": "MAINT: Let PdfMerger._create_stream raise NotImplemented (#1251)\n\n... if arg is none of str/Path/stream/PdfReader",
          "timestamp": "2022-08-20T19:16:12+02:00",
          "tree_id": "35b4b22d0cce469ea3229ddc80d71029283bfe65",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0983fe4b198eb121799a9f403bf3f6ff5604e9dd"
        },
        "date": 1661015841254,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1741268407145466,
            "unit": "iter/sec",
            "range": "stddev: 0.00654781365166129",
            "extra": "mean: 851.6967378000004 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.832101203030904,
            "unit": "iter/sec",
            "range": "stddev: 0.005677800754418979",
            "extra": "mean: 67.42133068749911 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25904943472816644,
            "unit": "iter/sec",
            "range": "stddev: 0.030364166550685315",
            "extra": "mean: 3.8602670607999983 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "baf0de1be0b68a1c1654d63ba60bbdca87ca6e80",
          "message": "TST: Close PdfMerger in tests (#1260)",
          "timestamp": "2022-08-20T20:15:04+02:00",
          "tree_id": "b262f3eefc2d38cd305d63216d4050f3798e5f6e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/baf0de1be0b68a1c1654d63ba60bbdca87ca6e80"
        },
        "date": 1661019372928,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0395083123852884,
            "unit": "iter/sec",
            "range": "stddev: 0.008126362283471111",
            "extra": "mean: 961.9932693999999 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.111357882058998,
            "unit": "iter/sec",
            "range": "stddev: 0.0062149287492786285",
            "extra": "mean: 76.26975092857131 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2616860634545713,
            "unit": "iter/sec",
            "range": "stddev: 0.013092832759295573",
            "extra": "mean: 3.8213727807999986 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cf3aab4b784163539a1f68ebd3f8979018449204",
          "message": "ROB: Decrypt returns empty bytestring (#1258)\n\nCloses #1245",
          "timestamp": "2022-08-21T17:37:22+02:00",
          "tree_id": "af3c06f3de9b56467d2973e6816addd7bfaa6590",
          "url": "https://github.com/py-pdf/PyPDF2/commit/cf3aab4b784163539a1f68ebd3f8979018449204"
        },
        "date": 1661096319413,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8836858516938194,
            "unit": "iter/sec",
            "range": "stddev: 0.012720617999235382",
            "extra": "mean: 1.1316238662000004 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.045125963876767,
            "unit": "iter/sec",
            "range": "stddev: 0.007452184204886718",
            "extra": "mean: 90.53767274999973 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22358587462793958,
            "unit": "iter/sec",
            "range": "stddev: 0.0457764006060093",
            "extra": "mean: 4.472554456599999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "67144813863936e34b37a0fe382a1f811a5f3681",
          "message": "MAINT: Remove 'mine' as PdfMerger always creates the stream (#1261)",
          "timestamp": "2022-08-21T20:02:01+02:00",
          "tree_id": "1b989f2bdc27b64399cd4646530cf9158a365fb5",
          "url": "https://github.com/py-pdf/PyPDF2/commit/67144813863936e34b37a0fe382a1f811a5f3681"
        },
        "date": 1661104980532,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.1838852554619061,
            "unit": "iter/sec",
            "range": "stddev: 0.007046529283704954",
            "extra": "mean: 844.676454399999 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 14.788379162995014,
            "unit": "iter/sec",
            "range": "stddev: 0.005417849373847881",
            "extra": "mean: 67.62066274999911 msec\nrounds: 16"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2938413116889739,
            "unit": "iter/sec",
            "range": "stddev: 0.019800708466894378",
            "extra": "mean: 3.403197441000002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2ff3bff55b8208e57c1d292d63ef72a82e071b06",
          "message": "MAINT: Remove unused sign function in _extract_text (#1262)",
          "timestamp": "2022-08-21T20:24:34+02:00",
          "tree_id": "86dfc2f6f3709c99831df6c373b2f923f81fd405",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2ff3bff55b8208e57c1d292d63ef72a82e071b06"
        },
        "date": 1661106348220,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0009085597314662,
            "unit": "iter/sec",
            "range": "stddev: 0.023494447267058075",
            "extra": "mean: 999.0922650000016 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.168313106908847,
            "unit": "iter/sec",
            "range": "stddev: 0.007511048066215973",
            "extra": "mean: 82.18065981818188 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2546623616234841,
            "unit": "iter/sec",
            "range": "stddev: 0.07835100710192802",
            "extra": "mean: 3.9267679511999916 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b086e20dc4d0a24f3849652b8164088788479387",
          "message": "TST: Delete annotations (#1263)",
          "timestamp": "2022-08-21T21:15:10+02:00",
          "tree_id": "8ac79b2b0af24f6f96cf710aefd2995c3657a280",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b086e20dc4d0a24f3849652b8164088788479387"
        },
        "date": 1661109372734,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.099982460471667,
            "unit": "iter/sec",
            "range": "stddev: 0.01629611671322416",
            "extra": "mean: 909.1054048000046 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.483398901706263,
            "unit": "iter/sec",
            "range": "stddev: 0.004890501893591509",
            "extra": "mean: 74.16527592856832 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26801350798715057,
            "unit": "iter/sec",
            "range": "stddev: 0.032347096512371755",
            "extra": "mean: 3.731155222399997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "2ddc48a8933bce3efec757fd0222fa07d0f07b0e",
          "message": "REL: 2.10.3\n\nRobustness (ROB):\n-  Decrypt returns empty bytestring (#1258)\n\nDocumentation (DOC):\n-  Adding WevertonGomes as a Contributor\n\nDeveloper Experience (DEV):\n-  Modify CI to better verify built package contents (#1244)\n\nMaintenance (MAINT):\n-  Remove unused sign function in _extract_text (#1262)\n-  Remove \\'mine\\' as PdfMerger always creates the stream (#1261)\n-  Let PdfMerger._create_stream raise NotImplemented (#1251)\n-  password param of _security._alg32(...) is only a string, not bytes (#1259)\n-  Remove unreachable code in read_block_backwards (#1250)\n\nTesting (TST):\n-  Delete annotations (#1263)\n-  Close PdfMerger in tests (#1260)\n-  PdfReader.xmp_metadata workflow (#1257)\n-  Various PdfWriter (Layout, Bookmark deprecation) (#1249)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.2...2.10.3",
          "timestamp": "2022-08-21T21:18:49+02:00",
          "tree_id": "9157df6706b82e8fa527ea1a5cceb6e27217a9cf",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2ddc48a8933bce3efec757fd0222fa07d0f07b0e"
        },
        "date": 1661109635987,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0318547139730054,
            "unit": "iter/sec",
            "range": "stddev: 0.007335895767721379",
            "extra": "mean: 969.1286829999996 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.73121350258523,
            "unit": "iter/sec",
            "range": "stddev: 0.005496567335273853",
            "extra": "mean: 78.54710784615602 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2602075659943726,
            "unit": "iter/sec",
            "range": "stddev: 0.0346785794246462",
            "extra": "mean: 3.843085792599999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "Shortfinga@users.noreply.github.com",
            "name": "Maximilian",
            "username": "Shortfinga"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "84460f54aa4721db36452fe510f8063838e358d5",
          "message": "PKG: Add minimum version for typing_extensions requirement (#1277)\n\nPyPDF2 uses TypeAlias which was introduced via PEP 613 in Python 3.10. Older versions of Python need typing_extensions>=3.10.0.0.",
          "timestamp": "2022-08-27T11:37:58+02:00",
          "tree_id": "9d70756651d1e055932cc07dfe69127b9db3e6dd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/84460f54aa4721db36452fe510f8063838e358d5"
        },
        "date": 1661593155706,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8882557378302759,
            "unit": "iter/sec",
            "range": "stddev: 0.012174822316427632",
            "extra": "mean: 1.125801903000007 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.196244858594758,
            "unit": "iter/sec",
            "range": "stddev: 0.00726290642689451",
            "extra": "mean: 89.31566008333174 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22231838051433703,
            "unit": "iter/sec",
            "range": "stddev: 0.02610528429108766",
            "extra": "mean: 4.4980536368 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "4745984bee177eec5c92adc0df13c6f293aca9c5",
          "message": "DEV: Fix benchmark",
          "timestamp": "2022-08-28T12:42:31+02:00",
          "tree_id": "dddb13fdde1fdb40507b10534ae4f665c2029b6b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4745984bee177eec5c92adc0df13c6f293aca9c5"
        },
        "date": 1661683443577,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7716416716303457,
            "unit": "iter/sec",
            "range": "stddev: 0.026605073066173216",
            "extra": "mean: 1.2959383050000042 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.712474564218983,
            "unit": "iter/sec",
            "range": "stddev: 0.006307335780672884",
            "extra": "mean: 102.96037259999906 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20127640286705403,
            "unit": "iter/sec",
            "range": "stddev: 0.04055135773160935",
            "extra": "mean: 4.9682922874000015 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "69a27ae9db9eda4406942c0c4f7effff38498523",
          "message": "TST: Rectangle deletion (#1289)",
          "timestamp": "2022-08-28T13:22:50+02:00",
          "tree_id": "491e3e637b51b26c975dabbc1eef521277e2ff79",
          "url": "https://github.com/py-pdf/PyPDF2/commit/69a27ae9db9eda4406942c0c4f7effff38498523"
        },
        "date": 1661685848766,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8501818151389722,
            "unit": "iter/sec",
            "range": "stddev: 0.04525304620215502",
            "extra": "mean: 1.1762189947999986 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.292573574343962,
            "unit": "iter/sec",
            "range": "stddev: 0.009336841163847732",
            "extra": "mean: 97.15743033333031 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22011052316548957,
            "unit": "iter/sec",
            "range": "stddev: 0.05302062880752393",
            "extra": "mean: 4.543172155599995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "347cc24cb0d3b3a8db27d82031e4d8351d2db2ab",
          "message": "MAINT: Use NameObject idempotency (#1290)",
          "timestamp": "2022-08-28T13:41:00+02:00",
          "tree_id": "134975eba3c7d7b2386a676797f0940a8e90fdbd",
          "url": "https://github.com/py-pdf/PyPDF2/commit/347cc24cb0d3b3a8db27d82031e4d8351d2db2ab"
        },
        "date": 1661686938400,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8318193289908056,
            "unit": "iter/sec",
            "range": "stddev: 0.02141846455177555",
            "extra": "mean: 1.2021841343999995 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.50070117286518,
            "unit": "iter/sec",
            "range": "stddev: 0.005455647175104198",
            "extra": "mean: 95.2317358181848 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21348101555134683,
            "unit": "iter/sec",
            "range": "stddev: 0.06088756479434983",
            "extra": "mean: 4.684257274200002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "3b74312924542a59dce5c3f8e067b6e1765a12e6",
          "message": "REL: 2.10.4\n\nRobustness (ROB):\n-  Fix errors/warnings on no /Resources within extract_text (#1276)\n-  Add required line separators in ContentStream ArrayObjects (#1281)\n\nMaintenance (MAINT):\n-  Use NameObject idempotency (#1290)\n\nTesting (TST):\n-  Rectangle deletion (#1289)\n-  Add workflow tests (#1287)\n-  Remove files after tests ran (#1286)\n\nPackaging (PKG):\n-  Add minimum version for typing_extensions requirement (#1277)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.3...2.10.4",
          "timestamp": "2022-08-28T14:41:24+02:00",
          "tree_id": "51f65fcd64641186c8a554a6ec201406a04ce552",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3b74312924542a59dce5c3f8e067b6e1765a12e6"
        },
        "date": 1661690596799,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8484339475283145,
            "unit": "iter/sec",
            "range": "stddev: 0.016130499778974097",
            "extra": "mean: 1.1786421358000028 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.177434279759009,
            "unit": "iter/sec",
            "range": "stddev: 0.004999568420946521",
            "extra": "mean: 98.25659124999812 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21005747619677081,
            "unit": "iter/sec",
            "range": "stddev: 0.08995703125245019",
            "extra": "mean: 4.760601803400002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b5dce26583a125a15a39bf816dc3c979f5212638",
          "message": "ROB: Cope with corrupted entries in xref table (#1300)\n\nThis robustness improvement is for PDF files that have a corrupted Xref table entry, but the object can be found in the PDF file by searching the file for the entry.\r\n\r\nCloses #1292",
          "timestamp": "2022-08-29T17:00:26+02:00",
          "tree_id": "c41aa8573a56e890eb86897ade2f776d75b4201e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b5dce26583a125a15a39bf816dc3c979f5212638"
        },
        "date": 1661785295143,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0251856503722079,
            "unit": "iter/sec",
            "range": "stddev: 0.011782442337798677",
            "extra": "mean: 975.4330834000029 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.846158764820924,
            "unit": "iter/sec",
            "range": "stddev: 0.007798212546502772",
            "extra": "mean: 77.84428157142897 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2533932622149277,
            "unit": "iter/sec",
            "range": "stddev: 0.024259499187166557",
            "extra": "mean: 3.9464348470000035 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d9ba8170f2712883422cbc23a906818ad72c81da",
          "message": "MAINT: Remove catching OverflowException (#1302)\n\nSince Python 2.2 (PEP 237), integers cannot throw overflow exceptions.",
          "timestamp": "2022-08-29T21:19:00+02:00",
          "tree_id": "694d09062f1652cd52268e5b31263a59158a99d2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d9ba8170f2712883422cbc23a906818ad72c81da"
        },
        "date": 1661800809953,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9749196586940284,
            "unit": "iter/sec",
            "range": "stddev: 0.04023151375329755",
            "extra": "mean: 1.0257255467999982 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.33038995945093,
            "unit": "iter/sec",
            "range": "stddev: 0.0047668218838942955",
            "extra": "mean: 81.10043585714217 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26115022281684297,
            "unit": "iter/sec",
            "range": "stddev: 0.01137542885677665",
            "extra": "mean: 3.8292136580000062 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "b8517d9395866d57e101cf20c92525e40d8884ef",
          "message": "Update sample files submodule",
          "timestamp": "2022-08-30T15:17:50+02:00",
          "tree_id": "0e9252a02a28faf013b6c4a6dc85a114f18a8165",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b8517d9395866d57e101cf20c92525e40d8884ef"
        },
        "date": 1661865545064,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.044641316330491,
            "unit": "iter/sec",
            "range": "stddev: 0.011395960492420781",
            "extra": "mean: 957.266369200002 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.211344833201185,
            "unit": "iter/sec",
            "range": "stddev: 0.006807675576734895",
            "extra": "mean: 75.69252128571488 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26205038274965425,
            "unit": "iter/sec",
            "range": "stddev: 0.03207313986346202",
            "extra": "mean: 3.816060062600002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4e7602a120d8cfd992b6c1581f4dbe01a4427c74",
          "message": "TST: Catch Exception for sample-files repo (#1307)",
          "timestamp": "2022-08-31T06:19:58+02:00",
          "tree_id": "e82e060bdee42adb77700e42fd066ba73b24ce5c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4e7602a120d8cfd992b6c1581f4dbe01a4427c74"
        },
        "date": 1661919680632,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8097156069444527,
            "unit": "iter/sec",
            "range": "stddev: 0.017057874100227806",
            "extra": "mean: 1.2350015134000016 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.225955910436177,
            "unit": "iter/sec",
            "range": "stddev: 0.01028252216249103",
            "extra": "mean: 97.79036881817986 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20379193155068612,
            "unit": "iter/sec",
            "range": "stddev: 0.044548799544015194",
            "extra": "mean: 4.906965611400002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ediamondscience@gmail.com",
            "name": "Ed Diamond",
            "username": "ediamondscience"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5c76c8f36e2cacab0ce7cd4905ad0f493f6143e3",
          "message": "MAINT: Throw PdfReadError if Trailer can't be read (#1298)\n\nAdded PdfReadError in cases where trailer is absent of can't be read.\r\n\r\nCloses #1279",
          "timestamp": "2022-08-31T06:38:47+02:00",
          "tree_id": "458440a8334b0a238cf48064aac7154cc4a8bc1a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5c76c8f36e2cacab0ce7cd4905ad0f493f6143e3"
        },
        "date": 1661920799639,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9211107561643584,
            "unit": "iter/sec",
            "range": "stddev: 0.022277082492411584",
            "extra": "mean: 1.0856457741999974 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.675130341357066,
            "unit": "iter/sec",
            "range": "stddev: 0.007858374699872533",
            "extra": "mean: 85.65214869230869 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2328902705348256,
            "unit": "iter/sec",
            "range": "stddev: 0.13023745997447359",
            "extra": "mean: 4.293867655800002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c696192d1112200df1048626a8916a18be386e5a",
          "message": "MAINT: PdfReaderProtocol (#1303)\n\nPyPDF2 has some dependencies that make proper typing hard:\r\n\r\n* PdfReader has the pages property which returns a List[PageObject]\r\n* PageObject has the pdf property which returns the PdfReader it belongs to\r\n\r\nThe simplest solution would be to put both classes in the same file, but that makes PRs hard to read. Additionally, bigger files mean merge conflicts happen more often.\r\n\r\nAnother solution is to just not use type annotations for one of the objects (or use `Any` as the type)\r\n\r\nThe solution implemented in this PR is to define a `Protocol` (PEP 544): A protocol just states which methods a class is expected to have (with their function signature). It's duck typing: If it walks like a duck and it quacks like a duck, then it must be a duck.\r\n\r\nSo we define the expected behavior instead of referencing to the specific class.\r\n\r\ntyping.Iterable is an example for a Protocol. In the Java world, one would call this an interface.",
          "timestamp": "2022-08-31T06:45:02+02:00",
          "tree_id": "a9c6ee0b1a1c8c99a7ee19fb9f5db85d7d5ffc1b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/c696192d1112200df1048626a8916a18be386e5a"
        },
        "date": 1661921165154,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0431393577727275,
            "unit": "iter/sec",
            "range": "stddev: 0.007088021372775671",
            "extra": "mean: 958.6446840000008 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.05556465663114,
            "unit": "iter/sec",
            "range": "stddev: 0.006695381598673855",
            "extra": "mean: 76.5956912857142 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25867650116633123,
            "unit": "iter/sec",
            "range": "stddev: 0.03515069578892133",
            "extra": "mean: 3.8658324026 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7a95708b949c673b9d6d7140e9330b94a76f53f1",
          "message": "ENH: Auto-detect RTL for text extraction (#1309)\n\nIncludes some customization capabilities to extend RTL\r\n\r\nCloses #1296",
          "timestamp": "2022-08-31T22:15:10+02:00",
          "tree_id": "37ee256da51944d8c036ea40e505a5ad452d0e75",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7a95708b949c673b9d6d7140e9330b94a76f53f1"
        },
        "date": 1661976985545,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0513173974517462,
            "unit": "iter/sec",
            "range": "stddev: 0.006111518136058924",
            "extra": "mean: 951.1875314000008 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.885752369949303,
            "unit": "iter/sec",
            "range": "stddev: 0.00517029118522961",
            "extra": "mean: 77.6050921428606 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2627351888447409,
            "unit": "iter/sec",
            "range": "stddev: 0.0247952285285272",
            "extra": "mean: 3.8061136933999875 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "yegor.litvinov@yandex.ru",
            "name": "Egor Litvinov",
            "username": "yegorLitvinov"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e3fc7f619eb00730dc308a19f304e719353d42df",
          "message": "DOC: Fix usage of page.scale by replacing it with page.scale_by (#1313)\n\n`scale` accepts two params (`sx` and `sy`)\r\n`scale_by` accepts one (`factor`)",
          "timestamp": "2022-09-02T07:37:41+02:00",
          "tree_id": "920679ae390495d3dc0fe95cfdf2364bd244c99c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e3fc7f619eb00730dc308a19f304e719353d42df"
        },
        "date": 1662097136002,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8714498680723303,
            "unit": "iter/sec",
            "range": "stddev: 0.014916997284713738",
            "extra": "mean: 1.147512939799998 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.810347494899359,
            "unit": "iter/sec",
            "range": "stddev: 0.006672829978836444",
            "extra": "mean: 92.50396441666926 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21816921365621486,
            "unit": "iter/sec",
            "range": "stddev: 0.06394122871532412",
            "extra": "mean: 4.5835981312000005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "475bd68e3af0b4702a451cf7136be9f1c9d48696",
          "message": "ROB: Log errors during Float / NumberObject initialization (#1315)\n\nCloses #1271",
          "timestamp": "2022-09-02T07:40:56+02:00",
          "tree_id": "6c30b44480719c58137f4c58795799b5f75ddacf",
          "url": "https://github.com/py-pdf/PyPDF2/commit/475bd68e3af0b4702a451cf7136be9f1c9d48696"
        },
        "date": 1662097336109,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7869209228838271,
            "unit": "iter/sec",
            "range": "stddev: 0.018711874253653445",
            "extra": "mean: 1.2707757170000036 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.687541663997989,
            "unit": "iter/sec",
            "range": "stddev: 0.006723262350073684",
            "extra": "mean: 103.2253624999953 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.19825733608105625,
            "unit": "iter/sec",
            "range": "stddev: 0.027691494681552718",
            "extra": "mean: 5.043949544399993 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a9fe98d7691c5a65b2edf2627b872f68ac556985",
          "message": "ROB: Accept '/annn' charset as ASCII code (#1316)\n\nCloses #1312",
          "timestamp": "2022-09-02T07:42:25+02:00",
          "tree_id": "5f2a0db1568284abba47fd1f7a85433d1008fea0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a9fe98d7691c5a65b2edf2627b872f68ac556985"
        },
        "date": 1662097409450,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0140705081845194,
            "unit": "iter/sec",
            "range": "stddev: 0.01058528612924594",
            "extra": "mean: 986.1247240000012 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.83446494169072,
            "unit": "iter/sec",
            "range": "stddev: 0.00683727542897707",
            "extra": "mean: 77.91520757142426 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25323584721251885,
            "unit": "iter/sec",
            "range": "stddev: 0.035436951094155254",
            "extra": "mean: 3.9488880069999994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "yegor.litvinov@yandex.ru",
            "name": "Egor Litvinov",
            "username": "yegorLitvinov"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3326cb7bbbd795a71dbf472f78e20521891873f8",
          "message": "BUG: Avoid scaling cropbox twice (#1314)\n\nWhen a PDF document has no crobox, artbox, etc, they are fallback to mediabox.\r\nAs they are lazy, self.cropbox returns the mediabox copy which already was scaled.\r\n\r\nChanging the order avoids this issue",
          "timestamp": "2022-09-02T07:46:02+02:00",
          "tree_id": "e43f028980048fc046779992cf67a4a3e0fa7a5e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3326cb7bbbd795a71dbf472f78e20521891873f8"
        },
        "date": 1662097624898,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0271256102432846,
            "unit": "iter/sec",
            "range": "stddev: 0.007902516062116428",
            "extra": "mean: 973.5907566000037 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.001814298242397,
            "unit": "iter/sec",
            "range": "stddev: 0.006745562700653924",
            "extra": "mean: 76.9123429285697 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2547594364787623,
            "unit": "iter/sec",
            "range": "stddev: 0.021561905482224208",
            "extra": "mean: 3.9252716752000025 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1e089c0a42c267d6ffd9674171ecffdb9a2cbd80",
          "message": "ROB: Cope with 2 digit codes in bfchar (#1310)\n\nFixes #1293",
          "timestamp": "2022-09-02T07:56:23+02:00",
          "tree_id": "c01ed851700527cc0d18314b317547bc4b8a2e76",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1e089c0a42c267d6ffd9674171ecffdb9a2cbd80"
        },
        "date": 1662098262509,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8225284417964308,
            "unit": "iter/sec",
            "range": "stddev: 0.007162297000818019",
            "extra": "mean: 1.2157634304000056 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.251639377629775,
            "unit": "iter/sec",
            "range": "stddev: 0.006783227310916198",
            "extra": "mean: 97.54537427273456 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2125065141125252,
            "unit": "iter/sec",
            "range": "stddev: 0.055972676855762134",
            "extra": "mean: 4.705738100200006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "markdlevy@gmail.com",
            "name": "Mark Levy",
            "username": "markdlevy"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b219dfd228b5f455c54758606d4c7a9b2cb259ba",
          "message": "DOC: Fix AnnotationBuilder.free_text example (#1311)\n\nModify sample code for annotation builder to use the parameter background_color property instead of bg_color",
          "timestamp": "2022-09-02T07:59:01+02:00",
          "tree_id": "809a8b61291c5a4be45823d66987ec689009a01a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b219dfd228b5f455c54758606d4c7a9b2cb259ba"
        },
        "date": 1662098414880,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9309089981837798,
            "unit": "iter/sec",
            "range": "stddev: 0.01730413885286789",
            "extra": "mean: 1.0742188570000053 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.186570015570924,
            "unit": "iter/sec",
            "range": "stddev: 0.006423409286983406",
            "extra": "mean: 89.39290583334032 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22742819353663987,
            "unit": "iter/sec",
            "range": "stddev: 0.1983402087486978",
            "extra": "mean: 4.396992230600006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "ba2d32a1ff19ad065f0feddd200d23b0c4e76434",
          "message": "DEV: Only run coverage for PyPDF2",
          "timestamp": "2022-09-02T19:41:38+02:00",
          "tree_id": "de1940be9269e59d0994edb1996c4d88f232f488",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ba2d32a1ff19ad065f0feddd200d23b0c4e76434"
        },
        "date": 1662140594991,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7967690630768284,
            "unit": "iter/sec",
            "range": "stddev: 0.01617220202847135",
            "extra": "mean: 1.2550688101999952 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.767416458987633,
            "unit": "iter/sec",
            "range": "stddev: 0.009996480809733154",
            "extra": "mean: 102.38121863636061 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20075190918529587,
            "unit": "iter/sec",
            "range": "stddev: 0.04733865141501659",
            "extra": "mean: 4.981272676600005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eb0be4d2ffad84bbe051395802cc7e9e6b526983",
          "message": "ROB: MultiLine bfrange in cmap (#1299)\n\nROB : ending list with only one item on the line\r\n\r\nFixes #1274\r\nFixes #1285",
          "timestamp": "2022-09-02T21:17:04+02:00",
          "tree_id": "1146299b373ca9dcdf07308e045ba12cd74a279a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/eb0be4d2ffad84bbe051395802cc7e9e6b526983"
        },
        "date": 1662146287155,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0601241287553784,
            "unit": "iter/sec",
            "range": "stddev: 0.0068229316191296555",
            "extra": "mean: 943.2857651999996 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.011905546901044,
            "unit": "iter/sec",
            "range": "stddev: 0.0047855996628543215",
            "extra": "mean: 76.85269435714304 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2663104059654887,
            "unit": "iter/sec",
            "range": "stddev: 0.013358065324864617",
            "extra": "mean: 3.7550166182000053 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1252a49c5c9cd7d2e3c6559a32c550c849c26550",
          "message": "ENH:  Process XRefStm (#1297)\n\nFixes #1273\r\nFixes #1279\r\nFixes #1292\r\nFixes #1294\r\nFixes #1295\r\n\r\nROB: Cope with xref starting on \\r\\n\r\nROB: Escaped octal code followed by decimal int\r\nROB: Cope with some corrupted entries in xref table\r\nROB: Extend xref autorepair cases",
          "timestamp": "2022-09-03T11:34:26+02:00",
          "tree_id": "a6699f20448e00127832ba3fe23409e7c70d66ad",
          "url": "https://github.com/py-pdf/PyPDF2/commit/1252a49c5c9cd7d2e3c6559a32c550c849c26550"
        },
        "date": 1662197726196,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0641480573897524,
            "unit": "iter/sec",
            "range": "stddev: 0.009059001811701621",
            "extra": "mean: 939.7188605999986 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.04685515975275,
            "unit": "iter/sec",
            "range": "stddev: 0.0048378466602849775",
            "extra": "mean: 76.6468231428539 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2680376474117465,
            "unit": "iter/sec",
            "range": "stddev: 0.014450287737417916",
            "extra": "mean: 3.7308191952000245 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "exiledkingcc@gmail.com",
            "name": "exiledkingcc",
            "username": "exiledkingcc"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a61ef5f6f2321e324cbf3e67f65cf6d80acf2c9c",
          "message": "ROB: Crop data of /U and /O in encryption dictionary to 48 bytes (#1317)\n\nThe specification says:\r\n\r\nTo understand the algorithm below, it is necessary to treat the O and U strings in the Encrypt dictionary\r\nas made up of three sections. The first 32 bytes are a hash value (explained below). The next 8 bytes are\r\ncalled the Validation Salt. The final 8 bytes are called the Key Salt.\r\n\r\nSo /U and /O should be 48-bytes data, but for the PDF file which causes #1288 , /O 's length is 127-bytes. The redundant data are zeros.\r\n\r\nFixes #1288",
          "timestamp": "2022-09-03T14:09:28+02:00",
          "tree_id": "9caeea8f827caf3f0a92636bd1c9eedda219b9e2",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a61ef5f6f2321e324cbf3e67f65cf6d80acf2c9c"
        },
        "date": 1662207042522,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0286415697238571,
            "unit": "iter/sec",
            "range": "stddev: 0.019335938131490853",
            "extra": "mean: 972.1559281999987 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.988821120075627,
            "unit": "iter/sec",
            "range": "stddev: 0.007533205810339809",
            "extra": "mean: 76.98928107142778 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25688677950239697,
            "unit": "iter/sec",
            "range": "stddev: 0.02390360262005744",
            "extra": "mean: 3.8927655286000005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b4b8f2d74a1ba107b1858cb93280b1d71b3b2260",
          "message": "ROB: Fix offset correction in revised PDF (#1318)\n\nThe problem is observed in PDF files where the xref table in previous versions are not starting at 0 where _zero_xref was changing index.\r\n\r\nFixes #328",
          "timestamp": "2022-09-03T16:54:05+02:00",
          "tree_id": "f29db2bbc34649ef3b8bff62067e287020f9ca1f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/b4b8f2d74a1ba107b1858cb93280b1d71b3b2260"
        },
        "date": 1662216908898,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0522142758604975,
            "unit": "iter/sec",
            "range": "stddev: 0.006153900146864961",
            "extra": "mean: 950.3767653999972 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.079396098234664,
            "unit": "iter/sec",
            "range": "stddev: 0.0044826547495367495",
            "extra": "mean: 76.45612935714752 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26456509646152054,
            "unit": "iter/sec",
            "range": "stddev: 0.01924222494581255",
            "extra": "mean: 3.779788087599999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3ec834de9bf4cc6a9830aef9e8eb7131fa642cf0",
          "message": "DOC: Creating a coverage report (#1319)",
          "timestamp": "2022-09-03T16:54:39+02:00",
          "tree_id": "135c9969d86e90b811fa7dfbb474e6a376a30b97",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3ec834de9bf4cc6a9830aef9e8eb7131fa642cf0"
        },
        "date": 1662216965263,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7570694202561844,
            "unit": "iter/sec",
            "range": "stddev: 0.014941045230091717",
            "extra": "mean: 1.3208828321999988 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.68195774754705,
            "unit": "iter/sec",
            "range": "stddev: 0.00645306975140907",
            "extra": "mean: 103.28489610000133 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1928527473396932,
            "unit": "iter/sec",
            "range": "stddev: 0.06935520650738101",
            "extra": "mean: 5.185303366400001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "704be2de0e77deac66dd2caa1069afb7f84c60db",
          "message": "STY: Minor changes (#1320)\n\nTST: xmp",
          "timestamp": "2022-09-04T11:08:47+02:00",
          "tree_id": "cc91c99ec273285d0004167b1199394300470e74",
          "url": "https://github.com/py-pdf/PyPDF2/commit/704be2de0e77deac66dd2caa1069afb7f84c60db"
        },
        "date": 1662282602162,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.040811809764208,
            "unit": "iter/sec",
            "range": "stddev: 0.018248471253927184",
            "extra": "mean: 960.7884831999996 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.192735486545178,
            "unit": "iter/sec",
            "range": "stddev: 0.005516595799658209",
            "extra": "mean: 75.79929128571295 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25959950040040836,
            "unit": "iter/sec",
            "range": "stddev: 0.02066518365864261",
            "extra": "mean: 3.8520875366000014 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "421970f363a111df3462c610a3beb36d8e66e07a",
          "message": "STY: Tiny stylistic changes that hopefully make the code easier to read (#1323)",
          "timestamp": "2022-09-04T13:06:01+02:00",
          "tree_id": "1d2f825110057f2d2a40b24f1fb509d228e4676b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/421970f363a111df3462c610a3beb36d8e66e07a"
        },
        "date": 1662289637319,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8430008917256695,
            "unit": "iter/sec",
            "range": "stddev: 0.02089051785404179",
            "extra": "mean: 1.186238365599999 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.837280213590509,
            "unit": "iter/sec",
            "range": "stddev: 0.0063538360942714854",
            "extra": "mean: 92.27407433333212 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21757752763880725,
            "unit": "iter/sec",
            "range": "stddev: 0.046808538210503355",
            "extra": "mean: 4.596062887799997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6e251fa5a252d323aa4f33ba6a6354a5c4e16c17",
          "message": "DOC: Migration guide (PyPDF2 1.x ➔ 2.x) (#1324)",
          "timestamp": "2022-09-04T16:25:27+02:00",
          "tree_id": "f5f4456f534fd4bf1718ce7855bcf34e087553b3",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6e251fa5a252d323aa4f33ba6a6354a5c4e16c17"
        },
        "date": 1662301598248,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0299821078161924,
            "unit": "iter/sec",
            "range": "stddev: 0.007728555675876471",
            "extra": "mean: 970.8906517999992 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.977029053131897,
            "unit": "iter/sec",
            "range": "stddev: 0.006886942296175638",
            "extra": "mean: 77.05924028571535 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25722826113086733,
            "unit": "iter/sec",
            "range": "stddev: 0.016684339404831678",
            "extra": "mean: 3.8875977141999982 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "4073b2a36ef476b865e927f4c84be4bedd21f0f8",
          "message": "REL: 2.10.5\n\nVersion 2.10.5, 2022-09-04\n--------------------------\n\nNew Features (ENH):\n-  Process XRefStm (#1297)\n-  Auto-detect RTL for text extraction (#1309)\n\nBug Fixes (BUG):\n-  Avoid scaling cropbox twice (#1314)\n\nRobustness (ROB):\n-  Fix offset correction in revised PDF (#1318)\n-  Crop data of /U and /O in encryption dictionary to 48 bytes (#1317)\n-  MultiLine bfrange in cmap (#1299)\n-  Cope with 2 digit codes in bfchar (#1310)\n-  Accept '/annn' charset as ASCII code (#1316)\n-  Log errors during Float / NumberObject initialization (#1315)\n-  Cope with corrupted entries in xref table (#1300)\n\nDocumentation (DOC):\n-  Migration guide (PyPDF2 1.x \\xe2\\x9e\\x94 2.x) (#1324)\n-  Creating a coverage report (#1319)\n-  Fix AnnotationBuilder.free_text example (#1311)\n-  Fix usage of page.scale by replacing it with page.scale_by (#1313)\n\nDeveloper Experience (DEV):\n-  Only run coverage for PyPDF2\n\nMaintenance (MAINT):\n-  PdfReaderProtocol (#1303)\n-  Throw PdfReadError if Trailer can't be read (#1298)\n-  Remove catching OverflowException (#1302)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.4...2.10.5",
          "timestamp": "2022-09-04T17:27:10+02:00",
          "tree_id": "74475491b489c12227e34c4a74fe104a3dd13a68",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4073b2a36ef476b865e927f4c84be4bedd21f0f8"
        },
        "date": 1662305449811,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0553666856911397,
            "unit": "iter/sec",
            "range": "stddev: 0.005881995922592149",
            "extra": "mean: 947.5379634000092 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.967851975237185,
            "unit": "iter/sec",
            "range": "stddev: 0.004936419985800421",
            "extra": "mean: 77.11377350000248 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26515859642476325,
            "unit": "iter/sec",
            "range": "stddev: 0.01562448075170397",
            "extra": "mean: 3.7713278523999976 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5049c1e7d0379d783bf809f6545d3583b51dab25",
          "message": "ROB: Fix image extraction issue with superfluous whitespaces (#1327)\n\nFix some images reading when some operations are inserted between EI and Q\r\nend of image is now considered with [whitespace]EI[whitespace] (4 characters should be sufficient)\r\n\r\nFixes #1090",
          "timestamp": "2022-09-06T21:12:20+02:00",
          "tree_id": "b128cbaa7fa7c9f6c28ab5a926355235621fd287",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5049c1e7d0379d783bf809f6545d3583b51dab25"
        },
        "date": 1662491627088,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8292465173651408,
            "unit": "iter/sec",
            "range": "stddev: 0.045797761839791944",
            "extra": "mean: 1.2059140183999972 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.3474308992661,
            "unit": "iter/sec",
            "range": "stddev: 0.009119273076981772",
            "extra": "mean: 96.64234627272802 msec\nrounds: 11"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2146879695554501,
            "unit": "iter/sec",
            "range": "stddev: 0.09901607838831915",
            "extra": "mean: 4.6579228546 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bfbe0b2528c74a12757cce1e811aed638f0c386e",
          "message": "DOC: Update migration guide (#1326)",
          "timestamp": "2022-09-07T20:25:41+02:00",
          "tree_id": "2161e3f8ea1dfccd85e7185cf4cd1128981775d7",
          "url": "https://github.com/py-pdf/PyPDF2/commit/bfbe0b2528c74a12757cce1e811aed638f0c386e"
        },
        "date": 1662575217417,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8891542610484456,
            "unit": "iter/sec",
            "range": "stddev: 0.021353915355282548",
            "extra": "mean: 1.1246642386000048 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.320641950899935,
            "unit": "iter/sec",
            "range": "stddev: 0.005819671925433987",
            "extra": "mean: 88.33421323077044 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21906988769156338,
            "unit": "iter/sec",
            "range": "stddev: 0.03924893089316149",
            "extra": "mean: 4.564753333000001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "2f776987cc0f58b6661ae4b681b9843777543fcc",
          "message": "DOC: Added Timo Stüber as a contributor",
          "timestamp": "2022-09-08T19:36:34+02:00",
          "tree_id": "9ac148f4044046be9d58de86e6799b4b4b3402b5",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2f776987cc0f58b6661ae4b681b9843777543fcc"
        },
        "date": 1662658668306,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9690690018952417,
            "unit": "iter/sec",
            "range": "stddev: 0.010087359544627915",
            "extra": "mean: 1.0319182618000013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.198472342895595,
            "unit": "iter/sec",
            "range": "stddev: 0.008766480454203958",
            "extra": "mean: 81.9774781538445 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2620642971833742,
            "unit": "iter/sec",
            "range": "stddev: 0.049913376758489454",
            "extra": "mean: 3.8158574470000017 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e6531a25325e7e0174b6a1ba03b57320b5227f6b",
          "message": "ROB: Fix infinite loop due to Invalid object (#1331)\n\nFixes #1329\r\n\r\n* Prevent loop within dictionaries caused by objects not respecting the PDF standard\r\n* Fix cmap warnings due to \"numbered\" characters ( #2d instead of -)\r\n* Apply unnumbering to NameObject\r\n* Add _get_indirect_object for debugging and development\r\n* Add some missing seeks (no issue reported yet)",
          "timestamp": "2022-09-09T08:06:35+02:00",
          "tree_id": "cc954c99d0488fe2494f4e966a6903608975177a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e6531a25325e7e0174b6a1ba03b57320b5227f6b"
        },
        "date": 1662703661148,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0422303387063234,
            "unit": "iter/sec",
            "range": "stddev: 0.013902408031828246",
            "extra": "mean: 959.4808008000016 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.082988064089117,
            "unit": "iter/sec",
            "range": "stddev: 0.0058102600128795276",
            "extra": "mean: 76.43513814285693 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25556546595554336,
            "unit": "iter/sec",
            "range": "stddev: 0.02544385496308365",
            "extra": "mean: 3.912891736999998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "0ceaa6034e1e72d52a0a08992cc0bce3ca001ef8",
          "message": "REL: 2.10.6\n\nRobustness (ROB):\n-  Fix infinite loop due to Invalid object (#1331)\n-  Fix image extraction issue with superfluous whitespaces (#1327)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.5...2.10.6",
          "timestamp": "2022-09-09T16:04:55+02:00",
          "tree_id": "6f31b908164a782f72c5cd4bf209a3c929bb6d72",
          "url": "https://github.com/py-pdf/PyPDF2/commit/0ceaa6034e1e72d52a0a08992cc0bce3ca001ef8"
        },
        "date": 1662732407001,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0494997827747492,
            "unit": "iter/sec",
            "range": "stddev: 0.007430763104365055",
            "extra": "mean: 952.8348803999961 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.063564509299399,
            "unit": "iter/sec",
            "range": "stddev: 0.006188811198812502",
            "extra": "mean: 76.54878569230797 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25554098356379396,
            "unit": "iter/sec",
            "range": "stddev: 0.026143391410957",
            "extra": "mean: 3.9132666160000014 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mgorny@gentoo.org",
            "name": "Michał Górny",
            "username": "mgorny"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2bbccf743305748b6460170ef2e3b73828470541",
          "message": "TST: Use pytest.warns() for warnings, and .raises() for exceptions (#1325)\n\nReplace the warning-as-exception checks with use of `pytest.warns()`.\r\n\r\nThat is more semantically correct and works correctly when the tests\r\nare run without -Werror (e.g. because -Werror tends to cause test suites\r\nto crash on irrelevant deprecation warnings from other components).\r\n\r\nWhile at it, replace the homegrown exception checks in test_orientations\r\nwith `pytest.raises()`.",
          "timestamp": "2022-09-10T18:54:59+02:00",
          "tree_id": "7ec6063f7081b18a9face80398202f2798ae1a09",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2bbccf743305748b6460170ef2e3b73828470541"
        },
        "date": 1662828977419,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9115532677130727,
            "unit": "iter/sec",
            "range": "stddev: 0.032870517787145344",
            "extra": "mean: 1.0970285944000011 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.177973103055768,
            "unit": "iter/sec",
            "range": "stddev: 0.006943427400421153",
            "extra": "mean: 89.46165738461349 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22211418479684508,
            "unit": "iter/sec",
            "range": "stddev: 0.06513811632151847",
            "extra": "mean: 4.502188822000008 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d3a4a990c005625125fb65864c42d3d5871baf4c",
          "message": "BUG: Decode #23 in NameObject (#1342)\n\nFixes #1340",
          "timestamp": "2022-09-10T20:47:55+02:00",
          "tree_id": "bd919bfc5c3ea87d3558dec99b50e02d42ebd55c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d3a4a990c005625125fb65864c42d3d5871baf4c"
        },
        "date": 1662835752534,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8288893557812607,
            "unit": "iter/sec",
            "range": "stddev: 0.009274339813885634",
            "extra": "mean: 1.2064336368000057 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.219120256866082,
            "unit": "iter/sec",
            "range": "stddev: 0.009117496791860174",
            "extra": "mean: 97.85578159999773 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.20656773506370676,
            "unit": "iter/sec",
            "range": "stddev: 0.10303899849451936",
            "extra": "mean: 4.841027083399998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "95012cc4632c83522588ad32137a53d5280b606e",
          "message": "BUG: Fix Error in transformations (#1341)\n\nError detected during analysis of #1280",
          "timestamp": "2022-09-10T21:08:20+02:00",
          "tree_id": "9cb3f4792237b6766046c2b7ab87804e6ddc93a8",
          "url": "https://github.com/py-pdf/PyPDF2/commit/95012cc4632c83522588ad32137a53d5280b606e"
        },
        "date": 1662836973280,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9479814562124197,
            "unit": "iter/sec",
            "range": "stddev: 0.008641641628737656",
            "extra": "mean: 1.0548729550000018 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.735828829383324,
            "unit": "iter/sec",
            "range": "stddev: 0.005143876505672406",
            "extra": "mean: 85.20915007692273 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2344449426630794,
            "unit": "iter/sec",
            "range": "stddev: 0.017148262135389936",
            "extra": "mean: 4.265393779200002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "725294e7c071bb3aaa86668e24dbfcfc6938d175",
          "message": "DOC: Mention contributor",
          "timestamp": "2022-09-10T21:10:09+02:00",
          "tree_id": "e63a6615f8710b40f11ce1747e83272bdbf9ddab",
          "url": "https://github.com/py-pdf/PyPDF2/commit/725294e7c071bb3aaa86668e24dbfcfc6938d175"
        },
        "date": 1662837117695,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8814924014863998,
            "unit": "iter/sec",
            "range": "stddev: 0.037319460074302487",
            "extra": "mean: 1.1344397278000002 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.243387114029737,
            "unit": "iter/sec",
            "range": "stddev: 0.008895535905427196",
            "extra": "mean: 88.9411695833348 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22747482691046428,
            "unit": "iter/sec",
            "range": "stddev: 0.10782029248952642",
            "extra": "mean: 4.396090827200001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "7e2362448a6d288fb0d9b43ba9aec51e3f024b99",
          "message": "DOC: Add sietzeberends as a contributor",
          "timestamp": "2022-09-11T18:21:23+02:00",
          "tree_id": "6bf62b2d738e3841d908f90b1be2b0b7ff1ad4ab",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7e2362448a6d288fb0d9b43ba9aec51e3f024b99"
        },
        "date": 1662913350318,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0295491729714825,
            "unit": "iter/sec",
            "range": "stddev: 0.012065061460089448",
            "extra": "mean: 971.298920199996 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 13.137549352529707,
            "unit": "iter/sec",
            "range": "stddev: 0.006067631200668945",
            "extra": "mean: 76.11769692857096 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2575495599872805,
            "unit": "iter/sec",
            "range": "stddev: 0.026250994937033246",
            "extra": "mean: 3.8827478488 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "e23b9854e419a66f5b1cba645372cb35be8d6053",
          "message": "REL: 2.10.7\n\nBug Fixes (BUG):\n-  Fix Error in transformations (#1341)\n-  Decode #23 in NameObject (#1342)\n\nTesting (TST):\n-  Use pytest.warns() for warnings, and .raises() for exceptions (#1325)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.6...2.10.7",
          "timestamp": "2022-09-11T22:19:06+02:00",
          "tree_id": "2ce9e5c0e3080056107ab2adfa7aadccec9115b1",
          "url": "https://github.com/py-pdf/PyPDF2/commit/e23b9854e419a66f5b1cba645372cb35be8d6053"
        },
        "date": 1662927664330,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0585717828094796,
            "unit": "iter/sec",
            "range": "stddev: 0.012322810822143038",
            "extra": "mean: 944.6690495999917 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.949241850377343,
            "unit": "iter/sec",
            "range": "stddev: 0.00453974619900126",
            "extra": "mean: 77.22459828571816 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26186914662466326,
            "unit": "iter/sec",
            "range": "stddev: 0.016786024806938984",
            "extra": "mean: 3.8187011066000025 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fb8be4065bfb26ec3bec71d8c6d65b3be3a2034f",
          "message": "ROB: Improve NameObject reading/writing (#1345)\n\nThree kinds of changes were made in this PR\r\n\r\n1) _cmap.py : the str is coming from `/Encoding` which stores a NameObject : The conversion is already performed; no need to force it.\r\n2) _page.py : Replaced obsolete call in _debug_for_extract()\r\n3) _base.py :\r\n3.1) unnumber : all `#xx` should be performed prior to conversion to str (using utf-8) to allow multi language text\r\n3.2) read_from_stream : if utf-8 (normally the only one required) or gbk (kept to prevent regression) we will use charmap to get some sequence of chars\r\n3.3) renumber : added to recode in #xx sequence. renumber will also be compatible with utf-8 chars\r\n\r\nCloses #1344",
          "timestamp": "2022-09-14T06:01:29+02:00",
          "tree_id": "e59fb626573c7fa27583dcf0dbf9d357dafb238e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/fb8be4065bfb26ec3bec71d8c6d65b3be3a2034f"
        },
        "date": 1663128156045,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0094067154877042,
            "unit": "iter/sec",
            "range": "stddev: 0.011447237489045643",
            "extra": "mean: 990.6809462000069 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.210191939633464,
            "unit": "iter/sec",
            "range": "stddev: 0.008486277987090545",
            "extra": "mean: 81.89879446154052 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.24724322397220874,
            "unit": "iter/sec",
            "range": "stddev: 0.017219825674530575",
            "extra": "mean: 4.044600227799992 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3cf80bf3a76e878c742d81b22029b334c7dea78a",
          "message": "ENH: Add PageObject.user_unit property (#1336)\n\nCo-authored-by: Matthew Peveler <matt.peveler@gmail.com>",
          "timestamp": "2022-09-14T06:10:10+02:00",
          "tree_id": "74d7c7594da4d6a27fb63891b61ced2762488b3d",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3cf80bf3a76e878c742d81b22029b334c7dea78a"
        },
        "date": 1663128677834,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.972632710888716,
            "unit": "iter/sec",
            "range": "stddev: 0.01765523186575038",
            "extra": "mean: 1.0281373316000013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.314642696435117,
            "unit": "iter/sec",
            "range": "stddev: 0.007632295864917567",
            "extra": "mean: 88.38104983333395 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.24281006962622206,
            "unit": "iter/sec",
            "range": "stddev: 0.052753750665905014",
            "extra": "mean: 4.118445341 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "7c96d13ad9404076730846a11284ed0f611cab4d",
          "message": "DOC: Add Antoine Mérino as a contributor",
          "timestamp": "2022-09-14T13:17:56+02:00",
          "tree_id": "5ee5bc6f0bed3a809a0799badbd3dd54d4e5b81f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7c96d13ad9404076730846a11284ed0f611cab4d"
        },
        "date": 1663154348624,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.4684095944166569,
            "unit": "iter/sec",
            "range": "stddev: 0.005770408644948413",
            "extra": "mean: 681.0088982000025 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 18.378171551533548,
            "unit": "iter/sec",
            "range": "stddev: 0.0033648545881603477",
            "extra": "mean: 54.412377052632095 msec\nrounds: 19"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.36223994359127704,
            "unit": "iter/sec",
            "range": "stddev: 0.010577205321008438",
            "extra": "mean: 2.760601136600002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "61194539+mergezalot@users.noreply.github.com",
            "name": "Michael Karlen",
            "username": "mergezalot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3be01fda141817c90a0df18fb22e1747ac5832b3",
          "message": "PI: Avoid string concatenation with large embedded base64-encoded images (#1350)\n\nCertain PDF libraries do embed images as base64 strings. This causes performance issues\r\nin `read_string_from_stream` due to incremental string concatenation, byte by byte.\r\n\r\nAn example for such a library is `Canon iR-ADV C256  PDF` (PDF Annotator 8.0.0.826  - Adobe PSL 1.3e for Canon)\r\n\r\nCo-authored-by: Michael Karlen <michael.karlen@gmail.com>",
          "timestamp": "2022-09-17T12:05:58+02:00",
          "tree_id": "0a34ecc10845d4069225da588f97779474d9e2e5",
          "url": "https://github.com/py-pdf/PyPDF2/commit/3be01fda141817c90a0df18fb22e1747ac5832b3"
        },
        "date": 1663409221842,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.038997853272714,
            "unit": "iter/sec",
            "range": "stddev: 0.00926400754964586",
            "extra": "mean: 962.4658962000012 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.307017853985258,
            "unit": "iter/sec",
            "range": "stddev: 0.004912545069790154",
            "extra": "mean: 81.25445269230515 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25924081422539946,
            "unit": "iter/sec",
            "range": "stddev: 0.018530878962134206",
            "extra": "mean: 3.8574172935999966 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6f51189d880980b19fed900e43f73f91ac119239",
          "message": "ROB: Fix merge_page for pages without resources (#1349)\n\nCloses #270",
          "timestamp": "2022-09-17T12:08:10+02:00",
          "tree_id": "8e336e7fe908841403757236d7e4cd7178f7b947",
          "url": "https://github.com/py-pdf/PyPDF2/commit/6f51189d880980b19fed900e43f73f91ac119239"
        },
        "date": 1663409395124,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9046985162073656,
            "unit": "iter/sec",
            "range": "stddev: 0.013548143552784405",
            "extra": "mean: 1.1053405991999994 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.895769780578323,
            "unit": "iter/sec",
            "range": "stddev: 0.007673579328333105",
            "extra": "mean: 91.77873799999858 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22476176220917615,
            "unit": "iter/sec",
            "range": "stddev: 0.028210089859163425",
            "extra": "mean: 4.449155364199996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "71de6c8d2792c25e40d4d82dba1de4a788991196",
          "message": "ENH: Add rotation property and transfer_rotate_to_content (#1348)\n\nSee #1280 for the context of this change",
          "timestamp": "2022-09-17T13:07:55+02:00",
          "tree_id": "8503b9a1c67a60c71ea311f2d2231e436638690c",
          "url": "https://github.com/py-pdf/PyPDF2/commit/71de6c8d2792c25e40d4d82dba1de4a788991196"
        },
        "date": 1663412936246,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0316565504419797,
            "unit": "iter/sec",
            "range": "stddev: 0.008347614800685934",
            "extra": "mean: 969.3148360000066 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.494743497452962,
            "unit": "iter/sec",
            "range": "stddev: 0.006482750419340068",
            "extra": "mean: 80.03365576923198 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2571593506264986,
            "unit": "iter/sec",
            "range": "stddev: 0.022491068636409234",
            "extra": "mean: 3.888639466400008 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "donald.ness@gmail.com",
            "name": "programmarchy",
            "username": "programmarchy"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5aeb92633769785e50470a3acecffe883112a99d",
          "message": "BUG: Format floats using their intrinsic decimal precision (#1267)\n\nSince FloatObject is represented as a decimal, format numbers using their intrinsic precision, instead of reducing the precision to 5 decimal places.\r\n\r\nThis fixes rendering issues for PDFs that contain coordinates, transformations, etc. with real numbers containing more than 5 decimal places of precision. For example, PDFs exported from Microsoft PowerPoint contain numbers with up to 11 decimal places.\r\n\r\nFixes #1266",
          "timestamp": "2022-09-18T11:46:22+02:00",
          "tree_id": "06a28811e5f006d4820d8ff85db228fd9dbc6228",
          "url": "https://github.com/py-pdf/PyPDF2/commit/5aeb92633769785e50470a3acecffe883112a99d"
        },
        "date": 1663494444144,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0396376033570993,
            "unit": "iter/sec",
            "range": "stddev: 0.007102140060710866",
            "extra": "mean: 961.8736344000013 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.72215104370597,
            "unit": "iter/sec",
            "range": "stddev: 0.0059802404773838195",
            "extra": "mean: 78.60305985714027 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2583919497943388,
            "unit": "iter/sec",
            "range": "stddev: 0.022775210705508486",
            "extra": "mean: 3.870089609200005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "620d2fa03c8b87e2923d9f41e2bc0da8a4321c6a",
          "message": "REL: 2.10.9\n\nNew Features (ENH):\n-  Add rotation property and transfer_rotate_to_content (#1348)\n\nPerformance Improvements (PI):\n-  Avoid string concatenation with large embedded base64-encoded images (#1350)\n\nBug Fixes (BUG):\n-  Format floats using their intrinsic decimal precision (#1267)\n\nRobustness (ROB):\n-  Fix merge_page for pages without resources (#1349)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.8...2.10.9",
          "timestamp": "2022-09-18T12:00:04+02:00",
          "tree_id": "5e6d728dcbf9c03d3f94a42dc407e4fed5acaedf",
          "url": "https://github.com/py-pdf/PyPDF2/commit/620d2fa03c8b87e2923d9f41e2bc0da8a4321c6a"
        },
        "date": 1663495297665,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0514339613554329,
            "unit": "iter/sec",
            "range": "stddev: 0.006172719079493318",
            "extra": "mean: 951.0820810000013 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.477429613564272,
            "unit": "iter/sec",
            "range": "stddev: 0.005006332828891026",
            "extra": "mean: 80.14471176923294 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.26020978018594915,
            "unit": "iter/sec",
            "range": "stddev: 0.014044998689420704",
            "extra": "mean: 3.843053090799998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "141a765621235a395ce04ef078ab2060d359d2fa",
          "message": "ROB: Ensure update_page_form_field_values does not fail if no fields (#1346)\n\nFixes #1343",
          "timestamp": "2022-09-18T12:14:55+02:00",
          "tree_id": "4664a0ee539525ad560b95fff6b3a45848c3a391",
          "url": "https://github.com/py-pdf/PyPDF2/commit/141a765621235a395ce04ef078ab2060d359d2fa"
        },
        "date": 1663496156808,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0496911813582968,
            "unit": "iter/sec",
            "range": "stddev: 0.005277649554666396",
            "extra": "mean: 952.6611423999996 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.840812875698955,
            "unit": "iter/sec",
            "range": "stddev: 0.005431720126884577",
            "extra": "mean: 77.87668971428475 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2586209455070898,
            "unit": "iter/sec",
            "range": "stddev: 0.01736674794806411",
            "extra": "mean: 3.866662841400006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7803a72c1e446b957b7919b8097f272b14ae9fdc",
          "message": "BUG: Errors in transfer_rotation_to_content() (#1356)\n\nSee https://github.com/py-pdf/PyPDF2/issues/1280#issuecomment-1251018614",
          "timestamp": "2022-09-22T09:33:39+02:00",
          "tree_id": "344d41bf9f4db99a1cef993c015d8fd5a54fd872",
          "url": "https://github.com/py-pdf/PyPDF2/commit/7803a72c1e446b957b7919b8097f272b14ae9fdc"
        },
        "date": 1663832084623,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0415303264411961,
            "unit": "iter/sec",
            "range": "stddev: 0.008916489979658044",
            "extra": "mean: 960.1256676000005 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.81585438654046,
            "unit": "iter/sec",
            "range": "stddev: 0.005514018390088257",
            "extra": "mean: 78.02835221428747 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2585361207204495,
            "unit": "iter/sec",
            "range": "stddev: 0.025972699888375538",
            "extra": "mean: 3.8679314798000006 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "4ff5e0a3faf40b8eb1632c0708366591c1b41ea3",
          "message": "DOC: Add programmarchy to contributors",
          "timestamp": "2022-09-24T05:19:12+02:00",
          "tree_id": "d7b03b26bf8489bd015eaa159c1fa135e11e727a",
          "url": "https://github.com/py-pdf/PyPDF2/commit/4ff5e0a3faf40b8eb1632c0708366591c1b41ea3"
        },
        "date": 1663989625665,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0105865581520175,
            "unit": "iter/sec",
            "range": "stddev: 0.007533782838037952",
            "extra": "mean: 989.5243429999937 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.343171355835286,
            "unit": "iter/sec",
            "range": "stddev: 0.007971191854074508",
            "extra": "mean: 81.01645607692595 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.24961003143976856,
            "unit": "iter/sec",
            "range": "stddev: 0.008814258450953053",
            "extra": "mean: 4.006249245000004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dcab241e4ab386834d6864538b99b556b04a3f7c",
          "message": "BUG: 'IndexError: index out of range' when using extract_text (#1361)\n\nFixes #1358\r\n\r\nCo-authored-by: diavral <73272031+diavral@users.noreply.github.com>",
          "timestamp": "2022-09-24T06:45:33+02:00",
          "tree_id": "3bb00ebf8c23f6bf4ff934d6226ef3e0540fc0c4",
          "url": "https://github.com/py-pdf/PyPDF2/commit/dcab241e4ab386834d6864538b99b556b04a3f7c"
        },
        "date": 1663994813953,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.7740802987014608,
            "unit": "iter/sec",
            "range": "stddev: 0.014000307163367968",
            "extra": "mean: 1.2918556404000014 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.074723471872899,
            "unit": "iter/sec",
            "range": "stddev: 0.010185591047150866",
            "extra": "mean: 110.1961953 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1995728793205561,
            "unit": "iter/sec",
            "range": "stddev: 0.10213553189027288",
            "extra": "mean: 5.0107008697999955 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "85b3e8785830bf35fc1c21f5c2edf29636281290",
          "message": "ENH: Add PageObject.images attribute (#1330)",
          "timestamp": "2022-09-24T07:39:46+02:00",
          "tree_id": "d18a824240011eb5290e06b4b24ba84a926adbb0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/85b3e8785830bf35fc1c21f5c2edf29636281290"
        },
        "date": 1663998066961,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8860711255285805,
            "unit": "iter/sec",
            "range": "stddev: 0.011808193474007207",
            "extra": "mean: 1.1285775726000054 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.642001788987075,
            "unit": "iter/sec",
            "range": "stddev: 0.00791500847486989",
            "extra": "mean: 93.96728358332496 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21952163398681096,
            "unit": "iter/sec",
            "range": "stddev: 0.042785993240842736",
            "extra": "mean: 4.555359678399992 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2845c6d94a3fb56a13393191fc8e050ad9d6bb37",
          "message": "ENH: Add metadata.creation_date and modification_date (#1364)\n\nCloses #1222",
          "timestamp": "2022-09-24T14:58:13+02:00",
          "tree_id": "73d2b462ba8d45e7776ec0f72aeb43b2dba94978",
          "url": "https://github.com/py-pdf/PyPDF2/commit/2845c6d94a3fb56a13393191fc8e050ad9d6bb37"
        },
        "date": 1664024363333,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8806256138231203,
            "unit": "iter/sec",
            "range": "stddev: 0.008633998257069975",
            "extra": "mean: 1.1355563412000151 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.925786911979031,
            "unit": "iter/sec",
            "range": "stddev: 0.00743731261781028",
            "extra": "mean: 91.52658825000515 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.21995164083661684,
            "unit": "iter/sec",
            "range": "stddev: 0.043022811604254904",
            "extra": "mean: 4.546453921399996 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "61194539+mergezalot@users.noreply.github.com",
            "name": "Michael Karlen",
            "username": "mergezalot"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "30a9e68beecb0d710339e85b991add63d9141c93",
          "message": "TST: read_string_from_stream performance (#1355)\n\nThere is a saftey margin of a factor of 10 in both directions,\r\nso the test should be fairly stable.\r\n\r\nTests #1350.\r\n\r\nCo-authored-by: Michael Karlen <michael.karlen@gmail.com>",
          "timestamp": "2022-09-25T08:31:40+02:00",
          "tree_id": "abeed7a9eed8aea364d7120ea37bdfbf90fb22f0",
          "url": "https://github.com/py-pdf/PyPDF2/commit/30a9e68beecb0d710339e85b991add63d9141c93"
        },
        "date": 1664087573292,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.9142626711048651,
            "unit": "iter/sec",
            "range": "stddev: 0.012020139850162639",
            "extra": "mean: 1.0937775669999994 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 11.3773641123255,
            "unit": "iter/sec",
            "range": "stddev: 0.006328296813346617",
            "extra": "mean: 87.89382058333395 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22219162599093986,
            "unit": "iter/sec",
            "range": "stddev: 0.05791000906966937",
            "extra": "mean: 4.500619659000003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "59577610+srogmann@users.noreply.github.com",
            "name": "Sascha Rogmann",
            "username": "srogmann"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ebb3b83c3aa6e2305b32710c609e0e7534186934",
          "message": "ENH: Addition of optional visitor-functions in extract_text() (#1252)\n\nOptional visitor-callback were added to extract_text().\r\n\r\n_extract_text() calls these visitor-methods while scanning the text-objects of a page. So one can analyze the operations in the page and the positions of the texts.\r\n\r\nIt can also be used to extract the rectangles of a table and the text in the cells.\r\n\r\ntests/test_page.py extracts the texts of labels in a Figure and serves as an example how to use this enhancement.",
          "timestamp": "2022-09-25T10:42:38+02:00",
          "tree_id": "7e61d824d7e7b07f782333f3b036178b3ab50b5e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/ebb3b83c3aa6e2305b32710c609e0e7534186934"
        },
        "date": 1664095432696,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0401711833016192,
            "unit": "iter/sec",
            "range": "stddev: 0.01561085702181688",
            "extra": "mean: 961.3802190000001 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.694411373890373,
            "unit": "iter/sec",
            "range": "stddev: 0.006510090549569157",
            "extra": "mean: 78.7748222857171 msec\nrounds: 14"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2573582380007235,
            "unit": "iter/sec",
            "range": "stddev: 0.02050986545427886",
            "extra": "mean: 3.8856343117999925 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "cf76824e3324d1bf7ad38710be7118f1689d272c",
          "message": "MAINT: Update sample-files",
          "timestamp": "2022-09-25T10:47:23+02:00",
          "tree_id": "fee2324b2b8c87ce3805958001e51c93b0c9fc3f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/cf76824e3324d1bf7ad38710be7118f1689d272c"
        },
        "date": 1664095710795,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.037682653821665,
            "unit": "iter/sec",
            "range": "stddev: 0.005608881027674314",
            "extra": "mean: 963.6857630000037 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.400775422013472,
            "unit": "iter/sec",
            "range": "stddev: 0.005054686199997665",
            "extra": "mean: 80.640118538461 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25803690464866097,
            "unit": "iter/sec",
            "range": "stddev: 0.011011951733543263",
            "extra": "mean: 3.8754146480000005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "26bdc6b36e4bcd8bae11f73dfdba0926abd62ae3",
          "message": "DOC: Add Sascha Rogmann as a contributor",
          "timestamp": "2022-09-25T17:15:25+02:00",
          "tree_id": "23b67b16d087852f4baac114c3b472c836419b64",
          "url": "https://github.com/py-pdf/PyPDF2/commit/26bdc6b36e4bcd8bae11f73dfdba0926abd62ae3"
        },
        "date": 1664119006415,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8902953665880672,
            "unit": "iter/sec",
            "range": "stddev: 0.02098050566385097",
            "extra": "mean: 1.1232227388000013 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.014535943139089,
            "unit": "iter/sec",
            "range": "stddev: 0.008792094308513103",
            "extra": "mean: 99.85485155556262 msec\nrounds: 9"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22167248436237474,
            "unit": "iter/sec",
            "range": "stddev: 0.074569126704801",
            "extra": "mean: 4.511159798999995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eca1a848633871548dd700a147060dfbfa0da7c2",
          "message": "BUG: Lookup index in _xobj_to_image can be ByteStringObject (#1366)\n\nDEV: Adjusted File classes __str__ and __repr__ to easy debugging",
          "timestamp": "2022-09-25T18:40:11+02:00",
          "tree_id": "ff6f6d212c2ac37f4392311a27ecb0557ff4e4f6",
          "url": "https://github.com/py-pdf/PyPDF2/commit/eca1a848633871548dd700a147060dfbfa0da7c2"
        },
        "date": 1664124074001,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0605481365199423,
            "unit": "iter/sec",
            "range": "stddev: 0.005463334734702151",
            "extra": "mean: 942.9086389999952 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.573549801682004,
            "unit": "iter/sec",
            "range": "stddev: 0.004714931055203965",
            "extra": "mean: 79.53203476922856 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.2598913643732448,
            "unit": "iter/sec",
            "range": "stddev: 0.010354597710917198",
            "extra": "mean: 3.8477615538000065 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "67a5ccfad2664c7854c3fac4fc6fac6500a52232",
          "message": "REL: 2.11.0\n\nNew Features (ENH):\n-  Addition of optional visitor-functions in extract_text() (#1252)\n-  Add metadata.creation_date and modification_date (#1364)\n-  Add PageObject.images attribute (#1330)\n\nBug Fixes (BUG):\n-  Lookup index in _xobj_to_image can be ByteStringObject (#1366)\n-  \\'IndexError: index out of range\\' when using extract_text (#1361)\n-  Errors in transfer_rotation_to_content() (#1356)\n\nRobustness (ROB):\n-  Ensure update_page_form_field_values does not fail if no fields (#1346)\n\nTesting (TST):\n-  read_string_from_stream performance (#1355)\n\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/2.10.9...2.11.0",
          "timestamp": "2022-09-25T18:49:39+02:00",
          "tree_id": "1e4856d3f6d19b13c436ddbccb2da714e4dcfa66",
          "url": "https://github.com/py-pdf/PyPDF2/commit/67a5ccfad2664c7854c3fac4fc6fac6500a52232"
        },
        "date": 1664124670574,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.028173160727135,
            "unit": "iter/sec",
            "range": "stddev: 0.00826957765584864",
            "extra": "mean: 972.5988172000029 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.598792327643986,
            "unit": "iter/sec",
            "range": "stddev: 0.0065738009991870554",
            "extra": "mean: 79.37268699999305 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.25296824508617344,
            "unit": "iter/sec",
            "range": "stddev: 0.020067402657176336",
            "extra": "mean: 3.9530653330000005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d508c69c3dba15bc834d3d43df14415d46643ffa",
          "message": "STY: Variable naming, black, and isort (#1367)\n\nType annotations as well",
          "timestamp": "2022-09-26T08:15:46+02:00",
          "tree_id": "ea43867258da4d34d754a57db44817d5d989191e",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d508c69c3dba15bc834d3d43df14415d46643ffa"
        },
        "date": 1664173021958,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.898226400234903,
            "unit": "iter/sec",
            "range": "stddev: 0.010076081175121635",
            "extra": "mean: 1.1133050639999909 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 10.854901926219426,
            "unit": "iter/sec",
            "range": "stddev: 0.009236011964900512",
            "extra": "mean: 92.12427774999554 msec\nrounds: 12"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.22050797257448113,
            "unit": "iter/sec",
            "range": "stddev: 0.050225582900601744",
            "extra": "mean: 4.534983421799995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "59577610+srogmann@users.noreply.github.com",
            "name": "Sascha Rogmann",
            "username": "srogmann"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a5f4f41e5675f78902f9881545e2afb9d8455112",
          "message": "DOC: How to use visitor functions (#1369)\n\nAdd two samples using visitor-functions when calling extract_text.\r\n\r\nThe first example may be of help in #1354.\r\n\r\nThe second one may be of help when debugging extract_text.",
          "timestamp": "2022-09-27T14:09:42+02:00",
          "tree_id": "8bdec9aab871e3fe20fb451aa989798760dbe49b",
          "url": "https://github.com/py-pdf/PyPDF2/commit/a5f4f41e5675f78902f9881545e2afb9d8455112"
        },
        "date": 1664280648220,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.017408702050783,
            "unit": "iter/sec",
            "range": "stddev: 0.01132853420118732",
            "extra": "mean: 982.8891752000033 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.420098591812467,
            "unit": "iter/sec",
            "range": "stddev: 0.007526816819196323",
            "extra": "mean: 80.51465876923203 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.24891065089973516,
            "unit": "iter/sec",
            "range": "stddev: 0.0278825837447945",
            "extra": "mean: 4.0175058656000004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "committer": {
            "email": "info@martin-thoma.de",
            "name": "Martin Thoma",
            "username": "MartinThoma"
          },
          "distinct": true,
          "id": "d9aa64c2a41c379c4b1210e3689e4edb4f694a77",
          "message": "DOC: Black formatting and variable naming",
          "timestamp": "2022-09-27T20:33:38+02:00",
          "tree_id": "426055749aff5553a5574ad4611065653e83988f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/d9aa64c2a41c379c4b1210e3689e4edb4f694a77"
        },
        "date": 1664303701549,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 0.8040618012970783,
            "unit": "iter/sec",
            "range": "stddev: 0.03430003557187833",
            "extra": "mean: 1.2436854958000025 sec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 9.64115825886579,
            "unit": "iter/sec",
            "range": "stddev: 0.008954356004033348",
            "extra": "mean: 103.72197749999827 msec\nrounds: 10"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.1987792372610368,
            "unit": "iter/sec",
            "range": "stddev: 0.11140434343406645",
            "extra": "mean: 5.030706495200002 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "4083478+pubpub-zz@users.noreply.github.com",
            "name": "pubpub-zz",
            "username": "pubpub-zz"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f3b6d0e7d723aebc72c8de638ad852f5c98e9168",
          "message": "FIX : cope with cmap from #1322 (#1372)\n\nCope with cmap where the range contains first and last code are on variable length.\r\n\r\nAlso fixes cases where the code is on 3 characters only (not standard).\r\nNo test data is available.\r\n\r\nFixes #1322",
          "timestamp": "2022-09-28T07:29:49+02:00",
          "tree_id": "8d0df2e13b3c7a416bec4c556aefa675e809aa3f",
          "url": "https://github.com/py-pdf/PyPDF2/commit/f3b6d0e7d723aebc72c8de638ad852f5c98e9168"
        },
        "date": 1664343057058,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_page_operations",
            "value": 1.0248822921406338,
            "unit": "iter/sec",
            "range": "stddev: 0.008354862234113507",
            "extra": "mean: 975.7218050000034 msec\nrounds: 5"
          },
          {
            "name": "tests/bench.py::test_merge",
            "value": 12.558628289737285,
            "unit": "iter/sec",
            "range": "stddev: 0.007137786524885908",
            "extra": "mean: 79.62653061538451 msec\nrounds: 13"
          },
          {
            "name": "tests/bench.py::test_text_extraction",
            "value": 0.24402519734025632,
            "unit": "iter/sec",
            "range": "stddev: 0.0742969443718664",
            "extra": "mean: 4.097937470799996 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}