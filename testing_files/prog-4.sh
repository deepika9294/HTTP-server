
#! /bin/bash

echo "Enter radius"
#accepting number from user
read r

circum=$(echo "3.14*2*$r" | bc)
area=$(echo "3.14*$r*$r" | bc)

echo "Circumference is $circum"
echo "Area is $area"

