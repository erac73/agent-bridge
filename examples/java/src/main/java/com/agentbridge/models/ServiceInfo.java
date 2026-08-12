package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ServiceInfo {
    public String name;
    public String type;
    public String status;
    public String health;
    public Integer pid;
    @JsonProperty("memory_mb")
    public Double memoryMb;
    @JsonProperty("cpu_percent")
    public Double cpuPercent;
    public Map<String, Object> metadata;
}
