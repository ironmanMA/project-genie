
chrome.extension.sendMessage({"start":true});

S3UploadURL="https://cmb1mij1sc.execute-api.us-west-2.amazonaws.com/prod/encode-and-upload-s3"
Complete="https://cmb1mij1sc.execute-api.us-west-2.amazonaws.com/prod/endMeeting"

genie_mail="mygenie@gmail.com"

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

function makeid() {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

  for (var i = 0; i < 5; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
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
    	'user_email':makeid()+"."+makeid()
    }

    if(window.location.host == "hangouts.google.com"){
        config['meeting_id']=window.location.href.split("/call/")[1].replace("-","");
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
			uploadBlobToLambda(blob,"webm",config)
			createAudioElement(URL.createObjectURL(blob),"webm");

      }
    };

    jQuery("body").append('<div id="genie-app">foo</div>');
    var $input = $('<input type="button" id="star-rec" value="Start Meeting" style="width: 150px;padding-top: 10px;top: 100px;left: 100px;position: absolute;padding-bottom: 10px; z-index: 1;">').click(startRec);
    jQuery("#genie-app").html($input);
    
    
    function startRec() {
        console.log("started recording: "+config)
        document.getElementById('star-rec').style.display = "none";
        recorder.start(1000);
        // setTimeout to stop recording after 4 seconds
        setTimeout(() => {
            // this will trigger one final 'ondataavailable' event and set recorder state to 'inactive'        
            recorder.stop();
            console.log('ending localMediaStream');
        }, 20000);
    }
    
    
  }).catch(console.error);