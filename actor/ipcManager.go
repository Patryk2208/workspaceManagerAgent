package main

import (
	"github.com/mdirkse/i3ipc-go"
	"time"
)

type I3ipcConnection struct {
	Conn           *i3ipc.IPCSocket
	ResponseBuffer chan WorkspaceState
	ActionBuffer   chan string
}

//state

type WorkspaceState struct {
	Windows map[int64]WindowState
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

//action

type WorkspaceAction struct {
	WindowPositions map[int64]WindowPosition
}

type WindowPosition struct {
	TopLeft     int
	BottomRight int
}

func ConvertToScreenSize(windowPosition WindowPosition, screenWidth int, screenHeight int) (i3ipc.Rect, error) {
	//todo check correctness
	//todo convert
}
