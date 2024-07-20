# CMaps

Looking at the cmap of "crazyones":

```bash
pdftk crazyones.pdf output crazyones-uncomp.pdf uncompress
```

You can see this:

```text
begincmap
/CMapName /T1Encoding-UTF16 def
/CMapType 2 def
/CIDSystemInfo <<
  /Registry (Adobe)
  /Ordering (UCS)
  /Supplement 0
>> def
1 begincodespacerange
<00> <FF>
endcodespacerange
1 beginbfchar
<1B> <FB00>
endbfchar
endcmap
CMapName currentdict /CMap defineresource pop
```

## codespacerange

A codespacerange maps a complete sequence of bytes to a range of unicode glyphs.
It defines a starting point:

```text
1 beginbfchar
<1B> <FB00>
```

That means that `1B` (Hex for 27) maps to the unicode character [`FB00`](https://unicode-table.com/en/FB00/) - the ligature ﬀ (two lowercase f's).

The two numbers in `begincodespacerange` mean that it starts with an offset of
0 (hence from `1B ➜ FB00`) up to an offset of FF (dec: 255), hence 1B+FF = 282
➜ [FBFF](https://www.compart.com/de/unicode/U+FBFF).

Within the text stream, there is

```text
(The)-342(mis\034ts.)
```

`\034 ` is octal for 28 decimal.
