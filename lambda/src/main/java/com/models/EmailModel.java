package main.java.com.models;

import lombok.Data;

import java.util.Map;

@Data
public class EmailModel {

    Map<String, EmailTranscriptDetails> userData;

    public void add(String userId, TranscriptionObject transcriptionObject) {
        String transcript = transcriptionObject.getResults().getTranscripts().get(0).getTranscript();
        String creationTime = transcriptionObject.getCreationTime();
        String completionTime = transcriptionObject.getCreationTime();
        EmailTranscriptDetails emailTranscriptDetails = new EmailTranscriptDetails();
        emailTranscriptDetails.setTranscript(transcript);
        emailTranscriptDetails.setCreationTime(creationTime);
        emailTranscriptDetails.setCompletionTime(completionTime);
        userData.put(userId, emailTranscriptDetails);
    }
}
