from exchangelib import Credentials, Account
import memobird_agent
import re

EMAIL = ''
PW = ''

SMARTID = ''
USERID = ''

def add_section_header(doc, section_name):
    pass

def add_email(doc, sender_name, sender_email, subject, text_body, limit=50):
    # Process text_body to replace link and image
    text_body = re.sub(r'\[.+\]','[image]', text_body)
    text_body = re.sub(r'\<.+\>', '<link>', text_body)

    # Process text_body to limit length
    if len(text_body) > limit:
        text_body = text_body[:limit]
        text_body += '\n\n      !!! Email Cropped !!!'
    
    # Append content to document
    doc.add_text("From: ", bold=1)
    doc.add_text(sender_name)
    doc.add_text(sender_email)
    doc.add_text("Subject: ", bold=1)
    doc.add_text(subject)
    doc.add_text()  # empty line
    doc.add_text(text_body.strip())
    doc.add_sticker(42)

    return doc

if __name__ == '__main__':
    credentials = Credentials(EMAIL, PW)
    account = Account(EMAIL, credentials=credentials, autodiscover=True)

    # Print email in inbox
    # for item in account.inbox.all().order_by('-datetime_received')[:10]:
    #     print(item.subject, item.sender, item.datetime_received)

    # List folder tree
    #print(account.root.tree())

    # Set folder
    folder = account.root / 'Top of Information Store' / ''

    doc = memobird_agent.Document()
    doc.add_text('Email', font_size=2)
    has_new_email = False

    for item in folder.all():
        # if the document is read then don't print it
        if item.is_read:
            continue

        # Print the email
        add_email(doc, item.sender.name, item.sender.email_address, item.subject, item.text_body)
        has_new_email = True

        # Set the email to read
        item.is_read = True
        item.save(update_fields=['is_read'])

    doc.add_sticker(41)

    if has_new_email:
        doc.print(SMARTID, USERID)
