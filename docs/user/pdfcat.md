# pdfcat

**PyPDF2** contains a growing variety of sample programs meant to demonstrate its
features. It also contains useful scripts such as `pdfcat`, located within the
`Scripts` folder. This script makes it easy to concatenate PDF files by using
Python slicing syntax. Because we are slicing PDF pages, we refer to the slices
as *page ranges*.

```{admonition} Deprecation Discussion
We are thinking about moving pdfcat to a separate package.
Please [participate in the discussion](https://github.com/py-pdf/PyPDF2/discussions/718).
```

**Page range** expression examples:

|  :  | all pages                  | -1    | last page               |
| --- | -------------------------- | ----- | ----------------------- |
| 22  | just the 23rd page         | :-1   | all but the last page   |
| 0:3 | the first three pages      | -2    | second-to-last page     |
| :3  | the first three pages      | -2:   | last two pages          |
| 5:  | from the sixth page onward | -3:-1 | third & second to last  |

The third stride or step number is also recognized:

|  ::2   | 0 2 4 ... to the end       |
| ------ | -------------------------- |
| 1:10:2 | 1 3 5 7 9                  |
| ::-1   | all pages in reverse order |
| 3:0:-1 | 3 2 1 but not 0            |
| 2::-1  | 2 1 0                      |


Usage for pdfcat is as follows:

```console
$ pdfcat [-h] [-o output.pdf] [-v] input.pdf [page_range...] ...
```

You can add as many input files as you like. You may also specify as many page
ranges as needed for each file.

**Optional arguments:**


| -h | --help	 | Show the help message and exit
| -- |---------- | ------------------------------
| -o | --output	 | Follow this argument with the output PDF file. Will be created if it doesn’t exist.
| -v | --verbose | Show page ranges as they are being read

## Examples

```console
$ pdfcat -o output.pdf head.pdf content.pdf :6 7: tail.pdf -1
```

Concatenates all of head.pdf, all but page seven of content.pdf, and the last page of tail.pdf, producing output.pdf.

```console
$ pdfcat chapter*.pdf >book.pdf
```

You can specify the output file by redirection.

```console
$ pdfcat chapter?.pdf chapter10.pdf >book.pdf
```

In case you don’t want chapter 10 before chapter 2.

Thanks to **Steve Witham** for this script!
