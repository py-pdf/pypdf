#!/bin/sh

# An example shell script that demonstrates using `ps2pdf` on the command line
sample=1
for pagecount in 5 11 17; do
   page=1
   f=simple$sample.pdf
   while expr $page \<= $pagecount > /dev/null; do
     if [ $page != 1 ]; then
       echo "\c"
      fi
     echo "$f           page $page of $pagecount"
     echo ""
     echo "an incredible, yet simple example"
     echo "Created with Sample_Code/makesimple.sh"
     page=$(expr $page + 1)
    done | enscript --no-header -o - |ps2pdf - $f
   echo $f
   sample=$(expr $sample + 1)
 done