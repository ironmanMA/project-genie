
chrome.extension.sendMessage({"start":true});

S3UploadURL="https://cmb1mij1sc.execute-api.us-west-2.amazonaws.com/prod/upload-to-s3"

// appends an audio element to playback and download recording
function createAudioElement(blobUrl, type) {
    const downloadEl = document.createElement('a');
    downloadEl.style = 'display: block';
    downloadEl.innerHTML = 'download';
    downloadEl.download = 'audio.'+type;
    downloadEl.href = blobUrl;
    const audioEl = document.createElement('audio');
    audioEl.controls = true;
    const sourceEl = document.createElement('source');
    sourceEl.src = blobUrl;
    sourceEl.type = 'audio/'+type;
    audioEl.appendChild(sourceEl);
    document.body.appendChild(audioEl);
    document.body.appendChild(downloadEl);
    console.log(downloadEl)
}

function uploadBlobToLambda(blobObject,type){
	var milliseconds = Math.floor((new Date).getTime()/1000);
	 var reader = new FileReader();
	 reader.readAsDataURL(blobObject); 
	 base64data=""
	 reader.onloadend = function() {
	     base64data = reader.result;
	     jQuery.ajax({
		    type: 'POST',
		    url: S3UploadURL,
		    data: base64data,
	        headers: { 
			'meeting_id': '12378123456789',
	        'username':"user1",
	        'audio_part_name':milliseconds+"."+type,
	        'Content-Type':'audio/'+type },
		    processData: false,
		    contentType: false
		}).done(function(data) {
		       console.log(data);
		});
	 }

}
// request permission to access audio stream
navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
	console.log('got localMediaStream');
    // store streaming data chunks in array
    var chunks = [];
    var mp3Data = [];
    var mp3encoder = new lamejs.Mp3Encoder(1, 44100, 128); //mono 44.1khz encode to 128kbps

    // create media recorder instance to initialize recording
    const recorder = new MediaRecorder(stream);
    // function to be called when data is received
    recorder.ondataavailable = e => {
      // add stream data to chunks
	  // var mp3Data = [];
      chunks.push(e.data);

      // if recorder is 'inactive' then recording has finished
      if (recorder.state == 'inactive') {
          // convert to mp3
			// var arrayBuffer;
			// var fileReader = new FileReader();
			// fileReader.onload = function() {
			//     arrayBuffer = this.result;
			// };
			// fileReader.readAsArrayBuffer(blob);

			// var samples = new Int16Array(fileReader.result) // also accessible this way once the blob has been read

			// sampleBlockSize = 1152; //can be anything but make it a multiple of 576 to make encoders life easier
			
			// for (var i = 0; i < zx.length; i += sampleBlockSize) {
			//   sampleChunk = samples.subarray(i, i + sampleBlockSize);
			//   var mp3buf = mp3encoder.encodeBuffer(sampleChunk);
			//   if (mp3buf.length > 0) {
			//       mp3Data.push(mp3buf);
			//   }
			// }
			// var mp3buf = mp3encoder.flush();   //finish writing mp3

			// if (mp3buf.length > 0) {
			//     mp3Data.push(new Int8Array(mp3buf));
			// }

			// var blob_mp3 = new Blob(mp3Data, {type: 'audio/mp3'});
			// uploadBlobToLambda(blob_mp3,"mp3")
			// createAudioElement(URL.createObjectURL(blob_mp3),"mp3");

			// convert stream data chunks to a 'webm' audio format as a blob          
			const blob = new Blob(chunks, { type: 'audio/webm' });
			console.log(blob);

			// convert blob to URL so it can be assigned to a audio src attribute
			uploadBlobToLambda(blob,"webm")
			createAudioElement(URL.createObjectURL(blob),"webm");

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