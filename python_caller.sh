#!/bin/bash
line=" hihiand hihi2 and hihi3" 
#IFS="
#"
IFS=/

#set -f  #Disables glob? (what's glob?)
echo $line
python3 parser.py $line


#https://unix.stackexchange.com/questions/250963/passing-paths-with-spaces-as-arguments
