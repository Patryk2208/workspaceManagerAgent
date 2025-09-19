package main

import (
	"context"
	"encoding/json"
	"log"
	"sync"
	"time"
)

type WorkspaceState struct {
	Windows         map[int64]WindowState
	updateTimestamp time.Time
	windowsMutex    sync.Mutex
	RequestChannel  chan bool
	StateChannel    chan json.RawMessage
}

func RunStateServer(wmConnection *I3ipcConnection, requestChannel chan bool,
	stateChannel chan json.RawMessage, ctx context.Context, wg sync.WaitGroup) {
	workspaceState := &WorkspaceState{
		Windows:        make(map[int64]WindowState),
		RequestChannel: requestChannel,
		StateChannel:   stateChannel,
	}
	const interval = 2 * time.Second
	go workspaceState.RunInterface()
	for {
		select {
		case <-time.After(interval):
			workspaceState.windowsMutex.Lock()
			err := ScanState(wmConnection, workspaceState)
			if err != nil {
				log.Println(err)
			} else {
				workspaceState.updateTimestamp = time.Now()
				log.Println("Scanned state")
			}
			workspaceState.windowsMutex.Unlock()
		case <-ctx.Done():
			log.Println("Exiting RunStateServer")
			break
		}
	}
	wg.Done()
}

func (ws *WorkspaceState) RunInterface() {
	for {
		select {
		case <-ws.RequestChannel:
			ws.windowsMutex.Lock()
			msg := ws.ParseState()
			if msg != nil {
				ws.StateChannel <- msg
				log.Println("Parsed and prepared state message")
			}
			ws.windowsMutex.Unlock()
		}
	}
}

func (ws *WorkspaceState) ParseState() json.RawMessage {
	var windows []WindowState
	for _, state := range ws.Windows {
		windows = append(windows, state)
	}
	payload := StatePayload{
		Timestamp: ws.updateTimestamp,
		Windows:   windows,
	}
	msg, err := json.Marshal(payload)
	if err != nil {
		log.Println(err)
		return nil
	}
	return msg
}
