package main

func (swayConn *I3ipcConnection) ExecuteAction() bool {
	action := <-swayConn.ActionBuffer
	ok, err := swayConn.Conn.Command(action)
	return ok && err == nil
}
