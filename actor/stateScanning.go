package main

import (
	"github.com/mdirkse/i3ipc-go"
)

func NewI3ipcConnection(conn *i3ipc.IPCSocket) *I3ipcConnection {
	const bufferSize = 64
	return &I3ipcConnection{
		Conn:         conn,
		ActionBuffer: make(chan string, bufferSize),
	}
}

func CreateSwayConnection() (*I3ipcConnection, error) {
	sock, err := i3ipc.GetIPCSocket()
	if err != nil {
		return nil, err
	}
	return NewI3ipcConnection(sock), nil
}

func ScanState(swayConn *I3ipcConnection, workspaceState *WorkspaceState) {
	for id := range workspaceState.Windows {
		temp := workspaceState.Windows[id]
		temp.StillExists = false
		workspaceState.Windows[id] = temp
	}

	swayConn.getSwayTree(*workspaceState)

	for id := range workspaceState.Windows {
		temp := workspaceState.Windows[id]
		if !temp.StillExists {
			delete(workspaceState.Windows, id)
		}
	}

}
