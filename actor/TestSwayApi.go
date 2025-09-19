package main

import (
	"sync"
	"testing"
	"time"
)

func TestSwayConnection_SwayConnection(t *testing.T) {
	swayConnection, err := CreateSwayConnection()
	if err != nil {
		t.Error(err)
	}
	workspaceState := &WorkspaceState{
		Windows:         make(map[int64]WindowState),
		updateTimestamp: time.Now(),
		windowsMutex:    sync.Mutex{},
		RequestChannel:  nil,
		StateChannel:    nil,
	}

	err = swayConnection.GetSwayTree(workspaceState)
	if err != nil {
		t.Error(err)
	}

	ok, err := swayConnection.Conn.Command("")
	if err != nil {
		t.Error(err)
	}
	if !ok {
		t.Error("Bad command but success")
	}
}

func TestSwayConnection_ScanState(t *testing.T) {}

func TestSwayConnection_Command(t *testing.T) {}
