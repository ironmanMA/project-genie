import json
import time
import smtplib
import email.message
import boto3
import json
from datetime import datetime

s3_client = boto3.client('s3')
BUCKET_NAME = 'project-genie-meetings'

lookUpKeys = ["block", "please", "will", "would", "could", "should", "critical", "create"]
nextMoveWordLength = 4


def findTasks(corpus):
    tasks = []
    corpusArray = corpus.split(" ")
    for wordIndex in range(len(corpusArray)):
        currWord = corpusArray[wordIndex]
        if any(word in currWord for word in lookUpKeys):
            taskPhraseArray = corpusArray[wordIndex:wordIndex + nextMoveWordLength]
            taskPhrase = " ".join(taskPhraseArray) + "..."
            tasks.append(taskPhrase)
            if len(tasks) == 3:
                return tasks
    return tasks


def getFileAsString(event):
    key_name = event["Records"][0]["s3"]["object"]["key"]
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key_name)
    return json.loads(response['Body'].read())


def lambda_handler(event, context):
    print (event)
    email_list = ["ayush.ayush1994@gmail.com", "we.mohammad@gmail.com"]

    transcript_json = getFileAsString(event)["userData"]
    corpus = ""

    meeting_date = ""
    start_time = ""
    end_time = ""
    time_format = '%a %b %d %X UTC %Y'

    for key in transcript_json:
        print(key)
        corpus += transcript_json[key]["transcript"] + " "
        if len(meeting_date) == 0:
            datetime_object = datetime.strptime(transcript_json[key]["creationTime"], time_format)
            meeting_date = datetime_object.strftime('%d, %b %Y')
            start_time = datetime_object
            end_time = datetime.strptime(transcript_json[key]["completionTime"], time_format)
        else:
            if start_time > datetime.strptime(transcript_json[key]["creationTime"], time_format):
                start_time = datetime.strptime(transcript_json[key]["creationTime"], time_format)
            if end_time < datetime.strptime(transcript_json[key]["completionTime"], time_format):
                end_time = datetime.strptime(transcript_json[key]["completionTime"], time_format)

    email_content_template = get_email_content()

    email_content_template = email_content_template.replace("__DATE__", meeting_date)
    email_content_template = email_content_template.replace("__START_TIME__", start_time.strftime('%H:%M'))
    email_content_template = email_content_template.replace("__END_TIME__", end_time.strftime('%H:%M'))

    curr = 0
    allTasks = findTasks(corpus)
    for taskPhrase in allTasks:
        curr = curr + 1
        email_content_template = email_content_template.replace("__TASK" + str(curr) + "_DESC__", taskPhrase)
        email_content_template = email_content_template.replace("__TASK" + str(curr) + "_DEV__", "Manager")

    email_content_template = email_content_template.replace("__ACTUAL_SUMMARY__", corpus)

    msg = email.message.Message()
    currentTime = int(time.strftime('%H'))
    greeting = "Morning"
    if currentTime < 12:
        greeting = "Morning"
    if currentTime > 12:
        greeting = "Afternoon"
    if currentTime > 6:
        greeting = "Evening"
    msg['Subject'] = '[Your ' + greeting + ' Meeting Genie Minutes]'

    msg['From'] = 'mygenieassistant@gmail.com'
    msg['To'] = ", ".join(email_list)
    password = "projectgenie2018"
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_content_template)

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    return server.sendmail(msg['From'], [msg['To']], msg.as_string())


