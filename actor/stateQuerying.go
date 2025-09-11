package main

import (
	"github.com/mdirkse/i3ipc-go"
	"strconv"
	"time"
)

const ContainerSway = "con"
const WorkspaceSway = "workspace"

func (swayConn *I3ipcConnection) getSwayTree(state WorkspaceState) {
	root, err := swayConn.Conn.GetTree()
	if err != nil {
		return
	}
	ParseSwayTree(&root, 0, state)
}
func ParseSwayTree(root *i3ipc.I3Node, currentWorkspace int, workspaceState WorkspaceState) {
	if len(root.Nodes) == 0 {
		return
	}
	if root.Type == WorkspaceSway {
		workspaceNumber, err := strconv.Atoi(root.Name)
		if err != nil {
			return
		}
		currentWorkspace = workspaceNumber
	} else if root.Type == ContainerSway {
		v, exists := workspaceState.Windows[root.ID]
		if exists {
			UpdateWindowState(root, currentWorkspace, &v)
		} else {
			workspaceState.Windows[root.ID] = CreateWindowState(root, currentWorkspace)
		}
	}
	for _, node := range root.Nodes {
		ParseSwayTree(&node, currentWorkspace, workspaceState)
	}
}

func CreateWindowState(node *i3ipc.I3Node, workspaceNumber int) WindowState {
	now := time.Now()
	noDuration := time.Duration(0)
	lastFocusTime := &now
	focusDuration := &noDuration
	if !node.Focused {
		lastFocusTime = nil
		focusDuration = nil
	}
	activity := WindowActivity{
		LastFocusTime: lastFocusTime,
		FocusDuration: focusDuration,
	}
	return WindowState{
		AppName:         node.Name,
		Rect:            node.Rect,
		WorkspaceNumber: workspaceNumber,
		Activity:        activity,
		StillExists:     true,
	}
}

func UpdateWindowState(node *i3ipc.I3Node, workspaceNumber int, windowState *WindowState) {
	windowState.AppName = node.Name
	windowState.Rect = node.Rect
	windowState.WorkspaceNumber = workspaceNumber
	windowState.StillExists = true

	//todo update activity
}
