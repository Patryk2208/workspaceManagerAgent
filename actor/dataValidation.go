package main

import (
	"time"
)

type WindowActivity struct {
	IsFocused            bool          `json:"is_focused"`
	CurrentFocusDuration time.Duration `json:"current_focus_duration"`
	TotalFocusDuration   time.Duration `json:"total_focus_duration"`
}

type WindowPosition struct {
	TopLeftX     int `json:"top_left_x" validate:"required,min=0,max=6"`
	TopLeftY     int `json:"top_left_y" validate:"required,min=0,max=4"`
	BottomRightX int `json:"bottom_right_x" validate:"required,min=0,max=6"`
	BottomRightY int `json:"bottom_right_y" validate:"required,min=0,max=4"`
}

type WindowState struct {
	WindowId        int64          `json:"window_id"`
	Title           string         `json:"title"`
	Position        WindowPosition `json:"position"`
	WindowActivity  WindowActivity `json:"window_activity"`
	WorkspaceNumber int            `json:"workspace_number"`
	stillExists     bool
}

type StatePayload struct {
	Timestamp time.Time     `json:"timestamp"`
	Windows   []WindowState `json:"windows"`
}

type Action struct {
	WindowId int64          `json:"window_id" validate:"required"`
	Position WindowPosition `json:"position" validate:"required"`
}

type ActionPayload struct {
	Timestamp time.Time `json:"timestamp" validate:"required"`
	Windows   []Action  `json:"windows" validate:"required"`
}
