'''
Created on Apr 8, 2013

@author: roehrig
'''

import smtplib
from email.mime.text import MIMEText

class EmailSender(object):
    '''
    This simply is an object that can be used to send an email.
    It can either read a file for its contents or a user supplied text.
    '''    
    def __init__(self,  emailList=None):
        '''
        Constructor
        
        emailList - a list of wx.TxtCtrl that each contains an email address
        '''
        self._emailList = emailList
        
        return

    def SendEmail(self, sender, subject, text="", useFile=False, fileName=""):
        '''
        Send an email to each person in the email list.
        
        sender - An email address that the email is from.
        subject - The subject line of the email.
        text - The default content of the email.
        useFile - If this equals 0, use the value of text as the email content.
                  If this equals 1, use the content of a file as the email content.
        fileName - The full path to a file that can be used for the email content.
        '''
        
        # Do not try to send an email if there is no one to send it to
        # or no one who is sending it.
        if (not self._emailList == None) and (not len(sender) == 0):
            s = smtplib.SMTP('localhost')
            
            # If useFile = 0, use the value of text as the email content.
            # If useFile = 1, open fileName for reading and use its
            # content for the email.
            if not useFile:
                message = MIMEText(text)
            else:
                try:
                    with open(fileName, "r") as fileHandle:
                        fileHandle.seek(0)
                        message = MIMEText(fileHandle.read())
                except IOError as e:
                    message = MIMEText("Could not open file for email content.\n\n %s" % e)                     
            
            message['Subject'] = subject
            message['From'] = sender
            
            # Send the email to each email address in the list.
            for email in self._emailList:
                receiver = email.GetValue()
                message['To'] = receiver
                s.sendmail(sender, [receiver], message.as_string())
                
        return