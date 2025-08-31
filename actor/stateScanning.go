package main

import (
	"github.com/mdirkse/i3ipc-go"
)

func NewI3ipcConnection(conn *i3ipc.IPCSocket) *I3ipcConnection {
	const bufferSize = 64
	return &I3ipcConnection{
		Conn:           conn,
		ResponseBuffer: make(chan WorkspaceState, bufferSize),
		ActionBuffer:   make(chan WorkspaceAction, bufferSize),
	}
}

func RunStateScan() error {
	i3ipc, err := CreateSwayConnection()
	if err != nil {
		return err
	}
	return nil
}

func CreateSwayConnection() (*I3ipcConnection, error) {
	sock, err := i3ipc.GetIPCSocket()
	if err != nil {
		return nil, err
	}
	return NewI3ipcConnection(sock), nil
}

func ScanState(swayConn *I3ipcConnection) {}
