package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

type Service struct {
	Name           string            `json:"name"`
	Path           string            `json:"path"`
	Status         string            `json:"status"`
	Port           string            `json:"port"`
	Containers     []Container       `json:"containers"`
	LastChecked    time.Time         `json:"last_checked"`
	HealthEndpoint string            `json:"health_endpoint,omitempty"`
	Networks       []string          `json:"networks"`
	Volumes        []string          `json:"volumes"`
	Environment    map[string]string `json:"environment"`
}

type Container struct {
	Name   string `json:"name"`
	Status string `json:"status"`
	Health string `json:"health"`
	Image  string `json:"image"`
	Port   string `json:"port"`
}

type ServiceManager struct {
	services map[string]*Service
	rootPath string
	upgrader websocket.Upgrader
}

func NewServiceManager(rootPath string) *ServiceManager {
	return &ServiceManager{
		services: make(map[string]*Service),
		rootPath: rootPath,
		upgrader: websocket.Upgrader{
			CheckOrigin: func(r *http.Request) bool {
				return true // Allow all origins for development
			},
		},
	}
}

func (sm *ServiceManager) discoverServices() error {
	servicesPath := filepath.Join(sm.rootPath, "services")

	// Discover services in the db directory
	dbPath := filepath.Join(servicesPath, "db")
	if _, err := os.Stat(dbPath); err == nil {
		err := filepath.Walk(dbPath, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}

			if info.IsDir() && strings.Contains(path, "docker-compose.yml") {
				return nil
			}

			if info.Name() == "docker-compose.yml" {
				serviceName := filepath.Base(filepath.Dir(path))
				if serviceName != "db" {
					sm.services[serviceName] = &Service{
						Name:        serviceName,
						Path:        filepath.Dir(path),
						Status:      "unknown",
						LastChecked: time.Now(),
					}
				}
			}
			return nil
		})
		if err != nil {
			log.Printf("Error walking db directory: %v", err)
		}
	}

	// Discover services in the root services directory
	entries, err := os.ReadDir(servicesPath)
	if err != nil {
		return err
	}

	for _, entry := range entries {
		if entry.IsDir() && entry.Name() != "db" {
			servicePath := filepath.Join(servicesPath, entry.Name())
			composePath := filepath.Join(servicePath, "docker-compose.yml")

			if _, err := os.Stat(composePath); err == nil {
				sm.services[entry.Name()] = &Service{
					Name:        entry.Name(),
					Path:        servicePath,
					Status:      "unknown",
					LastChecked: time.Now(),
				}
			}
		}
	}

	// Discover shared infrastructure services
	sharedServicesPath := filepath.Join(sm.rootPath, "infrastructure", "shared-services")
	if _, err := os.Stat(sharedServicesPath); err == nil {
		composePath := filepath.Join(sharedServicesPath, "docker-compose.yml")
		if _, err := os.Stat(composePath); err == nil {
			sm.services["shared-services"] = &Service{
				Name:        "shared-services",
				Path:        sharedServicesPath,
				Status:      "unknown",
				LastChecked: time.Now(),
			}
		}
	}

	return nil
}

