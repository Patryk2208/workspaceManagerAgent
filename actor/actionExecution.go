package main

import (
	"encoding/json"
	"github.com/go-playground/validator/v10"
	"log"
)

func RunActionExecution(wmConnection *I3ipcConnection) {
	for {
		select {
		case rawAction := <-wmConnection.ActionChannel:
			action, err := ParseAndValidateAction(rawAction)
			if err != nil {
				continue
			}
			actionString := ConvertActionToMessage(action)
			ok, err := wmConnection.Conn.Command(actionString)
			if err != nil || !ok {
				log.Fatal(err)
				continue
			}
		}
	}
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
