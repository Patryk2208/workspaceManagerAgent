package main

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
