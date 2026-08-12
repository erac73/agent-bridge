package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Heartbeat {
    @JsonProperty("agent_id")
    public String agentId;
    @JsonProperty("active_tasks")
    public Integer activeTasks;
    @JsonProperty("pending_tasks")
    public Integer pendingTasks;
    public Map<String, Object> metrics;
}
