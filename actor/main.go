package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"
)

//todo add testing and command translation

func main() {
	log.Println("Starting...")

	wmConnection, err := CreateSwayConnection()
	if err != nil {
		log.Fatal(err)
	}
	const defaultCapacity = 16
	requestChannel := make(chan bool, defaultCapacity)
	stateChannel := make(chan json.RawMessage, defaultCapacity)
	commandChannel := make(chan json.RawMessage, defaultCapacity)

	ctx, cancel := context.WithCancel(context.Background())
	wg := sync.WaitGroup{}
	wg.Add(3)

	go RunServer(requestChannel, stateChannel, commandChannel, ctx, wg)
	go RunStateServer(wmConnection, requestChannel, stateChannel, ctx, wg)
	go RunActionExecution(wmConnection, ctx, wg)

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	cancel()

	wg.Wait()

	log.Println("Shutting down")
}
