package main.java.com;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.event.S3EventNotification;
import com.amazonaws.services.s3.model.ListObjectsV2Result;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.transcribe.AmazonTranscribe;
import com.amazonaws.services.transcribe.AmazonTranscribeClientBuilder;
import com.amazonaws.services.transcribe.model.GetTranscriptionJobRequest;
import com.amazonaws.services.transcribe.model.GetTranscriptionJobResult;
import com.amazonaws.services.transcribe.model.Media;
import com.amazonaws.services.transcribe.model.StartTranscriptionJobRequest;
import com.amazonaws.services.transcribe.model.TranscriptionJobStatus;
import main.java.com.models.GenieS3Object;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.ExecutionException;

public class AudioTranscribeLambda {

    public String handleRequest(final S3Event s3Event, final Context context) throws ExecutionException, InterruptedException, IOException {
        final LambdaLogger logger = context.getLogger();
        final AmazonS3 s3 = AmazonS3ClientBuilder.defaultClient();
        List<S3EventNotification.S3EventNotificationRecord> s3EventRecord = s3Event.getRecords();

        //We would have one event per one put request in S3 as per current setup
        //Refer to https://stackoverflow.com/questions/40765699/how-many-records-can-be-in-s3-put-event-lambda-trigger
        S3EventNotification.S3EventNotificationRecord s3EventNotificationRecord = s3EventRecord.get(0);
        String key = s3EventNotificationRecord.getS3().getObject().getKey();
        String bucket = s3EventNotificationRecord.getS3().getBucket().getName();
        String region = s3EventNotificationRecord.getAwsRegion();

        S3Object s3Object = s3.getObject(bucket, key);
        ObjectMetadata s3ObjectMetadata = s3Object.getObjectMetadata();
        logger.log("MetaData Content: "+s3ObjectMetadata.getContentType());
        String meetingId = s3ObjectMetadata.getUserMetaDataOf("meeting_id");
        String userId = s3ObjectMetadata.getUserMetaDataOf("username");

        GenieS3Object genieS3Object = GenieS3Object.builder()
                .audioFileKey(key)
                .bucket(bucket)
                .region(region)
                .meetingId(meetingId)
                .userId(userId).build();

//      Call Transcribe
        AmazonTranscribe amazonTranscribe = AmazonTranscribeClientBuilder.defaultClient();
        startTranscribeJob(genieS3Object, amazonTranscribe);

        //Poll for Transcribe Job Completion
        GetTranscriptionJobResult getTranscriptionJobResult = null;
        Boolean flag = true;
        while (flag) {
            getTranscriptionJobResult = amazonTranscribe.getTranscriptionJob(
                    new GetTranscriptionJobRequest().withTranscriptionJobName(genieS3Object.getTranscriptionJobName()));
            switch (TranscriptionJobStatus.fromValue(getTranscriptionJobResult.getTranscriptionJob().getTranscriptionJobStatus())) {
                case COMPLETED:
                    writeTranscribedFileToS3(getTranscriptionJobResult, genieS3Object, s3);
                    if (isLastCall(genieS3Object, s3)) {
                        //TODO Merging logic
                        logger.log("THIS IS THE LAST CALL");
                    }
                    return "Write Completed";
                case FAILED:
                    return TranscriptionJobStatus.FAILED.toString();
                default:
                    Thread.sleep(1000);
            }
        }
        return "Unexpected";
    }

    private void writeTranscribedFileToS3(final GetTranscriptionJobResult completedTranscriptionJobResult, final GenieS3Object genieS3Object, final AmazonS3 s3Client) throws IOException {

        //Make http get call
        final CloseableHttpClient httpClient = HttpClientBuilder.create().build();
        final HttpGet request = new HttpGet(completedTranscriptionJobResult.getTranscriptionJob().getTranscript().getTranscriptFileUri());
        HttpResponse response = httpClient.execute(request);

        //S3 put call
        String transcribedAudioKey = String.format("meeting_%s/transcribed_text/%s.txt", genieS3Object.getMeetingId(), genieS3Object.getUserId());
        s3Client.putObject(genieS3Object.getBucket(),
                transcribedAudioKey,
                response.getEntity().getContent(),
                new ObjectMetadata());
    }

    private void startTranscribeJob(final GenieS3Object genieS3Object, AmazonTranscribe amazonTranscribeClient) {
        StartTranscriptionJobRequest jobRequest = new StartTranscriptionJobRequest();
        jobRequest.setLanguageCode("en-US");
        jobRequest.setMedia(new Media().withMediaFileUri(String.format("https://s3-%s.amazonaws.com/%s/%s",
                genieS3Object.getRegion(),
                genieS3Object.getBucket(),
                genieS3Object.getAudioFileKey())));
        jobRequest.setTranscriptionJobName(genieS3Object.getTranscriptionJobName());
        jobRequest.setMediaFormat("mp3");
        amazonTranscribeClient.startTranscriptionJob(jobRequest);
    }

    private Boolean isLastCall(final GenieS3Object genieS3Object, final AmazonS3 s3Client) {
        ListObjectsV2Result listObjects = s3Client.listObjectsV2(genieS3Object.getBucket(),
                String.format("meeting_%s/transcribed_text", genieS3Object.getMeetingId()));

        //TODO Logic only for 2 clients. Needs to be updated
        return listObjects.getKeyCount() == 1;
    }
}


//    String[] values = key.split("/");
//        logger.log("KEY: " + values.length);
//                String keyMain = values[2];
//                logger.log("KEY_MAIN: " + keyMain);
//                keyMain = values[2].split("\\.")[0];
//                String textKey = values[0] + "/transcribed_text/" + values[2] + ".txt";