func (sm *ServiceManager) updateServiceStatus(serviceName string) error {
	service, exists := sm.services[serviceName]
	if !exists {
		return fmt.Errorf("service %s not found", serviceName)
	}

	// Check docker-compose status
	cmd := exec.Command("docker", "compose", "ps", "--format", "json")
	cmd.Dir = service.Path

	output, err := cmd.Output()
	if err != nil {
		service.Status = "error"
		service.Containers = []Container{}
		return err
	}

	var containers []Container
	lines := strings.Split(strings.TrimSpace(string(output)), "\n")

	for _, line := range lines {
		if strings.TrimSpace(line) == "" {
			continue
		}

		var containerInfo map[string]interface{}
		if err := json.Unmarshal([]byte(line), &containerInfo); err != nil {
			continue
		}

		container := Container{
			Name:   fmt.Sprintf("%v", containerInfo["Name"]),
			Status: fmt.Sprintf("%v", containerInfo["State"]),
			Health: fmt.Sprintf("%v", containerInfo["Health"]),
			Image:  fmt.Sprintf("%v", containerInfo["Image"]),
		}

		if ports, ok := containerInfo["Publishers"]; ok {
			if portsArray, ok := ports.([]interface{}); ok && len(portsArray) > 0 {
				if portMap, ok := portsArray[0].(map[string]interface{}); ok {
					if publishedPort, ok := portMap["PublishedPort"]; ok {
						container.Port = fmt.Sprintf("%v", publishedPort)
					}
				}
			}
		}

		containers = append(containers, container)
	}

	service.Containers = containers
	service.LastChecked = time.Now()

	// Determine overall service status
	if len(containers) == 0 {
		service.Status = "stopped"
	} else {
		runningCount := 0
		for _, container := range containers {
			if container.Status == "running" {
				runningCount++
			}
		}

		if runningCount == 0 {
			service.Status = "stopped"
		} else if runningCount == len(containers) {
			service.Status = "running"
		} else {
			service.Status = "partial"
		}
	}

	return nil
}

func (sm *ServiceManager) startService(serviceName string) error {
	service, exists := sm.services[serviceName]
	if !exists {
		return fmt.Errorf("service %s not found", serviceName)
	}

	cmd := exec.Command("docker", "compose", "up", "-d")
	cmd.Dir = service.Path

	return cmd.Run()
}

func (sm *ServiceManager) stopService(serviceName string) error {
	service, exists := sm.services[serviceName]
	if !exists {
		return fmt.Errorf("service %s not found", serviceName)
	}

	cmd := exec.Command("docker", "compose", "down")
	cmd.Dir = service.Path

	return cmd.Run()
}

func (sm *ServiceManager) restartService(serviceName string) error {
	if err := sm.stopService(serviceName); err != nil {
		return err
	}

	time.Sleep(2 * time.Second) // Give it a moment to stop

	return sm.startService(serviceName)
}

func (sm *ServiceManager) getServiceLogs(serviceName string, lines int) (string, error) {
	service, exists := sm.services[serviceName]
	if !exists {
		return "", fmt.Errorf("service %s not found", serviceName)
	}

	args := []string{"compose", "logs"}
	if lines > 0 {
		args = append(args, "--tail", fmt.Sprintf("%d", lines))
	}

	cmd := exec.Command("docker", args...)
	cmd.Dir = service.Path

	output, err := cmd.Output()
	if err != nil {
		return "", err
	}

	return string(output), nil
}

func (sm *ServiceManager) updateAllServices() {
	for serviceName := range sm.services {
		if err := sm.updateServiceStatus(serviceName); err != nil {
			log.Printf("Error updating status for service %s: %v", serviceName, err)
		}
	}
}

func (sm *ServiceManager) setupRoutes() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// Serve static files
	r.Static("/static", "./static")
	r.LoadHTMLGlob("templates/*")

	// API routes
	api := r.Group("/api")
	{
		api.GET("/services", sm.handleGetServices)
		api.POST("/services/:name/start", sm.handleStartService)
		api.POST("/services/:name/stop", sm.handleStopService)
		api.POST("/services/:name/restart", sm.handleRestartService)
		api.GET("/services/:name/logs", sm.handleGetLogs)
		api.GET("/services/:name/status", sm.handleGetServiceStatus)
	}

	// WebSocket endpoint for real-time updates
	r.GET("/ws", sm.handleWebSocket)

	// Main dashboard
	r.GET("/", sm.handleDashboard)

	return r
}

