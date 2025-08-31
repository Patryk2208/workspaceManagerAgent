package Sway

import (
	"github.com/mdirkse/i3ipc-go"
	"time"
)

type I3ipcConnection struct {
	conn           *i3ipc.IPCSocket
	responseBuffer chan WorkspaceState
}

type WorkspaceState struct {
	windows map[int64]WindowState
} //todo check deleted windows

type WindowState struct {
	AppName         string //todo
	Rect            i3ipc.Rect
	WorkspaceNumber int
	Activity        WindowActivity
}

type WindowActivity struct {
	LastFocusTime *time.Time
	FocusDuration *time.Duration
}

func NewI3ipcConnection(conn *i3ipc.IPCSocket) *I3ipcConnection {
	const bufferSize = 64
	return &I3ipcConnection{conn: conn, responseBuffer: make(chan WorkspaceState, bufferSize)}
}

func RunStateScan() error {
	i3ipc, err := CreateSwayConnection()
	if err != nil {
		return err
	}

}

func CreateSwayConnection() (*I3ipcConnection, error) {
	sock, err := i3ipc.GetIPCSocket()
	if err != nil {
		return nil, err
	}
	return NewI3ipcConnection(sock), nil
}

func ScanState(swayConn *I3ipcConnection) {}
