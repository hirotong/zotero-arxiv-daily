import pytest
from unittest.mock import patch, MagicMock
from omegaconf import OmegaConf
from zotero_arxiv_daily.utils import send_email


@pytest.fixture
def email_config():
    return OmegaConf.create({
        "email": {
            "sender": "test@example.com",
            "receiver": "recv@example.com",
            "sender_password": "password",
            "smtp_server": "smtp.example.com",
            "smtp_port": 465,
        }
    })


@patch("zotero_arxiv_daily.utils.smtplib")
def test_send_email_port_465_uses_smtp_ssl(mock_smtplib, email_config):
    """Port 465 should use SMTP_SSL (implicit SSL)."""
    email_config.email.smtp_port = 465
    mock_server = MagicMock()
    mock_smtplib.SMTP_SSL.return_value = mock_server

    send_email(email_config, "<p>test</p>")

    mock_smtplib.SMTP_SSL.assert_called_once_with("smtp.example.com", 465)
    mock_smtplib.SMTP.assert_not_called()
    mock_server.login.assert_called_once_with("test@example.com", "password")
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()


@patch("zotero_arxiv_daily.utils.smtplib")
def test_send_email_port_587_uses_starttls(mock_smtplib, email_config):
    """Port 587 should use SMTP + ehlo + starttls + ehlo."""
    email_config.email.smtp_port = 587
    mock_server = MagicMock()
    mock_smtplib.SMTP.return_value = mock_server

    send_email(email_config, "<p>test</p>")

    mock_smtplib.SMTP.assert_called_once_with("smtp.example.com", 587)
    mock_smtplib.SMTP_SSL.assert_not_called()
    assert mock_server.ehlo.call_count == 2
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@example.com", "password")
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()


@patch("zotero_arxiv_daily.utils.smtplib")
def test_send_email_port_25_uses_plain_smtp(mock_smtplib, email_config):
    """Port 25 should use plain SMTP with ehlo but no starttls."""
    email_config.email.smtp_port = 25
    mock_server = MagicMock()
    mock_smtplib.SMTP.return_value = mock_server

    send_email(email_config, "<p>test</p>")

    mock_smtplib.SMTP.assert_called_once_with("smtp.example.com", 25)
    mock_smtplib.SMTP_SSL.assert_not_called()
    mock_server.ehlo.assert_called_once()
    mock_server.starttls.assert_not_called()
    mock_server.login.assert_called_once_with("test@example.com", "password")
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()
