#!/bin/bash

#1. Make pipe if it does not exist.
#2. 

banana() {
    for i in {1..10}; do
        echo "gorilla eats banana $i"
	sleep 1
    done
    echo "gorilla says thank you for the delicious bananas"
}

stuff() {
    echo "I'm doing this stuff"
    sleep 1
    echo "I'm doing that stuff"
    sleep 1
    echo "I'm done doing my stuff."
}

function agentOn() {
    echo "scan on" >&"${btPipe[1]}"
}
function agentOff() {
	echo "scan off" >&"${btPipe[1]}"
}
function printcheck() {
	echo "hihi"
}
#coproc btPipe { banana; }
coproc btPipe { bluetoothctl; }
IFS= read -r -u "${btPipe[0]}" line
sleep 1
#echo "scan on" >&"${btPipe[1]}" 
agentOn
IFS= read -r -u "${btPipe[0]}" line

while IFS= read -r -u "${btPipe[0]}" line; do
	echo "Read line from btctl: $line" >&2
done
echo "it left me :("



#https://www.linuxquestions.org/questions/programming-9/control-bluetoothctl-with-scripting-4175615328/