import azure.functions as func
import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="mallSendMail")
def mallSendMail(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    mail_title = req.params.get('mail_title')
    if not mail_title:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            mail_title = req_body.get('mail_title')

    if mail_title:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login('<me>@knou.ac.kr', '<발급비밀번호>')
        msg = MIMEText(mail_title)
        msg['Subject'] = Header('클라우드 컴퓨팅 메일 보내기 예제입니다', 'utf-8')
        smtp.sendmail('<me>@knou.ac.kr', '<to>', msg.as_string())
        smtp.quit()

        return func.HttpResponse(f"Hello {mail_title}!")
    else:
        return func.HttpResponse(
             "Please pass a mail_title on the query string or in the request body",
             status_code=400
        )
