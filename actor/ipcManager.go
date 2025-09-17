package main

import (
	"encoding/json"
	"github.com/mdirkse/i3ipc-go"
)

type I3ipcConnection struct {
	Conn          *i3ipc.IPCSocket
	ActionChannel chan json.RawMessage
}

func NewI3ipcConnection(conn *i3ipc.IPCSocket) *I3ipcConnection {
	const bufferSize = 64
	return &I3ipcConnection{
		Conn:          conn,
		ActionChannel: make(chan json.RawMessage, bufferSize),
	}
}

func CreateSwayConnection() (*I3ipcConnection, error) {
	sock, err := i3ipc.GetIPCSocket()
	if err != nil {
		return nil, err
	}
	return NewI3ipcConnection(sock), nil
}

func ConvertToScreenSize(windowPosition WindowPosition, screenWidth int, screenHeight int) (i3ipc.Rect, error) {
	//todo check correctness
	//todo convert
}
