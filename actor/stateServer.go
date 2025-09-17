package main

import (
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

func RunStateServer(wmConnection *I3ipcConnection, requestChannel chan bool, stateChannel chan json.RawMessage) {
	workspaceState := &WorkspaceState{
		Windows:        make(map[int64]WindowState),
		RequestChannel: requestChannel,
		StateChannel:   stateChannel,
	}
	const interval = 2 * time.Second
	go workspaceState.RunInterface()
	for {
		workspaceState.windowsMutex.Lock()
		ScanState(wmConnection, workspaceState)
		workspaceState.updateTimestamp = time.Now()
		workspaceState.windowsMutex.Unlock()
		time.Sleep(interval)
	}
}

func (ws *WorkspaceState) RunInterface() {
	for {
		select {
		case <-ws.RequestChannel:
			ws.windowsMutex.Lock()
			msg := ws.ParseState()
			if msg != nil {
				ws.StateChannel <- msg
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
