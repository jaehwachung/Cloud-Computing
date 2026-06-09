import json
import logging
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from typing import Any, Dict, List, Set

import azure.functions as func


app = func.FunctionApp()

TARGET_SECTIONS = {"transcript", "ocr", "labels", "topics", "keywords"}
TEXT_KEYS = {"text", "name", "value", "displayName"}


def get_required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Application setting '{name}' is not configured.")
    return value


def split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def shorten(text: str, limit: int = 120) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit] + "..."


def collect_texts(node: Any) -> List[str]:
    texts: List[str] = []

    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and key in TEXT_KEYS:
                texts.append(value)
            elif isinstance(value, (dict, list)):
                texts.extend(collect_texts(value))

    elif isinstance(node, list):
        for item in node:
            texts.extend(collect_texts(item))

    return texts


def find_target_sections(node: Any, result: Dict[str, List[str]]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            key_lower = key.lower()

            if key_lower in TARGET_SECTIONS:
                result.setdefault(key_lower, []).extend(collect_texts(value))

            if isinstance(value, (dict, list)):
                find_target_sections(value, result)

    elif isinstance(node, list):
        for item in node:
            find_target_sections(item, result)


def find_keyword_matches(
    section_texts: Dict[str, List[str]],
    keywords: List[str]
) -> Dict[str, Set[str]]:
    matches: Dict[str, Set[str]] = {}

    for section, texts in section_texts.items():
        for text in texts:
            text_lower = text.lower()
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches.setdefault(keyword, set()).add(
                        f"{section}: {shorten(text)}"
                    )

    return matches


def send_mail(subject: str, body: str) -> None:
    smtp_host = get_required_setting("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = get_required_setting("SMTP_USER")
    smtp_password = get_required_setting("SMTP_PASSWORD")
    mail_from = os.getenv("MAIL_FROM", smtp_user)
    mail_to = split_csv(get_required_setting("MAIL_TO"))

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = Header(subject, "utf-8")
    message["From"] = mail_from
    message["To"] = ", ".join(mail_to)

    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as smtp:
        smtp.login(smtp_user, smtp_password)
        smtp.sendmail(mail_from, mail_to, message.as_string())


@app.blob_trigger(
    arg_name="myblob",
    path="insights",
    connection="aivistorage201384_STORAGE",
)
def blob_trigger(myblob: func.InputStream) -> None:
    logging.info("Insights JSON upload detected.")
    logging.info("Blob name: %s", myblob.name)
    logging.info("Blob size: %s bytes", myblob.length)

    if not myblob.name.lower().endswith(".json"):
        logging.info("The uploaded blob is not a JSON file. Processing skipped.")
        return

    keyword_setting = os.getenv("ALERT_KEYWORDS", "")
    keywords = split_csv(keyword_setting)

    if not keywords:
        logging.warning("ALERT_KEYWORDS is empty. Processing skipped.")
        return

    try:
        raw = myblob.read().decode("utf-8-sig")
        insight_json = json.loads(raw)
    except Exception as exc:
        logging.error("Failed to read or parse JSON: %s", exc)
        raise

    section_texts: Dict[str, List[str]] = {}
    find_target_sections(insight_json, section_texts)

    logging.info(
        "Collected sections: %s",
        {section: len(values) for section, values in section_texts.items()},
    )

    matches = find_keyword_matches(section_texts, keywords)

    if not matches:
        logging.info("No alert keyword was found.")
        return

    lines: List[str] = []
    lines.append("Azure AI Video Indexer Insights JSON에서 지정된 키워드가 발견되었습니다.")
    lines.append("")
    lines.append(f"Blob: {myblob.name}")
    lines.append("")
    lines.append("[검색 키워드]")
    lines.append(", ".join(keywords))
    lines.append("")
    lines.append("[발견 결과]")

    for keyword, snippets in matches.items():
        lines.append(f"- {keyword}")
        for snippet in sorted(snippets):
            lines.append(f"  · {snippet}")

    body = "\n".join(lines)
    subject = "[클라우드 컴퓨팅] 미디어 AI 키워드 알림"

    send_mail(subject, body)
    logging.info("Alert mail sent. Matched keywords: %s", list(matches.keys()))
