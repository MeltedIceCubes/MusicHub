#!/bin/bash
pipe_name="parsePipe"
function createPipe(){
	mkfifo $pipe_name #makes pipe to talk with python parser.
}
function agentOn() { 
	echo "agent on" >&"${btPipe[1]}" 
}
function agentOff() { 
	echo "agent off" >&"${btPipe[1]}" 
}
function powerOn() { 
	echo "power on" >&"${btPipe[1]}" 
}
function powerOff() { 
	echo "power off" >&"${btPipe[1]}" 
}
function discoverableOn() { 
	echo "discoverable on" >&"${btPipe[1]}" 
}
function discoverableOff() { 
	echo "discoverable off" >&"${btPipe[1]}" 
}
function pairableOn() { 
	echo "pairable on" >&"${btPipe[1]}" 
}
function pairableOff() { 
	echo "pairable off" >&"${btPipe[1]}" 
}
function scanOn(){
	echo "scan on" >&"${btPipe[1]}"
}
function scanOff(){
	echo "scan off" >&"${btPipe[1]}"
}
function NoInputNoOutput(){
	echo "agent NoInputNoOutput" >&"${btPipe[1]}"
}
function readPipe() { 
	#IFS= read -r -u "${btPipe[0]}" line  #Get buffer 
	#echo $line | sed 's/\x1B\[[0-9;]*[JKmsu]//g; s/\r/\n/g'  >&2  #Removes control characters. 
	IFS= read -r -u "${btPipe[0]}" line  #Get buffer 
	line=$(echo "$line" | sed 's/\x1B\[[0-9;]*[JKmsu]//g; s/\r/\n/g')
	#echo $line >> content.txt
	echo $line >> pipe0
	
}


coproc btPipe { bluetoothctl; }  #Start coproc pipe
#readPipe
sleep 2

while : ; do  #Loop infinitly "break" to end loop
	readPipe
	scanOn
	sleep 1
	readPipe
	discoverableOn
	sleep 1
	readPipe
	pairableOn
	sleep 1
	readPipe
	sleep 5
	readPipe
	sleep 5 
	readPipe
	sleep 5
	readPipe
	sleep 5
	readPipe
	sleep 5
	
	
done
echo "Script exit."
