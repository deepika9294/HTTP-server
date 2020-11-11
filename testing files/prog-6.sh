#! /bin/bash

show_choices(){
	echo ""
	echo "Possible Choice :"
	echo "1. Addition"
	echo "2. Subtraction"
	echo "3. Division"
	echo "4. Multiplication"
	echo "5. Exit"
}


read_choices(){
	echo -n "Enter Choice: "
	read op 
	echo -n "Enter First number : "
	read a
	echo -n "Enter Second number: "
	read b
	
	case $op in
		1) echo "Sum is :" $(($a+$b));;
		2) echo "Subtraction is: " $(($a-$b));;
		3) echo "Division is: " $(($a/$b));;
		4) echo "Multiplication is: " $(($a*$b));;
		5) exit 0;;
		*) echo "Only Basic Airthmetic Operators  ";;
	esac
}


while true
do
	show_choices
	read_choices
done