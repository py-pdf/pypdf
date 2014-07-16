#!/bin/sh

n=1
for np in 5 11 17; do
   p=1
   f=simple$n.pdf
   while expr $p \<= $np > /dev/null; do
     if [ $p != 1 ]; then
       echo "\c"
      fi
     echo "$f           page $p of $np"
     echo ""
     echo "an incredible, yet simple example"
     echo "Created with Sample_Code/makesimple.sh"
     p=$(expr $p + 1)
    done | enscript --no-header -o - |ps2pdf - $f
   echo $f
   n=$(expr $n + 1)
 done