
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
    var config={
    	'meeting_id':'bhaari-dummy',
    	'user_email':makeid()+"."+makeid()
    }

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

			// convert blob to URL so it can be assigned to a audio src attribute
            console.log(JSON.stringify(config));
			uploadBlobToLambda(blob,"webm",config)
			// createAudioElement(URL.createObjectURL(blob),"webm");
            //flush
            chunks = [];
      }
    };

    jQuery("body").append('<div id="genie-app-start-button">foo</div>');
    var $start_input = $('<input type="button" id="star-rec" value="Start Meeting" '+
        'style="width: 150px;padding-top: 10px;top: 100px;left: 100px;position: absolute;padding-bottom: 10px; z-index: 1;">')
    .click(startRec);
    jQuery("#genie-app-start-button").html($start_input);
    
    jQuery("body").append('<div id="genie-app-stop-button">foo</div>');
    var $stop_input = $('<input type="button" id="stop-rec" value="Stop Meeting" '+
        'style="width: 150px;padding-top: 10px;top: 100px;left: 100px;position: absolute;padding-bottom: 15px; z-index: 1;">')
    .click(stopRec);
    jQuery("#genie-app-stop-button").html($stop_input);
    document.getElementById('stop-rec').style.display = "none";


    function startRec() {
        if(window.location.host == "hangouts.google.com"){
            config['meeting_id']=window.location.href.split("/call/")[1].replace("-","");
        }
        config['user_email']=makeid()+"."+makeid()
        console.log("started recording: "+JSON.stringify(config))
        document.getElementById('star-rec').style.display = "none";
        recorder.start(500);
        document.getElementById('stop-rec').style.display = "block";
    }

    function stopRec() {
        console.log("stopping recording: "+JSON.stringify(config))
        document.getElementById('stop-rec').style.display = "none";
        recorder.stop();
        console.log('ending localMediaStream');
        document.getElementById('star-rec').style.display = "block";
    }
    
    
  }).catch(console.error);