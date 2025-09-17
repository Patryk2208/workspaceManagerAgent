package main

import (
	"encoding/json"
	"github.com/gin-gonic/gin"
	"net/http"
	"time"
)

func RunServer(requestChannel chan bool, stateChannel chan json.RawMessage, actionChannel chan json.RawMessage) {
	router := gin.Default()

	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	const getDefaultTimeout = time.Second * 3

	router.GET("/state", func(c *gin.Context) {
		requestChannel <- true
		select {
		case state := <-stateChannel:
			c.JSON(http.StatusOK, state)
		case <-time.After(getDefaultTimeout):
			c.JSON(http.StatusInternalServerError, "timeout")
		}
	})

	router.POST("/command", func(c *gin.Context) {
		var command json.RawMessage
		if err := c.ShouldBindJSON(&command); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
			return
		}
		actionChannel <- command
	})

	router.Run(":8080")
}
