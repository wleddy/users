from flask import g, redirect, url_for, \
     render_template, render_template_string
from app import mail, app
from flask_mail import Message
from users.utils import printException, cleanRecordID

def send_message(to_address_list,**kwargs):
    """Send an email with the parameters as:
        to_address_list=[list of tuples (recipient name,recipient address)]=[]
        -- all templates must use 'context' as their only context variable
        **kwargs:
            context = {a dictionary like object with data for rendering all emails} = {}
            body = <text for body of email> = None
            body_text_is_html = <True | False> = False
            text_template=<template to render as plain text message> = None
            html_template=<template to render as html message> = None
            subject=<subject text (will be rendered with the current context>)>= a default subject
            subject_prefix=<some text to prepend to the subject: = ''
            from_address=<from address> = app.config['MAIL_DEFAULT_ADDR']
            from_sender=<name of sender> = app.config['MAIL_DEFAULT_SENDER']
            reply_to_address=<replyto address> = from_address
            reply_to_name=<name of reply to account> = from_sender
            
        On completion returns a tuple of:
            success [True or False]
            message "some message"
    """

    context = kwargs.get('context',{})
    body = kwargs.get('body',None)
    body_is_html = kwargs.get('body_is_html',None)
    text_template = kwargs.get('text_template',None)
    html_template = kwargs.get('html_template',None)
    subject_prefix = kwargs.get('subject_prefix','')
    from_address = kwargs.get('from_address',app.config['MAIL_DEFAULT_ADDR'])
    from_sender = kwargs.get('from_address',app.config['MAIL_DEFAULT_SENDER'])
    reply_to = kwargs.get('reply_to',from_address)
    reply_to_name = kwargs.get('reply_to_name',from_sender)
    subject = subject_prefix + ' ' +kwargs.get('subject','A message from {}'.format(from_sender))
    
    if not text_template and not html_template and not body:
        mes = "No message body was specified"
        printException(mes,"error")
        return (False, mes)
        
    if not to_address_list or len(to_address_list) == 0 or len(to_address_list[0]) != 2:
        mes = "No recipients were specified"
        printException(mes,"error")
        return (False, mes)
        
    with mail.record_messages() as outbox:
        for name,address in to_address_list:
            subject = render_template_string(subject.strip(),context=context)
            #Start a message
            msg = Message( subject,
                          sender=(from_sender, from_address),
                          recipients=[(name, address)])
        
            #Get the text body verson
            if body:
                if body_is_html:
                    msg.html = render_template_string(body, context=context)
                else:
                    msg.body = render_template_string(body, context=context)
            if html_template:
                msg.html = render_template(html_template, context=context)
            if text_template:
                msg.body = render_template(text_template, context=context) 
               
            try:
                mail.send(msg)
            except Exception as e:
                mes = "Error Sending email"
                printException(mes,"error",e)
                return (False, mes)

            if mail.suppress:
                mes = '{} email(s) would have been sent if we were not testing'.format(len(outbox),)
                return (True, mes )
    
            return (True, "Email Sent Successfully")
    
    