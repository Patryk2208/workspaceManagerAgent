package main

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/gin-gonic/gin"
	"log"
	"net/http"
	"sync"
	"time"
)

func RunServer(requestChannel chan bool, stateChannel chan json.RawMessage,
	actionChannel chan json.RawMessage, ctx context.Context, wg sync.WaitGroup) {
	router := gin.Default()

	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	const getDefaultTimeout = time.Second * 3

	router.GET("/state", func(c *gin.Context) {
		requestChannel <- true
		select {
		case state := <-stateChannel:
			c.JSON(http.StatusOK, state)
			log.Println("Sent state, timestamp: ", time.Now())
		case <-time.After(getDefaultTimeout):
			c.JSON(http.StatusInternalServerError, "timeout")
			log.Println("Timeout on GET")
		}
	})

	router.POST("/command", func(c *gin.Context) {
		var command json.RawMessage
		if err := c.ShouldBindJSON(&command); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
			log.Println(err)
			return
		}
		actionChannel <- command
		log.Println("Received command, timestamp: ", time.Now())
	})

	server := &http.Server{
		Addr:    "127.0.0.1:8080",
		Handler: router,
	}

	go func() {
		err := server.ListenAndServe()
		if errors.Is(err, http.ErrServerClosed) {
			log.Println("Server properly closed")
		}
		if err != nil {
			log.Fatal(err)
			return
		}
	}()

	<-ctx.Done()

	if err := server.Shutdown(nil); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	wg.Done()
}
