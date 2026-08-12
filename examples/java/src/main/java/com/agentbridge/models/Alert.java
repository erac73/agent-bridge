package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Alert {
    public String id;
    public String severity;
    public String title;
    public String message;
    public String source;
    public Boolean acknowledged;
    public Boolean resolved;
}
