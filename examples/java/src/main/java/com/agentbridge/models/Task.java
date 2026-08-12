package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Task {
    public String id;
    public String title;
    public String command;
    public String[] args;
    public String status;
    @JsonProperty("assigned_to")
    public String assignedTo;
    @JsonProperty("exit_code")
    public Integer exitCode;
    public String result;
    public String error;
    public String priority;
}
