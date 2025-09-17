package main

import (
	"github.com/mdirkse/i3ipc-go"
	"strconv"
	"time"
)

func ScanState(swayConn *I3ipcConnection, workspaceState *WorkspaceState) {
	for id := range workspaceState.Windows {
		temp := workspaceState.Windows[id]
		temp.stillExists = false
		workspaceState.Windows[id] = temp
	}

	swayConn.getSwayTree(workspaceState)

	for id := range workspaceState.Windows {
		temp := workspaceState.Windows[id]
		if !temp.stillExists {
			delete(workspaceState.Windows, id)
		}
	}

}

const ContainerSway = "con"
const WorkspaceSway = "workspace"

func (swayConn *I3ipcConnection) getSwayTree(state *WorkspaceState) {
	root, err := swayConn.Conn.GetTree()
	if err != nil {
		return
	}
	ParseSwayTree(&root, 0, state)
}
func ParseSwayTree(root *i3ipc.I3Node, currentWorkspace int, workspaceState *WorkspaceState) {
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
			UpdateWindowState(root, currentWorkspace, workspaceState.updateTimestamp, &v)
		} else {
			workspaceState.Windows[root.ID] = CreateWindowState(root, currentWorkspace)
		}
	}
	for _, node := range root.Nodes {
		ParseSwayTree(&node, currentWorkspace, workspaceState)
	}
}

func CreateWindowState(node *i3ipc.I3Node, workspaceNumber int) WindowState {
	activity := WindowActivity{
		IsFocused:            node.Focused,
		CurrentFocusDuration: 0,
		TotalFocusDuration:   0,
	}
	position := WindowPosition{}
	return WindowState{
		WindowId:        node.ID,
		Title:           node.Name,
		Position:        position, //todo
		WindowActivity:  activity,
		WorkspaceNumber: workspaceNumber,
		stillExists:     true,
	}
}

func UpdateWindowState(node *i3ipc.I3Node, workspaceNumber int, lastTimestamp time.Time, windowState *WindowState) {
	//todo id
	windowState.Title = node.Name
	windowState.Position = WindowPosition{} //todo
	wasFocused := windowState.WindowActivity.IsFocused
	windowState.WindowActivity.IsFocused = node.Focused
	if wasFocused {
		windowState.WindowActivity.CurrentFocusDuration += time.Now().Sub(lastTimestamp)
		windowState.WindowActivity.TotalFocusDuration += time.Now().Sub(lastTimestamp)
	}
	if !node.Focused {
		windowState.WindowActivity.CurrentFocusDuration = 0
	}
	windowState.WorkspaceNumber = workspaceNumber
	windowState.stillExists = true
}
