
chrome.extension.sendMessage({"start":true});

S3UploadURL="https://cmb1mij1sc.execute-api.us-west-2.amazonaws.com/prod/encode-and-upload-s3"

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

function uploadBlobToLambda(blobObject,type,config){
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
			'meeting_id':config['meeting_id'],
	        'username':config['user_email'],
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
    var config={
    	'meeting_id':'12378123456789',
    	'user_email':"we.mohammad@gmail.com"
    }

    // create media recorder instance to initialize recording
    const recorder = new MediaRecorder(stream);
    // function to be called when data is received
    recorder.ondataavailable = e => {
      // add stream data to chunks
	  // var mp3Data = [];
      chunks.push(e.data);

      // if recorder is 'inactive' then recording has finished
      if (recorder.state == 'inactive') {
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