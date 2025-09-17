package main

import (
	"encoding/json"
	"log"
)

//todo add testing, logging and command translation

func main() {
	wmConnection, err := CreateSwayConnection()
	if err != nil {
		log.Fatal(err)
	}
	const defaultCapacity = 16
	requestChannel := make(chan bool, defaultCapacity)
	stateChannel := make(chan json.RawMessage, defaultCapacity)
	commandChannel := make(chan json.RawMessage, defaultCapacity)
	go RunStateServer(wmConnection, requestChannel, stateChannel)
	go RunActionExecution(wmConnection)
	RunServer(requestChannel, stateChannel, commandChannel)
}
