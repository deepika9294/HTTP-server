Content-Type: application/x-shellscript#! /bin/bash

echo -n "Enter number : "
read n
 
rem=$(( $n % 2 ))
 
if [ $rem -eq 0 ]
then
  echo "even number"
else
  echo "odd number"
fi