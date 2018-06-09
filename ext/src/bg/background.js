
//example of using a message handler from the inject scripts
chrome.extension.onMessage.addListener(
  function(request, sender, sendResponse) {
  	console.log("request: "+JSON.stringify(request));
  	console.log("sender: "+JSON.stringify(sender));
  	console.log("Hello. This message was printed in background");
});