func (sm *ServiceManager) handleGetServices(c *gin.Context) {
	sm.updateAllServices()

	var services []*Service
	for _, service := range sm.services {
		services = append(services, service)
	}

	// Sort services by name
	sort.Slice(services, func(i, j int) bool {
		return services[i].Name < services[j].Name
	})

	c.JSON(http.StatusOK, services)
}

func (sm *ServiceManager) handleStartService(c *gin.Context) {
	serviceName := c.Param("name")

	if err := sm.startService(serviceName); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Update status after starting
	time.Sleep(2 * time.Second)
	sm.updateServiceStatus(serviceName)

	c.JSON(http.StatusOK, gin.H{"message": fmt.Sprintf("Service %s started", serviceName)})
}

func (sm *ServiceManager) handleStopService(c *gin.Context) {
	serviceName := c.Param("name")

	if err := sm.stopService(serviceName); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Update status after stopping
	time.Sleep(2 * time.Second)
	sm.updateServiceStatus(serviceName)

	c.JSON(http.StatusOK, gin.H{"message": fmt.Sprintf("Service %s stopped", serviceName)})
}

func (sm *ServiceManager) handleRestartService(c *gin.Context) {
	serviceName := c.Param("name")

	if err := sm.restartService(serviceName); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Update status after restarting
	time.Sleep(3 * time.Second)
	sm.updateServiceStatus(serviceName)

	c.JSON(http.StatusOK, gin.H{"message": fmt.Sprintf("Service %s restarted", serviceName)})
}

func (sm *ServiceManager) handleGetLogs(c *gin.Context) {
	serviceName := c.Param("name")
	lines := 100 // Default to 100 lines

	if linesParam := c.Query("lines"); linesParam != "" {
		if parsedLines, err := fmt.Sscanf(linesParam, "%d", &lines); err != nil || parsedLines != 1 {
			lines = 100
		}
	}

	logs, err := sm.getServiceLogs(serviceName, lines)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"logs": logs})
}

func (sm *ServiceManager) handleGetServiceStatus(c *gin.Context) {
	serviceName := c.Param("name")

	if err := sm.updateServiceStatus(serviceName); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	service, exists := sm.services[serviceName]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Service not found"})
		return
	}

	c.JSON(http.StatusOK, service)
}

func (sm *ServiceManager) handleWebSocket(c *gin.Context) {
	conn, err := sm.upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("Failed to upgrade connection: %v", err)
		return
	}
	defer conn.Close()

	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			sm.updateAllServices()

			var services []*Service
			for _, service := range sm.services {
				services = append(services, service)
			}

			sort.Slice(services, func(i, j int) bool {
				return services[i].Name < services[j].Name
			})

			if err := conn.WriteJSON(services); err != nil {
				log.Printf("WebSocket write error: %v", err)
				return
			}
		}
	}
}

func (sm *ServiceManager) handleDashboard(c *gin.Context) {
	c.HTML(http.StatusOK, "dashboard.html", gin.H{
		"title": "Service Manager Dashboard",
	})
}

func main() {
	// Get the current working directory as the root path
	rootPath, err := os.Getwd()
	if err != nil {
		log.Fatal("Failed to get working directory:", err)
	}

	// Navigate up to the project root (assuming we're in services/service_manager)
	rootPath = filepath.Join(rootPath, "..", "..")
	rootPath, err = filepath.Abs(rootPath)
	if err != nil {
		log.Fatal("Failed to get absolute path:", err)
	}

	log.Printf("Using root path: %s", rootPath)

	sm := NewServiceManager(rootPath)

	// Discover services
	if err := sm.discoverServices(); err != nil {
		log.Fatal("Failed to discover services:", err)
	}

	log.Printf("Discovered %d services", len(sm.services))
	for name := range sm.services {
		log.Printf("  - %s", name)
	}

	// Initial status update
	sm.updateAllServices()

	// Setup routes
	r := sm.setupRoutes()

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "9000"
	}

	log.Printf("Starting Service Manager on port %s", port)
	log.Fatal(r.Run(":" + port))
}
