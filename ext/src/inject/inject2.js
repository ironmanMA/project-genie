var format="mp3"
var quality=192

navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
	console.log('got localMediaStream');
	const audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);
    let mediaRecorder = new Recorder(source); //initiates the recorder based on the current stream
    mediaRecorder.setEncoding(format); //sets encoding based on options
	mediaRecorder.setOptions({timeLimit: 10800});
	mediaRecorder.setOptions({mp3: {bitRate: quality}});
	mediaRecorder.startRecording();

	setTimeout(() => {
        // this will trigger one final 'ondataavailable' event and set recorder state to 'inactive'
        mediaRecorder.finishRecording();
        console.log('got localMediaStream');
    }, 5000);

    // store streaming data chunks in array
    var chunks = [];
    var mp3Data = [];
    var mp3encoder = new lamejs.Mp3Encoder(1, 44100, 128); //mono 44.1khz encode to 128kbps

    // create media recorder instance to initialize recording
    const recorder = new MediaRecorder(stream);
    // function to be called when data is received
    recorder.ondataavailable = e => {
      // add stream data to chunks

      chunks.push(e.data);
      // if recorder is 'inactive' then recording has finished
      if (recorder.state == 'inactive') {

          // convert stream data chunks to a 'webm' audio format as a blob          
			const blob = new Blob(chunks, { type: 'audio/webm' });
			console.log(blob);

          // convert to mp3
          	var arrayBuffer;
			var fileReader = new FileReader();
			fileReader.onload = function() {
			    arrayBuffer = this.result;
			};
			fileReader.readAsArrayBuffer(blob);
			
			var samples = new Int16Array(fileReader.result) // also accessible this way once the blob has been read

			sampleBlockSize = 1152; //can be anything but make it a multiple of 576 to make encoders life easier
			var mp3Data = [];
			
			for (var i = 0; i < zx.length; i += sampleBlockSize) {
			  sampleChunk = samples.subarray(i, i + sampleBlockSize);
			  var mp3buf = mp3encoder.encodeBuffer(sampleChunk);
			  if (mp3buf.length > 0) {
			      mp3Data.push(mp3buf);
			  }
			}
			var mp3buf = mp3encoder.flush();   //finish writing mp3

			if (mp3buf.length > 0) {
			    mp3Data.push(new Int8Array(mp3buf));
			}

			var blob_mp3 = new Blob(mp3Data, {type: 'audio/mp3'});
			uploadBlobToLambda(blob_mp3,"mp3")
			createAudioElement(URL.createObjectURL(blob_mp3),"mp3");

          // convert blob to URL so it can be assigned to a audio src attribute
          // uploadBlobToLambda(blob,"webm")
          // createAudioElement(URL.createObjectURL(blob),"webm");

      }
    };
    // start recording with 1 second time between receiving 'ondataavailable' events
    recorder.start(1000);
    // setTimeout to stop recording after 4 seconds
    setTimeout(() => {
        // this will trigger one final 'ondataavailable' event and set recorder state to 'inactive'
        recorder.stop();
        console.log('got localMediaStream');
    }, 5000);
  }).catch(console.error);