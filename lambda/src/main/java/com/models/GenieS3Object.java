package main.java.com.models;

import lombok.Builder;
import lombok.Data;


@Data
@Builder
public class GenieS3Object {
    String bucket;
    String region;
    String audioFileKey;
    String userId;
    String meetingId;
    String transcribedFileKey;

    public String getTranscriptionJobName() {
        return String.format("genie_transcribe_%s_%s", meetingId, userId);
    }
}
