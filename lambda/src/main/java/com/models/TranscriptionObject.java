package main.java.com.models;

import com.google.gson.annotations.SerializedName;
import lombok.Data;

@Data
public class TranscriptionObject {
    String jobName;
    String accountId;
    String status;
    Results results;
    String creationTime;
    String completionTime;
}
