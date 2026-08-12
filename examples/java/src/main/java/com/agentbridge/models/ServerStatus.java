package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ServerStatus {
    public String hostname;
    @JsonProperty("cpu_percent")
    public Double cpuPercent;
    @JsonProperty("cpu_count")
    public Integer cpuCount;
    @JsonProperty("load_avg_1")
    public Double loadAvg1;
    @JsonProperty("load_avg_5")
    public Double loadAvg5;
    @JsonProperty("load_avg_15")
    public Double loadAvg15;
    @JsonProperty("memory_total_gb")
    public Double memoryTotalGb;
    @JsonProperty("memory_used_gb")
    public Double memoryUsedGb;
    @JsonProperty("memory_percent")
    public Double memoryPercent;
    @JsonProperty("disk_total_gb")
    public Double diskTotalGb;
    @JsonProperty("disk_used_gb")
    public Double diskUsedGb;
    @JsonProperty("disk_percent")
    public Double diskPercent;
    @JsonProperty("net_sent_gb")
    public Double netSentGb;
    @JsonProperty("net_recv_gb")
    public Double netRecvGb;
    @JsonProperty("kernel_version")
    public String kernelVersion;
    public List<ServiceInfo> services;
}