def get_email_content():
    return """
    <html><head>
        <meta http-equiv="Content-Type" content="text/html" charset="iso-8859-1">
        <meta name="format-detection" content="telephone=no">
        <meta name="x-apple-disable-message-reformatting">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0;">
        <title>Genie Meetings</title>
        <style type="text/css">
        * { padding: 0px; margin: 0px;}
        html {-webkit-text-size-adjust: none; -webkit-font-smoothing: antialiased;}
        a {outline: 0;}
        img {display: block;}
        td {mso-line-height-rule: exactly;}
        .outlookFix {text-decoration: underline;}
        /* Base Media Queries */
        @media (max-width: 480px) {
        * { -webkit-text-size-adjust: none; -ms-text-size-adjust: none; -webkit-font-smoothing: antialiased;}/*Stop iproducts from auto-resizing text*/
        .container {width:318px !important;}/*container width*/
        .height {height:auto !important;}/*See Movie cell height size adjust*/
        .hide {display:none !important;}
        .w100P {width:100% !important;}
        .mob-header {width: 80px !important;}
        .w95 {width:95% !important;}
        .w100 {width: 100px !important;}
        .w110 {width: 110px !important;}
        .w120 {width: 120px !important;}
        .font8{font-size: 8px !important;}
        .font9{font-size: 9px !important;}
        .font10{font-size: 10px !important;}
        .font12{font-size: 12px !important;}
        .font15{font-size: 15px !important;}
        .new-record-resize{width: 70px !important; height: auto !important;}
        .W100P {width:100% !important; height:auto !important;}/
        .width {width:318px !important;}/*cell width adjust*/
        .W300 {width:300px !important;}/*cell width adjust*/
        .paddingsides {padding:0 5px 0 5px !important;}/*Footer side padding*/
        .padd-left-15{padding-left:15px !important;}
        .padd-top{padding-top: 30px !important;}
        .font25{font-size: 20px !important; vertical-align: middle !important;}
        .font12{font-size: 12px !important; line-height: 25px !important;}
        .font10{font-size: 10px !important;}
        .font8{font-size: 8px !important;}
        .font55{font-size: 40px !important; vertical-align: bottom !important;}
        .img-width{width: 150px !important;}
        .mob-btn-size{width: 50px !important; height: 22px !important; padding-top:5px !important;}
        .img50P{width: 50px !important;}
        .img75P{width: 75px !important;}
        .img15P{width: 15px !important;}
        .mob-right-graph{width: 45% !important;}
        .mob-left-graph{width: 55% !important; padding-left: 10px !important;}
        /*    .show {display: block !important; max-height: none !important; overflow:visible !important; line-height:normal !important;}
        .showTable {display: block !important;}*/
        }
        </style>
    </head>
    <body bgcolor="#F5F6FB" style="-webkit-text-size-adjust: none; -ms-text-size-adjust: none; -webkit-font-smoothing: antialiased; padding:0px;">
    
        
        <table cellpadding="0" cellspacing="0" border="0" align="center" width="100%" bgcolor="#F5F6FB" class="W100P" style="margin:0 auto;">
            <tbody><tr>
                <td align="center">
                    <table cellpadding="0" cellspacing="0" border="0" width="550" class="w100P">
                        <!--Spacer-->
                        <tbody><tr>
                            <td bgcolor="#F5F6FB" height="20" style="line-height:20px; font-size:20px;">&nbsp;</td>
                        </tr>
                        <!--SPACER END -->
                        <!-- NAV -->
                        <tr>
                            <td align="center">
                                <table width="100%" bgcolor="#F5F6FB" cellpadding="0" cellspacing="0" border="0" align="center" class="w95">
                                    <tbody><tr>
                                        <td align="left" valign="top" style="text-align: left">
                                            <img class="height img-width" src="http://acme-world.com/wp-content/themes/immersivegarden/images/logo-acme-dark.png" width="171" height="40" style="width:150px; height:50px; max-width:237px; font-family:Helvetica, arial, sans-serif; font-size:24px; line-height:40px;" alt="Grammarly" border="0">
                                        </td>
                                        <td align="right" valign="center" style="font-family: Helvetica, arial, sans-serif; font-size: 14px; line-height: 21px;color: #28B473;">
                                            <a href="https://www.grammarly.com/signin?utm_campaign=Stats2point0_021218&amp;utm_medium=email&amp;afterLogin=1&amp;utm_content=Stats1D&amp;utm_source=WeeklyStats" style="color: #4CBAF6; text-decoration:none; white-space: nowrap" class="hover" alis="ftr-upgrade-premium" target="_blank">Visit My Calender</a>
                                        </td>
                                    </tr>
                                </tbody></table>
                            </td>
                        </tr>
                        <!-- /NAV -->
                        <!--Spacer-->
                        <tr>
                            <td bgcolor="#F5F6FB" height="20" style="line-height:20px; font-size:20px;">&nbsp;</td>
                        </tr>
                        <!--SPACER END -->
                        <!-- CONTENT -->
                        <!-- COMMENT -->
                        <tr>
                            <td align="center" class="w100P">
                                <table cellpadding="0" cellspacing="0" border="0" class="w100P" bgcolor="#FFFFFF" width="100%">
                                    <tbody><tr>
                                        <td align="center">
                                            <table cellpadding="0" cellspacing="0" border="0" class="w100P">
                                                <tbody><tr>
                                                    <td bgcolor="#ffffff" height="30" style="line-height:30px; font-size:30px;">&nbsp;</td>
                                                </tr>
                                                <tr>
                                                    <td align="center" style="color:#C7CED9;font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:150%;font-weight:normal;">
                                                        <table cellpadding="0" cellspacing="0" border="0">
                                                            
                                                            <tbody><tr>
                                                                <td width="100%" align="center" style="color:#7e828a;font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:150%;font-weight:normal;text-align: center;">
                                                                    __DATE__ __START_TIME__- __END_TIME__
                                                                </td>
                                                                <td width="60" class="hide"></td>
                                                                <td width="60"></td>
                                                                <td width="100"></td>
                                                                
                                                            </tr>
                                                        </tbody></table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td align="center">
                                                        <table cellpadding="0" cellspacing="0" border="0" class="w95">
                                                            <tbody><tr>
                                                                <td bgcolor="#ffffff" height="5" style="line-height:5px; font-size:5px;">&nbsp;</td>
                                                            </tr>
                                                            <tr>
                                                                <td width="480" align="center" style="color:#555C6A;font-family:Helvetica,Arial,sans-serif;font-size:25px;line-height:150%;font-weight:normal;">
                                                                    Your Sprint Meeting Summary
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td bgcolor="#ffffff" height="10" style="line-height:10px; font-size:10px;">&nbsp;</td>
                                                            </tr>
                                                            <tr>
                                                                <td width="480" align="center" style="color:#555C6A;font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:150%;font-weight:normal;">
                                                                    __ACTUAL_SUMMARY__
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td bgcolor="#ffffff" height="40" style="line-height:40px; font-size:40px;">&nbsp;</td>
                                                            </tr>
                                                        </tbody></table>
                                                    </td>
                                                </tr>
                                            </tbody></table>
                                        </td>
                                    </tr>               
                
                <tr>
                    <td bgcolor="#F5F6FB" height="20" style="line-height:20px; font-size:20px;">&nbsp;</td>
                </tr>
                
                <tr>
                    <td align="center" class="w100P" bgcolor="#FFFFFF">
                        <table cellpadding="0" cellspacing="0" border="0" class="w100P" width="85%">
                            <tbody><tr>
                                <td align="center">
                                    <table cellpadding="0" cellspacing="0" border="0" class="w95">
                                        <tbody><tr>
                                            <td bgcolor="#FFFFFF" height="40" style="line-height:40px; font-size:40px;">&nbsp;</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="color:#FDFDFD;font-family:Helvetica,Arial,sans-serif;font-size:32px;line-height:150%;font-weight:normal;">
                                                <img src="data:image/png;base64,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" width="51" alias="" border="0" style="display:block;">
                                            </td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#FFFFFF" height="10" style="line-height:10px; font-size:10px;">&nbsp;</td>
                                        </tr>
                                        
                                        <tr>
                                            <td align="center" style="color:#2E3543;font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:150%;font-weight:bold;text-transform:uppercase;">
                                                Top 3 New Tasks
                                            </td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#FFFFFF" height="40" style="line-height:40px; font-size:40px;">&nbsp;</td>
                                        </tr>
                                        <tr>
                                            <td width="100%" bgcolor="#F5F5F5" height="2" style="line-height:2px; font-size:2px;">&nbsp;</td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#FFFFFF" height="40" style="line-height:40px; font-size:40px;">&nbsp;</td>
                                        </tr>
                                        <tr>
                                            <td width="470" class="w95" align="center" style="color:#2E3543;font-family:Helvetica,Arial,sans-serif;font-size:19px;line-height:150%;font-weight:normal;">
                                                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                                    
                                                    <tbody>
                                                    <tr>
                                                        <td class="font12" style="color:#2E3543;font-family:Helvetica,Arial,sans-serif;font-size:19px;line-height:150%;font-weight:normal;">
                                                            <span style="color:#3C4555; font-size:16px;font-family:Helvetica,Arial,sans-serif;line-height:150%;font-weight:normal;">1.</span> __TASK1_DESC__
                                                            &nbsp;<a href="https://www.grammarly.com/blog/comma/?&amp;utm_source=WeeklyStats&amp;utm_medium=email&amp;utm_campaign=Stats2point0_021218&amp;utm_content=Stats1D" class="font15" style="text-decoration:none; color:#4D94E5; font-size:15px;" target="_blank">Jira</a>
                                                            
                                                        </td>
                                                        <td class="font15" style="color:#3C4555; font-size:16px;font-family:Helvetica,Arial,sans-serif;line-height:150%;font-weight:normal;">
                                                            __TASK1_DEV__ 
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td bgcolor="#FFFFFF" height="40" style="line-height:40px; font-size:40px;">&nbsp;</td>
                                                    </tr>
                                                    
                                                    <tr>
                                                        <td class="font12" style="color:#2E3543;font-family:Helvetica,Arial,sans-serif;font-size:19px;line-height:150%;font-weight:normal;">
                                                            <span style="color:#3C4555; font-size:16px;font-family:Helvetica,Arial,sans-serif;line-height:150%;font-weight:normal;">2.</span> __TASK2_DESC__&nbsp;<a href="https://www.grammarly.com/blog/comma/?&amp;utm_source=WeeklyStats&amp;utm_medium=email&amp;utm_campaign=Stats2point0_021218&amp;utm_content=Stats1D" class="font15" style="text-decoration:none; color:#4D94E5; font-size:15px;" target="_blank">Jira</a>
                                                            
                                                        </td>
                                                        <td class="font15" style="color:#3C4555; font-size:16px;font-family:Helvetica,Arial,sans-serif;line-height:150%;font-weight:normal;">
                                                            __TASK2_DEV__ 
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td bgcolor="#FFFFFF" height="40" style="line-height:40px; font-size:40px;">&nbsp;</td>
                                                    </tr>
                                                    
                                                    <tr>
                                                        <td class="font12" style="color:#2E3543;font-family:Helvetica,Arial,sans-serif;font-size:19px;line-height:150%;font-weight:normal;">
                                                            <span style="color:#3C4555; font-size:16px;font-family:Helvetica,Arial,sans-serif;line-height:150%;font-weight:normal;">3.</span> __TASK3_DESC__ 
                                                            &nbsp;<a href="https://www.grammarly.com/blog/articles/?utm_campaign=Stats2point0_021218&amp;utm_content=Stats1D&amp;utm_medium=email&amp;utm_source=WeeklyStats" class="font15" style="text-decoration:none; color:#4D94E5; font-size:15px;" target="_blank">Jira</a>
                                                            
                                                        </td>
                                                        <td class="font15" style="color:#3C4555; font-size:16px;font-family:Helvetica,Arial,sans-serif;line-height:150%;font-weight:normal;">
                                                            __TASK3_DEV__ 
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td bgcolor="#FFFFFF" height="40" style="line-height:40px; font-size:40px;">&nbsp;</td>
                                                    </tr>
                                                    
                                                </tbody></table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#FFFFFF" height="10" style="line-height:10px; font-size:10px;">&nbsp;</td>
                                        </tr>
                                    </tbody></table>
                                </td>
                            </tr>
                        </tbody></table>
                    </td>
                </tr>                
            </tbody></table>
        </td>
    </tr>
    
    
    </tbody></table>
    
</td></tr></tbody></table>

<style>
@media print {
/*#_t {
background-image: url('https://wuuxxlxm.emltrk.com/wuuxxlxm?p&d=hello@matthewsmith.cc&#39');
}
}
div.OutlookMessageHeader {
background-image: url('https://wuuxxlxm.emltrk.com/wuuxxlxm?f&d=hello@matthewsmith.cc&#39')
}
table.moz-email-headers-table {
background-image: url('https://wuuxxlxm.emltrk.com/wuuxxlxm?f&d=hello@matthewsmith.cc&#39')
}
blockquote #_t {
background-image: url('https://wuuxxlxm.emltrk.com/wuuxxlxm?f&d=hello@matthewsmith.cc&#39')
}
#MailContainerBody #_t {
background-image: url('https://wuuxxlxm.emltrk.com/wuuxxlxm?f&d=hello@matthewsmith.cc&#39')
}*/
.weekly-email-summary-badge-img{height: auto; width: auto;}
</style>
</body></html>
	
	"""
