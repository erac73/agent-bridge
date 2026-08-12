package com.agentbridge;

import com.agentbridge.client.AgentClient;
import com.agentbridge.models.*;

import java.util.List;

public class Main {

    private static final String SERVER_URL = "http://100.109.105.19:8000";

    public static void main(String[] args) {
        AgentClient client = new AgentClient(SERVER_URL);

        System.out.println("=== Agent Bridge Java Client ===\n");

        // 1. Health check
        System.out.println("--- Health Check ---");
        HealthStatus health = client.healthCheck();
        System.out.println("Status: " + health.status);

        // 2. Agent info
        System.out.println("\n--- Agent Info ---");
        AgentInfo info = client.getAgentInfo();
        System.out.println("Agent ID:  " + info.agentId);
        System.out.println("Hostname:  " + info.hostname);
        System.out.println("Type:      " + info.agentType);
        System.out.println("Version:   " + info.version);

        // 3. Server status
        System.out.println("\n--- Server Status ---");
        ServerStatus status = client.getServerStatus();
        System.out.println("Hostname:      " + status.hostname);
        System.out.println("CPU:           " + status.cpuPercent + "%");
        System.out.println("Memory:        " + status.memoryUsedGb + " / " + status.memoryTotalGb + " GB (" + status.memoryPercent + "%)");
        System.out.println("Disk:          " + status.diskUsedGb + " / " + status.diskTotalGb + " GB (" + status.diskPercent + "%)");
        System.out.println("Load Average:  " + status.loadAvg1 + " / " + status.loadAvg5 + " / " + status.loadAvg15);
        System.out.println("Kernel:        " + status.kernelVersion);

        // 4. List services
        System.out.println("\n--- Services ---");
        List<ServiceInfo> services = client.getServices();
        System.out.printf("%-25s %-12s %-12s %s%n", "NAME", "TYPE", "STATUS", "PID");
        System.out.println("-".repeat(60));
        for (ServiceInfo svc : services) {
            System.out.printf("%-25s %-12s %-12s %s%n",
                    svc.name, svc.type, svc.status,
                    svc.pid != null ? svc.pid.toString() : "");
        }

        // 5. Execute command
        System.out.println("\n--- Execute Command ---");
        CommandResult result = client.executeCommand("uptime", new String[]{}, 10);
        System.out.println("Exit Code: " + result.exitCode);
        System.out.println("Output:    " + result.stdout.trim());
        System.out.println("Duration:  " + result.durationSeconds + "s");

        // 6. Execute Docker command
        System.out.println("\n--- Docker Containers ---");
        CommandResult docker = client.executeCommand("docker", new String[]{"ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"}, 15);
        System.out.println(docker.stdout);

        System.out.println("\n=== Done ===");
    }
}
