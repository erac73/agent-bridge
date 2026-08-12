package com.agentbridge.client;

import com.agentbridge.models.*;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * Java client for Agent Bridge Server Agent REST API.
 * Works with Java 11+ (HttpClient).
 */
public class AgentClient {

    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper mapper;
    private String apiKey;

    public AgentClient(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
        this.mapper = new ObjectMapper();
    }

    public AgentClient(String baseUrl, String apiKey) {
        this(baseUrl);
        this.apiKey = apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    // ── Health ──────────────────────────────────────────────────────

    public HealthStatus healthCheck() {
        return get("/health/live", HealthStatus.class);
    }

    // ── Agent Info ──────────────────────────────────────────────────

    public AgentInfo getAgentInfo() {
        return get("/api/v1/agent", AgentInfo.class);
    }

    public Heartbeat getHeartbeat() {
        return get("/api/v1/agent/heartbeat", Heartbeat.class);
    }

    // ── Server Status ───────────────────────────────────────────────

    public ServerStatus getServerStatus() {
        return get("/api/v1/status", ServerStatus.class);
    }

    // ── Services ────────────────────────────────────────────────────

    public java.util.List<ServiceInfo> getServices() {
        return getList("/api/v1/services", ServiceInfo.class);
    }

    public ServiceInfo getService(String name) {
        return get("/api/v1/services/" + name, ServiceInfo.class);
    }

    public void watchService(String name) {
        post("/api/v1/services/" + name + "/watch", null, Object.class);
    }

    public void restartService(String name) {
        post("/api/v1/services/" + name + "/restart", null, Object.class);
    }

    public void stopService(String name) {
        post("/api/v1/services/" + name + "/stop", null, Object.class);
    }

    public void startService(String name) {
        post("/api/v1/services/" + name + "/start", null, Object.class);
    }

    // ── Commands ────────────────────────────────────────────────────

    public CommandResult executeCommand(String command, String[] args, int timeoutSeconds) {
        CommandRequest request = new CommandRequest();
        request.command = command;
        request.args = args;
        request.timeoutSeconds = timeoutSeconds;
        return post("/api/v1/command", request, CommandResult.class);
    }

    public CommandResult executeCommand(String command) {
        return executeCommand(command, new String[]{}, 60);
    }

    // ── Tasks ───────────────────────────────────────────────────────

    public java.util.List<Task> getTasks() {
        return getList("/api/v1/tasks", Task.class);
    }

    public Task getTask(String taskId) {
        return get("/api/v1/tasks/" + taskId, Task.class);
    }

    public Task createTask(Task task) {
        return post("/api/v1/tasks", task, Task.class);
    }

    public Task runTask(String taskId) {
        return post("/api/v1/tasks/" + taskId + "/run", null, Task.class);
    }

    // ── Alerts ──────────────────────────────────────────────────────

    public java.util.List<Alert> getAlerts() {
        return getList("/api/v1/alerts", Alert.class);
    }

    public void acknowledgeAlert(String alertId) {
        post("/api/v1/alerts/" + alertId + "/ack", null, Object.class);
    }

    // ── HTTP Helpers ────────────────────────────────────────────────

    private <T> T get(String path, Class<T> type) {
        try {
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + path))
                    .timeout(Duration.ofSeconds(30))
                    .GET();
            addAuth(builder);
            HttpResponse<String> response = httpClient.send(builder.build(),
                    HttpResponse.BodyHandlers.ofString());
            return mapper.readValue(response.body(), type);
        } catch (Exception e) {
            throw new RuntimeException("GET " + path + " failed: " + e.getMessage(), e);
        }
    }

    private <T> java.util.List<T> getList(String path, Class<T> type) {
        try {
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + path))
                    .timeout(Duration.ofSeconds(30))
                    .GET();
            addAuth(builder);
            HttpResponse<String> response = httpClient.send(builder.build(),
                    HttpResponse.BodyHandlers.ofString());
            return mapper.readValue(response.body(),
                    mapper.getTypeFactory().constructCollectionType(java.util.List.class, type));
        } catch (Exception e) {
            throw new RuntimeException("GET " + path + " failed: " + e.getMessage(), e);
        }
    }

    private <T> T post(String path, Object body, Class<T> type) {
        try {
            String json = body != null ? mapper.writeValueAsString(body) : "{}";
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + path))
                    .timeout(Duration.ofSeconds(30))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(json));
            addAuth(builder);
            HttpResponse<String> response = httpClient.send(builder.build(),
                    HttpResponse.BodyHandlers.ofString());
            if (type == Object.class) return null;
            return mapper.readValue(response.body(), type);
        } catch (Exception e) {
            throw new RuntimeException("POST " + path + " failed: " + e.getMessage(), e);
        }
    }

    private void addAuth(HttpRequest.Builder builder) {
        if (apiKey != null && !apiKey.isEmpty()) {
            builder.header("Authorization", "Bearer " + apiKey);
        }
    }
}
