package com.agentbridge.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class AgentInfo {
    @JsonProperty("agent_id")
    public String agentId;
    public String hostname;
    @JsonProperty("agent_type")
    public String agentType;
    public String version;
    public List<String> capabilities;
}
