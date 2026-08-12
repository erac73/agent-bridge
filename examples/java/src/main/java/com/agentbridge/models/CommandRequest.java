package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CommandRequest {
    public String command;
    public String[] args;
    @JsonProperty("timeout_seconds")
    public int timeoutSeconds = 60;
    @JsonProperty("working_dir")
    public String workingDir;
    public java.util.Map<String, String> env;
}
