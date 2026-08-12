package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CommandResult {
    @JsonProperty("request_id")
    public String requestId;
    @JsonProperty("exit_code")
    public Integer exitCode;
    public String stdout;
    public String stderr;
    @JsonProperty("duration_seconds")
    public Double durationSeconds;
}
