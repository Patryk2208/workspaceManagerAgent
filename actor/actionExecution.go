package main

import (
	"context"
	"encoding/json"
	"github.com/go-playground/validator/v10"
	"log"
	"sync"
)

func RunActionExecution(wmConnection *I3ipcConnection, ctx context.Context, wg sync.WaitGroup) {
	for {
		select {
		case rawAction := <-wmConnection.ActionChannel:
			action, err := ParseAndValidateAction(rawAction)
			if err != nil {
				log.Println("Error parsing action ", err)
				continue
			}
			log.Println("Action parsed ", action)
			actionString := ConvertActionToMessage(action)
			log.Println("Action converted to sway command")
			ok, err := wmConnection.Conn.Command(actionString)
			if err != nil || !ok {
				log.Println(err)
				continue
			}
			log.Println("Action executed successfully")
		case <-ctx.Done():
			log.Println("Exiting RunActionExecution")
			break
		}
	}
	wg.Done()
}

func ParseAndValidateAction(message json.RawMessage) (ActionPayload, error) {
	var payload ActionPayload
	err := json.Unmarshal(message, payload)
	if err != nil {
		log.Fatal(err)
		return ActionPayload{}, err
	}
	validator := validator.New()
	err = validator.Struct(payload)
	if err != nil {
		log.Fatal(err)
		return ActionPayload{}, err
	}
	return payload, nil
}

func ConvertActionToMessage(action ActionPayload) string {
	//todo
	return ""
}
