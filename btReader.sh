#!/bin/bash

echo "starting reader"

while IFS= read -r -u "${btPipe[0]}" line; do
  echo "Read line from btctl: $line" >&2 
done

echo "Reader exiting" 


#https://stackoverflow.com/questions/64808659/sending-commands-to-an-application-and-reading-its-output-via-file-descriptor-in

#https://stackoverflow.com/questions/20017805/bash-capture-output-of-command-run-in-background

#https://www.linuxquestions.org/questions/programming-9/control-bluetoothctl-with-scripting-4175615328/

#https://stackoverflow.com/questions/54443399/bash-inline-version-of-piping-file-to-bluetoothctl


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