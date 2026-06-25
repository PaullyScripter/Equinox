import discord
from discord import ui
from discord.ui import View, Modal, TextInput, Button
from asyncio import sleep
import json
import os
import re
import cogs.database as db


def load_active_tickets():
    return db.load_active_tickets()


def _lookup_ticket_owner(channel_id: int, guild_id: int) -> int | None:
    active = load_active_tickets()
    guild_key = str(guild_id)
    if guild_key in active:
        for uid_str, channel_ids in active[guild_key].items():
            if channel_id in channel_ids:
                return int(uid_str)
    return None


def save_active_tickets(data):
    db.save_active_tickets(data)


def load_archived_tickets():
    return db.load_archived_tickets()


def save_archived_tickets(data):
    db.save_archived_tickets(data)


def get_ticket_config(guild_id: int):
    return db.get_ticket_config(guild_id)


def save_ticket_config(guild_id: int, data):
    db.save_ticket_config(guild_id, data)


def find_message_entry(guild_id: int, message_id: int):
    config = get_ticket_config(guild_id)
    for msg in config.get("message", []):
        if msg.get("messageid") == message_id:
            return msg, config
    return None, config


def load_ticket_history():
    return db.load_ticket_history()


def save_ticket_history(data):
    db.save_ticket_history(data)


def append_ticket_history(channel_id: int, action: str, user_id: int, note: str = ""):
    db.append_ticket_history(channel_id, action, user_id, note)


def load_ticket_participants():
    return db.load_ticket_participants()


def save_ticket_participants(data):
    db.save_ticket_participants(data)


def add_ticket_participant(channel_id: int, user_id: int):
    db.add_ticket_participant(channel_id, user_id)

TRANSCRIPTS_DIR = "ticket-json/transcripts"

def _escape_html(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

SYSTEM_ICONS = {
    "recipient_add": "join-icon",
    "recipient_remove": "leave-icon",
    "call": "call-icon",
    "channel_name_change": "pencil-icon",
    "channel_icon_change": "pencil-icon",
    "pinned_message": "pin-icon",
    "guild_member_join": "join-icon",
    "thread_created": "thread-icon",
}

def _get_system_icon(msg_type):
    name = msg_type.name.lower() if hasattr(msg_type, 'name') else ""
    if "recipient" in name and "add" in name:
        return "join-icon"
    if "recipient" in name and "remove" in name:
        return "leave-icon"
    if "call" in name:
        return "call-icon"
    if "channel_name_change" in name:
        return "pencil-icon"
    if "channel_icon_change" in name:
        return "pencil-icon"
    if "pinned" in name:
        return "pin-icon"
    if "guild_member_join" in name:
        return "join-icon"
    if "thread" in name:
        return "thread-icon"
    return "pencil-icon"

def _format_timestamp(dt, fmt="g"):
    return dt.strftime("%m/%d/%Y %I:%M %p").lstrip("0") if fmt == "g" else dt.strftime("%I:%M %p").lstrip("0")

def _build_attachment_html(att):
    is_spoiler = att.is_spoiler()
    spoiler_class = ' chatlog__attachment--hidden' if is_spoiler else ''
    spoiler_caption = '<div class="chatlog__attachment-spoiler-caption">SPOILER</div>' if is_spoiler else ''
    onclick = ' onclick="showSpoiler(event, this)"' if is_spoiler else ''
    url = _escape_html(att.url)
    filename = _escape_html(att.filename)

    if att.content_type and att.content_type.startswith("image/"):
        return f'''<div class="chatlog__attachment{spoiler_class}"{onclick}>
            {spoiler_caption}
            <a href="{url}">
                <img class="chatlog__attachment-media" src="{url}" alt="{filename}" title="Image: {filename}" loading="lazy">
            </a>
        </div>'''
    elif att.content_type and att.content_type.startswith("video/"):
        return f'''<div class="chatlog__attachment{spoiler_class}"{onclick}>
            {spoiler_caption}
            <video class="chatlog__attachment-media" controls>
                <source src="{url}" alt="{filename}">
            </video>
        </div>'''
    elif att.content_type and att.content_type.startswith("audio/"):
        return f'''<div class="chatlog__attachment{spoiler_class}"{onclick}>
            {spoiler_caption}
            <audio class="chatlog__attachment-media" controls>
                <source src="{url}" alt="{filename}">
            </audio>
        </div>'''
    else:
        return f'''<div class="chatlog__attachment{spoiler_class}"{onclick}>
            {spoiler_caption}
            <div class="chatlog__attachment-generic">
                <svg class="chatlog__attachment-generic-icon"><use href="#attachment-icon"/></svg>
                <div class="chatlog__attachment-generic-name"><a href="{url}">{filename}</a></div>
                <div class="chatlog__attachment-generic-size">{_escape_html(str(att.size) + " bytes")}</div>
            </div>
        </div>'''

def _build_embed_html(emb):
    if emb.type == "image" and emb.url:
        url = _escape_html(emb.url)
        return f'''<div class="chatlog__embed">
            <a href="{url}"><img class="chatlog__embed-generic-image" src="{url}" alt="Embedded image" loading="lazy"></a>
        </div>'''

    if emb.type in ("rich", "article", "link"):
        color = emb.color
        if color:
            pill_style = f'style="background-color: rgb({color.r}, {color.g}, {color.b})"'
            pill_class = ""
        else:
            pill_style = ""
            pill_class = ' chatlog__embed-color-pill--default'

        author_html = ""
        if emb.author:
            a_icon = f'<img class="chatlog__embed-author-icon" src="{_escape_html(emb.author.icon_url)}" alt="" loading="lazy">' if emb.author.icon_url else ""
            a_name = f'<div class="chatlog__embed-author">{_escape_html(emb.author.name)}</div>' if emb.author.name else ""
            if emb.author.url and a_name:
                a_name = f'<a class="chatlog__embed-author-link" href="{_escape_html(emb.author.url)}">{a_name}</a>'
            if a_icon or a_name:
                author_html = f'<div class="chatlog__embed-author-container">{a_icon}{a_name}</div>'

        title_html = ""
        if emb.title:
            if emb.url:
                title_html = f'<div class="chatlog__embed-title"><a class="chatlog__embed-title-link" href="{_escape_html(emb.url)}"><div class="chatlog__markdown chatlog__markdown-preserve">{_escape_html(emb.title)}</div></a></div>'
            else:
                title_html = f'<div class="chatlog__embed-title"><div class="chatlog__markdown chatlog__markdown-preserve">{_escape_html(emb.title)}</div></div>'

        desc_html = ""
        if emb.description:
            desc_html = f'<div class="chatlog__embed-description"><div class="chatlog__markdown chatlog__markdown-preserve">{_escape_html(emb.description).replace(chr(10), "<br>")}</div></div>'

        fields_html = ""
        if emb.fields:
            fhtml = ""
            for field in emb.fields:
                inline = ' chatlog__embed-field--inline' if field.inline else ''
                fhtml += f'<div class="chatlog__embed-field{inline}">'
                if field.name:
                    fhtml += f'<div class="chatlog__embed-field-name"><div class="chatlog__markdown chatlog__markdown-preserve">{_escape_html(field.name)}</div></div>'
                if field.value:
                    fhtml += f'<div class="chatlog__embed-field-value"><div class="chatlog__markdown chatlog__markdown-preserve">{_escape_html(field.value).replace(chr(10), "<br>")}</div></div>'
                fhtml += '</div>'
            fields_html = f'<div class="chatlog__embed-fields">{fhtml}</div>'

        thumb_html = ""
        if emb.thumbnail:
            thumb_url = _escape_html(emb.thumbnail.url)
            thumb_html = f'<div class="chatlog__embed-thumbnail-container"><a class="chatlog__embed-thumbnail-link" href="{thumb_url}"><img class="chatlog__embed-thumbnail" src="{thumb_url}" alt="Thumbnail" loading="lazy"></a></div>'

        images_html = ""
        if emb.image:
            img_url = _escape_html(emb.image.url)
            images_html = f'<div class="chatlog__embed-images chatlog__embed-images--single"><div class="chatlog__embed-image-container"><a class="chatlog__embed-image-link" href="{img_url}"><img class="chatlog__embed-image" src="{img_url}" alt="Image" loading="lazy"></a></div></div>'

        footer_html = ""
        if emb.footer or emb.timestamp:
            f_icon = f'<img class="chatlog__embed-footer-icon" src="{_escape_html(emb.footer.icon_url)}" alt="" loading="lazy">' if emb.footer and emb.footer.icon_url else ""
            f_text = _escape_html(emb.footer.text) if emb.footer and emb.footer.text else ""
            ts = emb.timestamp.strftime("%m/%d/%Y %I:%M %p").lstrip("0") if emb.timestamp else ""
            sep = " • " if f_text and ts else ""
            footer_html = f'<div class="chatlog__embed-footer">{f_icon}<span class="chatlog__embed-footer-text">{f_text}{sep}{ts}</span></div>'

        return f'''<div class="chatlog__embed">
            <div class="chatlog__embed-color-pill{pill_class}" {pill_style}></div>
            <div class="chatlog__embed-content-container">
                <div class="chatlog__embed-content">
                    <div class="chatlog__embed-text">
                        {author_html}
                        {title_html}
                        {desc_html}
                        {fields_html}
                    </div>
                    {thumb_html}
                </div>
                {images_html}
                {footer_html}
            </div>
        </div>'''

    return ""

CUSTOM_EMOJI_RE = re.compile(r'<a?:(\w+):(\d+)>')
URL_RE = re.compile(r'https?://[^\s<>"]+(?:\?[^\s<>"]*)?', re.IGNORECASE)

def _format_content(content):
    if not content:
        return ""
    def replace_url(m):
        url = m.group(0)
        escaped = _escape_html(url)
        if any(url.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            return f'<a href="{escaped}"><img class="chatlog__embed-generic-image" src="{escaped}" alt="Image" loading="lazy"></a>'
        return f'<a href="{escaped}">{escaped}</a>'
    content = URL_RE.sub(replace_url, content)
    def replace_emoji(m):
        animated = m.group(0).startswith('<a')
        name = m.group(1)
        eid = m.group(2)
        ext = 'gif' if animated else 'png'
        url = f'https://cdn.discordapp.com/emojis/{eid}.{ext}'
        return f'<img class="chatlog__emoji" alt=":{name}:" src="{url}" title="{name}" loading="lazy">'
    content = CUSTOM_EMOJI_RE.sub(replace_emoji, content)
    return content.replace("\n", "<br>")

def _build_reactions_html(msg):
    if not msg.reactions:
        return ""
    html = '<div class="chatlog__reactions">'
    for reaction in msg.reactions:
        emoji_url = None
        emoji_code = str(reaction.emoji)
        if reaction.is_custom_emoji():
            try:
                emoji_url = reaction.emoji.url
            except Exception:
                emoji_url = None
        if emoji_url:
            html += f'<div class="chatlog__reaction" title="{_escape_html(emoji_code)}"><img class="chatlog__emoji chatlog__emoji--small" alt="{_escape_html(emoji_code)}" src="{_escape_html(emoji_url)}" loading="lazy"><span class="chatlog__reaction-count">{reaction.count}</span></div>'
        else:
            html += f'<div class="chatlog__reaction" title="{_escape_html(emoji_code)}"><span class="chatlog__reaction-emoji">{_escape_html(emoji_code)}</span><span class="chatlog__reaction-count">{reaction.count}</span></div>'
    html += '</div>'
    return html

def _build_stickers_html(msg):
    if not msg.stickers:
        return ""
    html = ""
    for sticker in msg.stickers:
        try:
            if sticker.format == discord.StickerFormatType.lottie:
                html += f'<div class="chatlog__sticker" title="{_escape_html(sticker.name)}"><div class="chatlog__sticker--media" data-source="{_escape_html(sticker.url)}"></div></div>'
            else:
                html += f'<div class="chatlog__sticker" title="{_escape_html(sticker.name)}"><img class="chatlog__sticker--media" src="{_escape_html(sticker.url)}" alt="{_escape_html(sticker.name)}"></div>'
        except Exception:
            html += f'<div class="chatlog__sticker" title="{_escape_html(sticker.name)}"><img class="chatlog__sticker--media" src="{_escape_html(sticker.url)}" alt="{_escape_html(sticker.name)}"></div>'
    return html

def _is_system_type(msg_type):
    system_names = {
        "recipient_add", "recipient_remove", "call",
        "channel_name_change", "channel_icon_change", "pins_add",
        "new_member", "guild_member_join", "premium_guild_subscription",
        "premium_guild_tier_1", "premium_guild_tier_2", "premium_guild_tier_3",
        "channel_follow_add", "thread_created", "thread_starter_message",
        "guild_stream", "boost", "member_join",
    }
    name = msg_type.name if hasattr(msg_type, 'name') else ""
    return name in system_names

def _build_message_html(msg, is_first, guild, message_lookup):
    is_system = _is_system_type(msg.type)
    if is_system:
        icon = _get_system_icon(msg.type)
        system_content = _escape_html(msg.system_content or "Unknown system event")
        return f'''<div class="chatlog__message-container" data-message-id="{msg.id}">
            <div class="chatlog__message">
                <div class="chatlog__message-aside">
                    <svg class="chatlog__system-notification-icon"><use href="#{icon}"/></svg>
                </div>
                <div class="chatlog__message-primary">
                    <span class="chatlog__system-notification-content">{system_content}</span>
                    <span class="chatlog__system-notification-timestamp"><a href="#chatlog__message-container-{msg.id}">{_format_timestamp(msg.created_at)}</a></span>
                </div>
            </div>
        </div>'''

    avatar_url = msg.author.display_avatar.url
    name = _escape_html(msg.author.display_name)
    short_ts = _format_timestamp(msg.created_at, "t")
    full_ts = _format_timestamp(msg.created_at, "f")
    content = _format_content(msg.content or "")

    is_bot = msg.author.bot
    bot_tag = '<span class="chatlog__author-tag">BOT</span>' if is_bot else ""

    has_edit = msg.edited_at is not None
    edit_html = f'<span class="chatlog__edited-timestamp" title="{_format_timestamp(msg.edited_at, "f") if msg.edited_at else ""}">(edited)</span>' if has_edit else ""

    reply_html = ""
    has_reply = False
    if msg.reference and msg.reference.message_id:
        ref_msg = message_lookup.get(msg.reference.message_id)
        if ref_msg:
            has_reply = True
            ref_name = _escape_html(ref_msg.author.display_name) if ref_msg.author else "Unknown"
            ref_avatar = ref_msg.author.display_avatar.url if ref_msg.author else ""
            ref_content = _escape_html((ref_msg.content or "Click to see attachment")[:80])
            reply_html = f'''<div class="chatlog__reply">
                <img class="chatlog__reply-avatar" src="{ref_avatar}" alt="" loading="lazy">
                <div class="chatlog__reply-author">{ref_name}</div>
                <div class="chatlog__reply-content">
                    <span class="chatlog__reply-link" onclick="scrollToMessage(event, '{ref_msg.id}')">{ref_content}</span>
                </div>
            </div>'''

    attachments_html = ""
    for att in msg.attachments:
        attachments_html += _build_attachment_html(att)

    embeds_html = ""
    for emb in msg.embeds:
        embeds_html += _build_embed_html(emb)

    reactions_html = _build_reactions_html(msg)
    stickers_html = _build_stickers_html(msg)

    if is_first:
        reply_symbol = '<div class="chatlog__reply-symbol"></div>' if has_reply else ''
        aside = f'''{reply_symbol}
            <img class="chatlog__avatar" src="{avatar_url}" alt="Avatar" loading="lazy">'''
        header = f'''<div class="chatlog__header">
            <span class="chatlog__author">{name}{bot_tag}</span>
            <span class="chatlog__timestamp"><a href="#chatlog__message-container-{msg.id}">{short_ts}</a></span>
        </div>'''
    else:
        aside = f'<div class="chatlog__short-timestamp" title="{full_ts}">{short_ts}</div>'
        header = ""

    return f'''<div id="chatlog__message-container-{msg.id}" class="chatlog__message-container" data-message-id="{msg.id}">
        <div class="chatlog__message">
            <div class="chatlog__message-aside">
                {aside}
            </div>
            <div class="chatlog__message-primary">
                {reply_html}
                {header}
                <div class="chatlog__content chatlog__markdown">
                    <span class="chatlog__markdown-preserve">{content}</span>
                    {edit_html}
                </div>
                {attachments_html}
                {embeds_html}
                {stickers_html}
                {reactions_html}
            </div>
        </div>
    </div>'''

def _build_message_group_html(messages, guild, message_lookup):
    if not messages:
        return ""
    html = '<div class="chatlog__message-group">'
    for i, msg in enumerate(messages):
        html += _build_message_html(msg, i == 0, guild, message_lookup)
    html += '</div>'
    return html

def _build_transcript_html(channel_name, creator_name, reason, closed_by_name, closed_at, messages, guild, stats=None):
    message_lookup = {msg.id: msg for msg in messages}

    groups = []
    current_group = []
    for msg in messages:
        is_system = _is_system_type(msg.type)
        if not current_group:
            current_group.append(msg)
        elif is_system:
            groups.append(current_group)
            current_group = [msg]
        elif _is_system_type(current_group[-1].type):
            groups.append(current_group)
            current_group = [msg]
        elif msg.author.id == current_group[-1].author.id and (msg.created_at - current_group[-1].created_at).total_seconds() < 300:
            current_group.append(msg)
        else:
            groups.append(current_group)
            current_group = [msg]
    if current_group:
        groups.append(current_group)

    msg_html = ""
    for group in groups:
        msg_html += _build_message_group_html(group, guild, message_lookup)

    guild_name = _escape_html(guild.name if guild else "Unknown")
    total_msgs = len(messages)

    stats_html = ""
    if stats:
        count_by_user = stats.get("count_by_user", {})
        sorted_users = sorted(count_by_user.items(), key=lambda x: -x[1])

        parts_rows = ""
        if stats.get("opened_by_name"):
            parts_rows += f'<tr><td class="stats-label">Opened by</td><td>{_escape_html(stats["opened_by_name"])} (ID: {stats["opened_by_id"]})</td></tr>'
        if stats.get("closed_by_name"):
            parts_rows += f'<tr><td class="stats-label">Closed by</td><td>{_escape_html(stats["closed_by_name"])} (ID: {stats["closed_by_id"]})</td></tr>'
        if stats.get("claimed_by_name"):
            parts_rows += f'<tr><td class="stats-label">Claimed by</td><td>{_escape_html(stats["claimed_by_name"])} (ID: {stats["claimed_by_id"]})</td></tr>'
        if stats.get("reason"):
            parts_rows += f'<tr><td class="stats-label">Close reason</td><td>{_escape_html(stats["reason"])}</td></tr>'
        if stats.get("first_msg"):
            parts_rows += f'<tr><td class="stats-label">First message</td><td>{_escape_html(stats["first_msg"])}</td></tr>'
        if stats.get("last_msg"):
            parts_rows += f'<tr><td class="stats-label">Last message</td><td>{_escape_html(stats["last_msg"])}</td></tr>'
        parts_rows += f'<tr><td class="stats-label">Total messages</td><td>{total_msgs}</td></tr>'

        participants_rows = ""
        for uid_str, count in sorted_users:
            uname = "Unknown"
            if uid_str in stats.get("user_names", {}):
                uname = stats["user_names"][uid_str]
            participants_rows += f'<tr><td>{_escape_html(uname)}</td><td>{uid_str}</td><td>{count}</td></tr>'

        history_rows = ""
        for event in stats.get("history", []):
            action = event.get("action", "")
            eid = event.get("user_id", 0)
            at = event.get("at", "")
            note = event.get("note", "")
            ename = stats.get("user_names", {}).get(str(eid), str(eid))
            label = action.capitalize()
            if note:
                label += f" ({_escape_html(note)})"
            history_rows += f'<tr><td>{label}</td><td>{_escape_html(ename)} (ID: {eid})</td><td>{_escape_html(at)}</td></tr>'

        stats_html = f'''<div class="stats">
            <h2>Statistics</h2>
            <table class="stats-table">
                {parts_rows}
            </table>
            <h3>Participants</h3>
            <table class="stats-table">
                <tr><th>User</th><th>ID</th><th>Messages</th></tr>
                {participants_rows}
            </table>
            <h3>Event History</h3>
            <table class="stats-table">
                <tr><th>Action</th><th>By</th><th>Time</th></tr>
                {history_rows}
            </table>
        </div>'''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<title>Transcript - {_escape_html(channel_name)}</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body {{ margin: 0; padding: 0; background-color: #313338; color: #dbdee1; font-family: 'Inter', 'gg sans', 'Helvetica Neue', Arial, sans-serif; font-size: 17px; font-weight: 400; }}
a {{ color: #00a8fc; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
img {{ object-fit: contain; image-rendering: high-quality; }}
.header {{ display: grid; grid-template-columns: auto 1fr; padding: 1rem; background: #2b2d31; border-bottom: 1px solid rgba(255,255,255,0.1); position: sticky; top: 0; z-index: 10; }}
.header-icon img {{ max-width: 88px; max-height: 88px; border-radius: 50%; }}
.header-entries {{ margin-left: 1rem; }}
.header-entry {{ margin-bottom: 0.15rem; color: #f2f3f5; font-size: 1.4rem; }}
.header-entry--small {{ font-size: 1rem; color: #dbdee1; }}
.chatlog {{ padding: 1rem 0; width: 100%; border-top: 1px solid rgba(255,255,255,0.1); border-bottom: 1px solid rgba(255,255,255,0.1); }}
.chatlog__message-group {{ margin-bottom: 1rem; }}
.chatlog__message-container {{ background-color: transparent; transition: background-color 1s ease; }}
.chatlog__message-container--highlighted {{ background-color: rgba(114, 137, 218, 0.2); }}
.chatlog__message {{ display: grid; grid-template-columns: auto 1fr; padding: 0.15rem 0; direction: ltr; unicode-bidi: bidi-override; }}
.chatlog__message:hover {{ background-color: #32353b; }}
.chatlog__message:hover .chatlog__short-timestamp {{ display: block; }}
.chatlog__message-aside {{ grid-column: 1; width: 72px; padding: 0.15rem 0.15rem 0 0.15rem; text-align: center; }}
.chatlog__reply-symbol {{ height: 10px; margin: 6px 4px 4px 36px; border-left: 2px solid #4f545c; border-top: 2px solid #4f545c; border-radius: 8px 0 0 0; }}
.chatlog__avatar {{ width: 40px; height: 40px; border-radius: 50%; }}
.chatlog__short-timestamp {{ display: none; color: #a3a6aa; font-size: 0.75rem; font-weight: 500; }}
.chatlog__message-primary {{ grid-column: 2; min-width: 0; }}
.chatlog__reply {{ display: flex; margin-bottom: 0.15rem; align-items: center; color: #b5b6b8; font-size: 0.875rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }}
.chatlog__reply:hover {{ color: #dbdee1; }}
.chatlog__reply-avatar {{ width: 16px; height: 16px; margin-right: 0.25rem; border-radius: 50%; }}
.chatlog__reply-author {{ margin-right: 0.3rem; font-weight: 600; color: #b5b6b8; }}
.chatlog__reply-content {{ overflow: hidden; text-overflow: ellipsis; }}
.chatlog__reply-link:hover {{ color: #dbdee1; }}
.chatlog__system-notification-icon {{ width: 18px; height: 18px; }}
.chatlog__system-notification-content {{ color: #96989d; font-size: 0.875rem; }}
.chatlog__system-notification-timestamp {{ margin-left: 0.3rem; color: #a3a6aa; font-size: 0.75rem; font-weight: 500; }}
.chatlog__system-notification-timestamp a {{ color: inherit; }}
.chatlog__header {{ margin-bottom: 0.1rem; }}
.chatlog__author {{ font-weight: 500; color: #f2f3f5; font-size: 1rem; cursor: pointer; }}
.chatlog__author:hover {{ text-decoration: underline; }}
.chatlog__author-tag {{ position: relative; top: -0.1rem; margin-left: 0.3rem; padding: 0.05rem 0.3rem; border-radius: 3px; background-color: #5865F2; color: #fff; font-size: 0.625rem; font-weight: 500; line-height: 1.3; text-transform: uppercase; }}
.chatlog__timestamp {{ margin-left: 0.3rem; color: #a3a6aa; font-size: 0.75rem; font-weight: 500; }}
.chatlog__timestamp a {{ color: inherit; }}
.chatlog__content {{ padding-right: 1rem; font-size: 0.95rem; word-wrap: break-word; }}
.chatlog__edited-timestamp {{ margin-left: 0.15rem; color: #a3a6aa; font-size: 0.75rem; font-weight: 500; }}
.chatlog__attachment {{ position: relative; width: fit-content; margin-top: 0.3rem; border-radius: 3px; overflow: hidden; }}
.chatlog__attachment--hidden {{ cursor: pointer; box-shadow: 0 0 1px 1px rgba(0,0,0,0.1); }}
.chatlog__attachment--hidden * {{ pointer-events: none; }}
.chatlog__attachment-spoiler-caption {{ display: none; position: absolute; left: 50%; top: 50%; z-index: 999; padding: 0.4rem 0.8rem; border-radius: 20px; transform: translate(-50%,-50%); background-color: rgba(0,0,0,0.9); color: #dcddde; font-size: 0.9rem; font-weight: 600; letter-spacing: 0.05rem; }}
.chatlog__attachment--hidden .chatlog__attachment-spoiler-caption {{ display: block; }}
.chatlog__attachment--hidden .chatlog__attachment-media {{ filter: blur(44px); }}
.chatlog__attachment--hidden:hover .chatlog__attachment-spoiler-caption {{ color: #fff; }}
.chatlog__attachment-media {{ max-width: 45vw; max-height: 500px; vertical-align: top; border-radius: 3px; }}
.chatlog__attachment-generic {{ max-width: 520px; width: 100%; height: 40px; padding: 10px; border: 1px solid #292b2f; border-radius: 3px; background-color: #2f3136; overflow: hidden; }}
.chatlog__attachment-generic-icon {{ float: left; width: 30px; height: 100%; margin-right: 10px; }}
.chatlog__attachment-generic-name {{ overflow: hidden; white-space: nowrap; text-overflow: ellipsis; color: #dbdee1; }}
.chatlog__attachment-generic-size {{ color: #72767d; font-size: 0.75rem; }}
.chatlog__embed {{ display: flex; margin-top: 0.3rem; max-width: 520px; }}
.chatlog__embed-color-pill {{ flex-shrink: 0; width: 0.25rem; border-top-left-radius: 3px; border-bottom-left-radius: 3px; }}
.chatlog__embed-color-pill--default {{ background-color: #202225; }}
.chatlog__embed-content-container {{ display: flex; flex-direction: column; padding: 0.5rem 0.6rem; border: 1px solid rgba(46,48,54,0.6); border-top-right-radius: 3px; border-bottom-right-radius: 3px; background-color: rgba(46,48,54,0.3); }}
.chatlog__embed-content {{ display: flex; width: 100%; }}
.chatlog__embed-text {{ flex: 1; }}
.chatlog__embed-author-container {{ display: flex; margin-bottom: 0.5rem; align-items: center; }}
.chatlog__embed-author-icon {{ width: 20px; height: 20px; margin-right: 0.5rem; border-radius: 50%; }}
.chatlog__embed-author {{ color: #f2f3f5; font-size: 0.875rem; font-weight: 600; }}
.chatlog__embed-author-link {{ color: #f2f3f5; }}
.chatlog__embed-title {{ margin-bottom: 0.5rem; }}
.chatlog__embed-title a {{ color: #f2f3f5; font-size: 0.875rem; font-weight: 600; }}
.chatlog__embed-description {{ color: #dbdee1; font-weight: 500; font-size: 0.85rem; }}
.chatlog__embed-fields {{ display: flex; flex-wrap: wrap; gap: 0 0.5rem; }}
.chatlog__embed-field {{ flex: 0; min-width: 100%; max-width: 506px; padding-top: 0.6rem; font-size: 0.875rem; }}
.chatlog__embed-field--inline {{ flex: 1; flex-basis: auto; min-width: 50px; }}
.chatlog__embed-field-name {{ margin-bottom: 0.2rem; color: #f2f3f5; font-weight: 600; }}
.chatlog__embed-field-value {{ color: #dbdee1; font-weight: 500; }}
.chatlog__embed-thumbnail {{ max-width: 80px; max-height: 80px; border-radius: 3px; }}
.chatlog__embed-thumbnail-container {{ flex: 0; margin-left: 1.2rem; }}
.chatlog__embed-images {{ display: grid; margin-top: 0.6rem; grid-template-columns: repeat(2,1fr); gap: 0.25rem; }}
.chatlog__embed-images--single {{ display: block; }}
.chatlog__embed-image {{ object-fit: cover; max-width: 500px; max-height: 400px; width: 100%; border-radius: 3px; }}
.chatlog__embed-image-container {{ width: 100%; }}
.chatlog__embed-image-link {{ display: block; }}
.chatlog__embed-footer {{ margin-top: 0.6rem; color: #dbdee1; }}
.chatlog__embed-footer-icon {{ width: 20px; height: 20px; margin-right: 0.2rem; border-radius: 50%; vertical-align: middle; }}
.chatlog__embed-footer-text {{ vertical-align: middle; font-size: 0.75rem; font-weight: 500; }}
.chatlog__embed-generic-image {{ object-fit: contain; object-position: left; max-width: 45vw; max-height: 500px; vertical-align: top; border-radius: 3px; }}
.chatlog__sticker {{ width: 180px; height: 180px; }}
.chatlog__sticker--media {{ max-width: 100%; max-height: 100%; }}
.chatlog__reactions {{ display: flex; flex-wrap: wrap; gap: 0.1rem; margin-top: 0.2rem; }}
.chatlog__reaction {{ display: flex; margin: 0.35rem 0.1rem 0.1rem 0; padding: 0.125rem 0.375rem; border: 1px solid transparent; border-radius: 8px; background-color: #2f3136; align-items: center; cursor: pointer; font-size: 0.875rem; }}
.chatlog__reaction:hover {{ border: 1px solid hsla(0,0%,100%,.2); }}
.chatlog__reaction-emoji {{ font-size: 1rem; }}
.chatlog__reaction-count {{ min-width: 9px; margin-left: 0.35rem; color: #b9bbbe; font-size: 0.875rem; }}
.chatlog__reaction:hover .chatlog__reaction-count {{ color: #dcddde; }}
.chatlog__markdown {{ max-width: 100%; line-height: 1.3; overflow-wrap: break-word; }}
.chatlog__markdown-preserve {{ white-space: pre-wrap; }}
.chatlog__markdown-spoiler {{ background-color: rgba(255,255,255,0.1); padding: 0 2px; border-radius: 3px; }}
.chatlog__markdown-spoiler--hidden {{ cursor: pointer; background-color: #202225; color: transparent; }}
.chatlog__markdown-spoiler--hidden:hover {{ background-color: rgba(32,34,37,0.8); }}
.chatlog__markdown-quote {{ display: flex; margin: 0.05rem 0; }}
.chatlog__markdown-quote-border {{ margin-right: 0.5rem; border: 2px solid #4f545c; border-radius: 3px; }}
.chatlog__markdown-pre {{ background-color: #2f3136; font-family: 'Consolas','Courier New',Courier,monospace; font-size: 0.85rem; }}
.chatlog__markdown-pre--multiline {{ display: block; margin-top: 0.25rem; padding: 0.5rem; border: 2px solid #282b30; border-radius: 5px; color: #b9bbbe; }}
.chatlog__markdown-pre--inline {{ display: inline-block; padding: 2px; border-radius: 3px; }}
.chatlog__markdown-mention {{ border-radius: 3px; padding: 0 2px; background-color: rgba(88,101,242,.3); color: #dee0fc; font-weight: 500; }}
.chatlog__emoji {{ width: 1.325rem; height: 1.325rem; margin: 0 0.06rem; vertical-align: -0.4rem; }}
.chatlog__emoji--small {{ width: 1rem; height: 1rem; }}
.postamble {{ padding: 1.25rem; text-align: center; color: #5c5f66; font-size: 0.875rem; }}
.postamble__entry {{ margin-bottom: 0.25rem; }}
.stats {{ padding: 1.25rem 2rem; border-top: 1px solid rgba(255,255,255,0.1); }}
.stats h2 {{ color: #f2f3f5; font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; }}
.stats h3 {{ color: #f2f3f5; font-size: 1rem; font-weight: 600; margin: 1.5rem 0 0.75rem; }}
.stats-table {{ width: 100%; border-collapse: collapse; margin-bottom: 0.5rem; }}
.stats-table td, .stats-table th {{ padding: 0.4rem 0.8rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }}
.stats-table th {{ color: #949ba4; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05rem; }}
.stats-table td {{ color: #dbdee1; font-size: 0.875rem; }}
.stats-table tr:hover td {{ background-color: rgba(255,255,255,0.02); }}
.stats-label {{ color: #949ba4; font-weight: 500; width: 180px; }}
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/solarized-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js"></script>
<script>document.addEventListener('DOMContentLoaded',()=>{{document.querySelectorAll('.chatlog__markdown-pre--multiline').forEach(e=>hljs.highlightBlock(e));}});</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.8.1/lottie.min.js"></script>
<script>document.addEventListener('DOMContentLoaded',()=>{{document.querySelectorAll('.chatlog__sticker--media[data-source]').forEach(e=>{{const anim=lottie.loadAnimation({{container:e,renderer:'svg',loop:true,autoplay:true,path:e.getAttribute('data-source')}});anim.addEventListener('data_failed',()=>e.innerHTML='<strong>[Sticker cannot be rendered]</strong>');}});}});</script>
<script>function scrollToMessage(event,id){{const element=document.getElementById('chatlog__message-container-'+id);if(!element)return;event.preventDefault();element.classList.add('chatlog__message-container--highlighted');window.scrollTo({{top:element.getBoundingClientRect().top-document.body.getBoundingClientRect().top-(window.innerHeight/2),behavior:'smooth'}});window.setTimeout(()=>element.classList.remove('chatlog__message-container--highlighted'),2000);}}
function showSpoiler(event,element){{if(!element)return;if(element.classList.contains('chatlog__attachment--hidden')){{event.preventDefault();element.classList.remove('chatlog__attachment--hidden');}}
if(element.classList.contains('chatlog__markdown-spoiler--hidden')){{event.preventDefault();element.classList.remove('chatlog__markdown-spoiler--hidden');}}}}</script>
<svg style="display:none" xmlns="http://www.w3.org/2000/svg">
<defs>
<symbol id="attachment-icon" viewBox="0 0 720 960"><path fill="#f4f5fb" d="M50,935a25,25,0,0,1-25-25V50A25,25,0,0,1,50,25H519.6L695,201.32V910a25,25,0,0,1-25,25Z"/><path fill="#7789c4" d="M509.21,50,670,211.63V910H50V50H509.21M530,0H50A50,50,0,0,0,0,50V910a50,50,0,0,0,50,50H670a50,50,0,0,0,50-50h0V191Z"/><path fill="#f4f5fb" d="M530,215a25,25,0,0,1-25-25V50a25,25,0,0,1,16.23-23.41L693.41,198.77A25,25,0,0,1,670,215Z"/><path fill="#7789c4" d="M530,70.71,649.29,190H530V70.71M530,0a50,50,0,0,0-50,50V190a50,50,0,0,0,50,50H670a50,50,0,0,0,50-50Z"/></symbol>
<symbol id="join-icon" viewBox="0 0 18 18"><path fill="#3ba55c" d="m0 8h14.2l-3.6-3.6 1.4-1.4 6 6-6 6-1.4-1.4 3.6-3.6h-14.2"/></symbol>
<symbol id="leave-icon" viewBox="0 0 18 18"><path fill="#ed4245" d="m3.8 8 3.6-3.6-1.4-1.4-6 6 6 6 1.4-1.4-3.6-3.6h14.2v-2"/></symbol>
<symbol id="call-icon" viewBox="0 0 18 18"><path fill="#3ba55c" fill-rule="evenodd" d="M17.7163041 15.36645368c-.0190957.02699568-1.9039523 2.6680735-2.9957762 2.63320406-3.0676659-.09785935-6.6733809-3.07188394-9.15694343-5.548738C3.08002193 9.9740657.09772497 6.3791404 0 3.3061316v-.024746C0 2.2060575 2.61386252.3152347 2.64082114.2972376c.7110335-.4971705 1.4917101-.3149497 1.80959713.1372281.19320342.2744561 2.19712724 3.2811005 2.42290565 3.6489167.09884826.1608492.14714912.3554431.14714912.5702838 0 .2744561-.07975258.5770327-.23701117.8751101-.1527655.2902036-.65262318 1.1664385-.89862055 1.594995.2673396.3768148.94804468 1.26429792 2.351016 2.66357424 1.39173858 1.39027775 2.28923588 2.07641807 2.67002628 2.34187563.4302146-.2452108 1.3086162-.74238132 1.5972981-.89423205.5447887-.28682915 1.0907006-.31944893 1.4568885-.08661115.3459689.2182151 3.3383754 2.21027167 3.6225641 2.41611376.2695862.19234426.4144887.5399137.4144887.91672846 0 .2969525-.089862.61190215-.2808189.88523346"/></symbol>
<symbol id="pencil-icon" viewBox="0 0 18 18"><path fill="#99aab5" d="m0 14.25v3.75h3.75l11.06-11.06-3.75-3.75zm17.71-10.21c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75z"/></symbol>
<symbol id="pin-icon" viewBox="0 0 18 18"><path fill="#b9bbbe" d="m16.908 8.39684-8.29587-8.295827-1.18584 1.184157 1.18584 1.18584-4.14834 4.1475v.00167l-1.18583-1.18583-1.185 1.18583 3.55583 3.55502-4.740831 4.74 1.185001 1.185 4.74083-4.74 3.55581 3.555 1.185-1.185-1.185-1.185 4.1475-4.14836h.0009l1.185 1.185z"/></symbol>
<symbol id="thread-icon" viewBox="0 0 24 24"><path fill="#b9bbbe" d="M5.43309 21C5.35842 21 5.30189 20.9325 5.31494 20.859L5.99991 17H2.14274C2.06819 17 2.01168 16.9327 2.02453 16.8593L2.33253 15.0993C2.34258 15.0419 2.39244 15 2.45074 15H6.34991L7.40991 9H3.55274C3.47819 9 3.42168 8.93274 3.43453 8.85931L3.74253 7.09931C3.75258 7.04189 3.80244 7 3.86074 7H7.75991L8.45234 3.09903C8.46251 3.04174 8.51231 3 8.57049 3H10.3267C10.4014 3 10.4579 3.06746 10.4449 3.14097L9.75991 7H15.7599L16.4523 3.09903C16.4625 3.04174 16.5123 3 16.5705 3H18.3267C18.4014 3 18.4579 3.06746 18.4449 3.14097L17.7599 7H21.6171C21.6916 7 21.7481 7.06725 21.7353 7.14069L21.4273 8.90069C21.4172 8.95811 21.3674 9 21.3091 9H17.4099L17.0495 11.04H15.05L15.4104 9H9.41035L8.35035 15H10.5599V17H7.99991L7.30749 20.901C7.29732 20.9583 7.24752 21 7.18934 21H5.43309Z"/><path fill="#b9bbbe" d="M13.4399 12.96C12.9097 12.96 12.4799 13.3898 12.4799 13.92V20.2213C12.4799 20.7515 12.9097 21.1813 13.4399 21.1813H14.3999C14.5325 21.1813 14.6399 21.2887 14.6399 21.4213V23.4597C14.6399 23.6677 14.8865 23.7773 15.0408 23.6378L17.4858 21.4289C17.6622 21.2695 17.8916 21.1813 18.1294 21.1813H22.5599C23.0901 21.1813 23.5199 20.7515 23.5199 20.2213V13.92C23.5199 13.3898 23.0901 12.96 22.5599 12.96H13.4399Z"/></symbol>
</defs>
</svg>
</head>
<body>
<div class="header">
    <div class="header-icon"><img src="{_escape_html(guild.icon.url if guild and guild.icon else 'https://cdn.discordapp.com/embed/avatars/0.png')}" alt="Guild icon" loading="lazy"></div>
    <div class="header-entries">
        <div class="header-entry">{guild_name}</div>
        <div class="header-entry">{_escape_html(channel_name)}</div>
        <div class="header-entry header-entry--small"><strong>Closed by:</strong> {_escape_html(closed_by_name)} &middot; <strong>Reason:</strong> {_escape_html(reason)} &middot; <strong>At:</strong> {_escape_html(closed_at)}</div>
    </div>
</div>
<div class="chatlog">
{msg_html}
</div>
{stats_html}
<div class="postamble">
    <div class="postamble__entry">Exported {total_msgs} message(s)</div>
    <div class="postamble__entry">Timezone: UTC+0</div>
    <div class="postamble__entry">Transcript generated by Equinox Bot &mdash; Confidential</div>
</div>
</body>
</html>"""

async def generate_transcript(channel, reason, closed_by_name, closed_by_id):
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

    creator_id = _lookup_ticket_owner(channel.id, channel.guild.id)
    creator_name = "Unknown"
    if creator_id is None:
        uid_str = channel.name.rsplit("-", 1)[-1]
        if uid_str.isdigit():
            creator_id = int(uid_str)
    if creator_id is not None:
        member = channel.guild.get_member(creator_id)
        if member:
            creator_name = str(member)

    messages = []
    async for msg in channel.history(limit=5000, oldest_first=True):
        messages.append(msg)

    participants_ids = set()
    count_by_user = {}
    user_names = {}
    for msg in messages:
        if msg.author.bot:
            continue
        participants_ids.add(msg.author.id)
        sid = str(msg.author.id)
        count_by_user[sid] = count_by_user.get(sid, 0) + 1
        if sid not in user_names:
            user_names[sid] = str(msg.author)

    stored_participants = load_ticket_participants().get(str(channel.id), [])
    participants_ids.update(stored_participants)

    archived = load_archived_tickets()
    arch_entry = archived.get(str(channel.id), {})
    claimed_by_id = arch_entry.get("claimed_by", 0)
    claimed_by_name = ""
    if claimed_by_id:
        m = channel.guild.get_member(claimed_by_id)
        claimed_by_name = str(m) if m else str(claimed_by_id)

    history = load_ticket_history()
    channel_history = history.get(str(channel.id), [])

    first_msg = messages[0].created_at.strftime("%m/%d/%Y %I:%M %p UTC") if messages else ""
    last_msg = messages[-1].created_at.strftime("%m/%d/%Y %I:%M %p UTC") if messages else ""

    closed_at = discord.utils.utcnow().strftime("%m/%d/%Y %I:%M %p UTC")
    stats = {
        "count_by_user": count_by_user,
        "user_names": user_names,
        "opened_by_name": creator_name,
        "opened_by_id": creator_id,
        "closed_by_name": closed_by_name,
        "closed_by_id": closed_by_id,
        "claimed_by_name": claimed_by_name,
        "claimed_by_id": claimed_by_id,
        "reason": reason,
        "first_msg": first_msg,
        "last_msg": last_msg,
        "history": channel_history,
    }

    html = _build_transcript_html(
        channel.name, creator_name, reason, closed_by_name, closed_at, messages, channel.guild, stats
    )

    path = os.path.join(TRANSCRIPTS_DIR, f"{channel.id}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return path, participants_ids


class BuyPremium2(View):
  def __init__(self):
    super().__init__(timeout=None)
    button = discord.ui.Button(label='Buy Premium', style=discord.ButtonStyle.url, url='https://discord.gg/Cu8JR7Vsvx')
    self.add_item(button)


class DelTicketModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Delete a ticket system")
        self.codeid = ui.TextInput(label="Enter message ID:", style=discord.TextStyle.short)
        self.add_item(self.codeid)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        config = get_ticket_config(guild_id)
        if not config.get("message"):
            await interaction.followup.send("No ticket data found.", ephemeral=True)
            return

        try:
            message_id = int(self.codeid.value)
        except ValueError:
            await interaction.followup.send("Invalid message ID.", ephemeral=True)
            return

        ticket_to_delete = next((msg for msg in config["message"] if msg["messageid"] == message_id), None)
        if not ticket_to_delete:
            await interaction.followup.send("Failed to delete ticket system: ID not found.", ephemeral=True)
            return

        channel_id = ticket_to_delete.get("channel_id")
        msg_id = ticket_to_delete.get("messageid")

        config["message"] = [msg for msg in config["message"] if msg["messageid"] != message_id]
        save_ticket_config(guild_id, config)

        if channel_id:
            target_channel = interaction.guild.get_channel(channel_id)
            if target_channel:
                try:
                    target_message = await target_channel.fetch_message(msg_id)
                    await target_message.delete()
                except (discord.NotFound, discord.Forbidden, Exception):
                    pass

        await interaction.followup.send("Successfully deleted the ticket system.", ephemeral=True)


class DeleteTicketSystemButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=15)
    button = discord.ui.Button(label='Buy Premium', style=discord.ButtonStyle.url, url='https://discord.gg/Cu8JR7Vsvx')
    self.add_item(button)
  @discord.ui.button(label="Delete ticket system", style=discord.ButtonStyle.red, custom_id="deletetticketsystem")
  async def deletetticketsystem(self, interaction: discord.Interaction, Button: discord.Button):
    guild_id = interaction.guild.id
    config = get_ticket_config(guild_id)
    if not config.get("message"):
        await interaction.response.defer()
        return
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_modal(DelTicketModal())
    else:
        await interaction.response.defer()


class setMaxTicketModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Enter Ticket Creation Limit")
        self.amount = ui.TextInput(
            label="Enter a number (0 = Limitless, Max < 100):",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not str(self.amount.value).isdigit() or int(self.amount.value) < 0 or int(self.amount.value) >= 100:
            await interaction.followup.send(
                "Maximum ticket creation must be a number (0 or positive).\n"
                "The number must be less than or equal to `100`, use `0` for limitless tickets.\n"
                "To disable ticket creation, use the 'Toggle Ticket' button.",
                ephemeral=True
            )
            return

        ticket_limit = int(self.amount.value)

        guild_id = interaction.guild.id
        config = get_ticket_config(guild_id)
        message_entry = next((msg for msg in config.get("message", []) if msg.get("messageid") == interaction.message.id), None)

        if not message_entry:
            await interaction.followup.send("Ticket system message not found.", ephemeral=True)
            return

        message_entry["max_ticket"] = None if ticket_limit == 0 else ticket_limit
        save_ticket_config(guild_id, config)

        limit_display = "Limitless" if ticket_limit == 0 else str(ticket_limit)
        await interaction.followup.send(
            f"Successfully set ticket creation limit to **{limit_display}**.",
            ephemeral=True
        )

        try:
            msg = await interaction.channel.fetch_message(interaction.message.id)
            original_embed = msg.embeds[0]
            is_disabled = "Disabled" if message_entry.get("disabled", False) else "Enabled"
            original_embed.set_footer(text=f"Ticket status: {is_disabled} | Max Ticket Per User: {limit_display}")
            view = TicketButton()
            await msg.edit(embed=original_embed, view=view)
        except discord.NotFound:
            await interaction.followup.send("Could not update the ticket message (message not found).", ephemeral=True)


class CloseReasonModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Close Ticket")
        self.reason = ui.TextInput(
            label="Reason for closing:",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        reason = self.reason.value or "No reason provided."
        channel = interaction.channel
        guild_id = interaction.guild.id

        active = load_active_tickets()
        uid = None
        guild_key = str(guild_id)
        cid = channel.id
        if guild_key in active:
            for uid_str, channel_ids in active[guild_key].items():
                if cid in channel_ids:
                    uid = int(uid_str)
                    break
        if uid is None:
            uid_str = channel.name.rsplit("-", 1)[-1]
            if uid_str.isdigit():
                uid = int(uid_str)
        if uid is None:
            await interaction.followup.send("Could not identify ticket owner.", ephemeral=True)
            return
        closed_by_name = str(interaction.user)
        transcript_path, participants = await generate_transcript(channel, reason, closed_by_name, interaction.user.id)

        archived = load_archived_tickets()
        archived[str(channel.id)] = {
            "guild_id": guild_id,
            "user_id": uid,
            "reason": reason,
            "closed_by": interaction.user.id,
            "closed_at": discord.utils.utcnow().isoformat(),
            "claimed_by": None,
            "transcript_path": transcript_path,
            "participants": list(participants)
        }
        save_archived_tickets(archived)

        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        target = interaction.guild.get_member(uid)
        if target:
            await channel.set_permissions(target, read_messages=False, send_messages=False)

        active = load_active_tickets()
        guild_key = str(guild_id)
        user_key = str(uid)
        if guild_key in active and user_key in active[guild_key]:
            active[guild_key][user_key] = [cid for cid in active[guild_key][user_key] if cid != channel.id]
            if not active[guild_key][user_key]:
                del active[guild_key][user_key]
            save_active_tickets(active)

        append_ticket_history(channel.id, "closed", interaction.user.id, reason)

        close_embed = discord.Embed(
            title="Ticket Closed",
            description=f"**Reason:** {reason}\n**Closed by:** {interaction.user.mention}",
            color=0xff4444,
            timestamp=discord.utils.utcnow()
        )
        await channel.send(embed=close_embed, view=TicketChannelView())

        if target:
            try:
                transcript_file = discord.File(transcript_path, filename=f"transcript-{channel.name}.html")
                await target.send(
                    embed=discord.Embed(
                        title="Your ticket has been closed",
                        description=(
                            f"**Server:** {interaction.guild.name}\n"
                            f"**Reason:** {reason}\n\n"
                            "Your transcript is attached below. "
                            "You can also use the **Get Transcript** button in the closed ticket channel."
                        ),
                        color=0xff4444
                    ),
                    file=transcript_file
                )
            except (discord.Forbidden, discord.HTTPException):
                pass

        await interaction.followup.send("Ticket closed.", ephemeral=True)


class ClaimConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="Yes, claim this ticket", style=discord.ButtonStyle.green)
    async def confirm_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        archived = load_archived_tickets()
        entry = archived.get(str(interaction.channel.id))
        if entry:
            entry["claimed_by"] = interaction.user.id
            save_archived_tickets(archived)
        append_ticket_history(interaction.channel.id, "claimed", interaction.user.id)
        await interaction.followup.send(f"{interaction.user.mention} has claimed this ticket.", ephemeral=False)

        async for msg in interaction.channel.history(limit=10):
            if msg.components:
                new_view = TicketChannelView()
                for child in new_view.children:
                    if isinstance(child, discord.ui.Button) and child.custom_id == "claimticket":
                        child.disabled = True
                        child.label = f"Claimed by {interaction.user.display_name}"
                try:
                    await msg.edit(view=new_view)
                except (discord.NotFound, discord.Forbidden):
                    pass
                break

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Claim cancelled.", embed=None, view=None)


class TicketChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def _is_claim_authorized(self, interaction: discord.Interaction) -> bool:
        user = interaction.user
        if user == interaction.guild.owner:
            return True
        if user.guild_permissions.administrator:
            return True

        config = get_ticket_config(interaction.guild.id)
        ticket_role_ids = set()
        for msg in config.get("message", []):
            roles = msg.get("ticket_role")
            if roles:
                ticket_role_ids.update(roles)

        if not ticket_role_ids:
            return bool(user.guild_permissions.administrator)

        user_role_ids = {r.id for r in user.roles}
        return bool(ticket_role_ids & user_role_ids)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green, custom_id="claimticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        owner_id = _lookup_ticket_owner(channel.id, channel.guild.id)
        if owner_id == interaction.user.id:
            await interaction.response.send_message("You cannot claim your own ticket.", ephemeral=True)
            return

        if not self._is_claim_authorized(interaction):
            await interaction.response.send_message(
                "Only the specified ticket roles, administrators, or the server owner can claim tickets.",
                ephemeral=True
            )
            return

        entry = load_archived_tickets().get(str(channel.id))
        if entry and entry.get("claimed_by"):
            claimed = interaction.guild.get_member(entry["claimed_by"])
            name = claimed.mention if claimed else entry["claimed_by"]
            await interaction.response.send_message(f"This ticket is already claimed by {name}.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"{interaction.user.mention} Do you want to claim this ticket?",
            view=ClaimConfirmView(),
            ephemeral=True
        )

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id="closeticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        archived = load_archived_tickets()
        if str(channel.id) in archived:
            await interaction.response.send_message("This ticket is already closed. Use Reopen to restore it.", ephemeral=True)
            return
        await interaction.response.send_modal(CloseReasonModal())

    @discord.ui.button(label="Reopen", style=discord.ButtonStyle.green, custom_id="reopenticket")
    async def reopen_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        channel = interaction.channel
        guild_id = interaction.guild.id
        archived = load_archived_tickets()
        entry = archived.pop(str(channel.id), None)
        if not entry:
            await interaction.followup.send("This ticket is not archived.", ephemeral=True)
            return
        save_archived_tickets(archived)

        uid = entry["user_id"]
        target = interaction.guild.get_member(uid)
        if target:
            await channel.set_permissions(target, read_messages=True, send_messages=True)

        active = load_active_tickets()
        guild_key = str(guild_id)
        user_key = str(uid)
        active.setdefault(guild_key, {}).setdefault(user_key, [])
        if channel.id not in active[guild_key][user_key]:
            active[guild_key][user_key].append(channel.id)
        save_active_tickets(active)

        append_ticket_history(channel.id, "reopened", interaction.user.id)

        reopen_embed = discord.Embed(
            title="Ticket Reopened",
            description=f"Reopened by {interaction.user.mention}",
            color=0x44ff44,
            timestamp=discord.utils.utcnow()
        )
        await channel.send(embed=reopen_embed, view=TicketChannelView())
        await interaction.followup.send("Ticket reopened.", ephemeral=True)

    @discord.ui.button(label="Get Transcript", style=discord.ButtonStyle.grey, custom_id="gettranscript")
    async def get_transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        archived = load_archived_tickets()
        entry = archived.get(str(channel.id))

        if not entry:
            await interaction.response.send_message("This ticket is not closed yet.", ephemeral=True)
            return

        uid = entry.get("user_id")
        closed_by = entry.get("closed_by")
        claimed_by = entry.get("claimed_by")
        participants = entry.get("participants", [])
        user_id = interaction.user.id

        is_authorized = any([
            user_id == uid,
            user_id == closed_by,
            claimed_by and user_id == claimed_by,
            user_id in participants
        ])

        if not is_authorized:
            await interaction.response.send_message(
                "You are not authorized to view this transcript. Only people who sent messages in this ticket can access it.",
                ephemeral=True
            )
            return

        transcript_path = entry.get("transcript_path")
        if not transcript_path or not os.path.exists(transcript_path):
            await interaction.response.send_message("Transcript file not found.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            transcript_file = discord.File(transcript_path, filename=f"transcript-{channel.name}.html")
            await interaction.followup.send(file=transcript_file, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to send transcript: {e}", ephemeral=True)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.red, custom_id="deleteticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        archived = load_archived_tickets()
        if str(channel.id) not in archived:
            await interaction.response.send_message("Only closed tickets can be deleted.", ephemeral=True)
            return

        owner_id = _lookup_ticket_owner(channel.id, channel.guild.id)
        if owner_id == interaction.user.id:
            await interaction.response.send_message("You cannot delete your own ticket.", ephemeral=True)
            return

        if not self._is_claim_authorized(interaction):
            await interaction.response.send_message(
                "Only the specified ticket roles, administrators, or the server owner can delete tickets.",
                ephemeral=True
            )
            return

        confirm_embed = discord.Embed(
            title="Confirm Deletion",
            description="Are you sure you want to permanently delete this ticket channel and its transcript? This cannot be undone.",
            color=0xff4444
        )
        await interaction.response.send_message(
            embed=confirm_embed,
            view=DeleteTicketConfirmView(channel.id, interaction.guild.id),
            ephemeral=True
        )


class DeleteSystemConfirmView(discord.ui.View):
    def __init__(self, message_entry, guild_id, json_data):
        super().__init__(timeout=30)
        self.message_entry = message_entry
        self.guild_id = guild_id
        self.json_data = json_data

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.red, custom_id="confirmsysdel")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.json_data["message"].remove(self.message_entry)
        save_ticket_config(self.guild_id, self.json_data)

        try:
            msg = await interaction.channel.fetch_message(self.message_entry["messageid"])
            await msg.delete()
        except (discord.NotFound, discord.Forbidden):
            pass

        await interaction.followup.send(embed=discord.Embed(title="Successfully deleted the ticket system.", color=0xffffff))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey, custom_id="cancelsysdel")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=discord.Embed(title="Deletion cancelled.", color=0xffffff), view=None)


class DeleteTicketConfirmView(discord.ui.View):
    def __init__(self, channel_id: int, guild_id: int):
        super().__init__(timeout=30)
        self.channel_id = channel_id
        self.guild_id = guild_id

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.red, custom_id="confirmdeleteticket")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.followup.send("Channel not found.", ephemeral=True)
            return

        await interaction.followup.send("Ticket channel deleted.", ephemeral=True)

        archived = load_archived_tickets()
        archived.pop(str(self.channel_id), None)
        save_archived_tickets(archived)

        await channel.delete(reason=f"Ticket deleted by {interaction.user} ({interaction.user.id})")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey, custom_id="canceldeleteticket")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=discord.Embed(title="Deletion cancelled.", color=0xffffff), view=None)


class TicketButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(label="Make a Ticket", style=discord.ButtonStyle.grey, custom_id="ticketbutton")
  async def ticketbutton(self, interaction: discord.Interaction, Button: discord.Button):
    await interaction.response.defer()
    guild_id = interaction.guild.id
    config = get_ticket_config(guild_id)

    message_entry = next((msg for msg in config.get("message", []) if msg["messageid"] == interaction.message.id), None)
    if not message_entry:
      await interaction.followup.send("This ticket system has been deleted\nRefer to a ticket supporter or administrator", ephemeral=True)
      return

    able = True
    max_tickets = message_entry.get("max_ticket")
    if max_tickets is not None:
      active = load_active_tickets()
      guild_key = str(guild_id)
      user_key = str(interaction.user.id)
      user_tickets = active.get(guild_key, {}).get(user_key, [])
      valid_tickets = [cid for cid in user_tickets if interaction.guild.get_channel(cid) is not None]
      if valid_tickets != user_tickets:
        active.setdefault(guild_key, {})[user_key] = valid_tickets
        save_active_tickets(active)
      if len(valid_tickets) >= max_tickets:
        able = False

    if not able:
      await interaction.followup.send("You have exceeded the limit of ticket creations.\nTo create a new one, delete previous created ticket!", ephemeral=True)
      return

    await interaction.followup.send(content="Please wait while I prepare your ticket... <a:loading_symbol:1295113412564615249>...", ephemeral=True)

    category = discord.utils.get(interaction.guild.categories, id=message_entry["category"])
    channel = await interaction.guild.create_text_channel(
        f"ticket-{interaction.user.id}",
        category=category
    )

    active = load_active_tickets()
    active.setdefault(str(guild_id), {}).setdefault(str(interaction.user.id), [])
    if channel.id not in active[str(guild_id)][str(interaction.user.id)]:
      active[str(guild_id)][str(interaction.user.id)].append(channel.id)
    save_active_tickets(active)

    append_ticket_history(channel.id, "opened", interaction.user.id)

    await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    await channel.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)

    ticket_roles = message_entry.get("ticket_role")
    if ticket_roles:
      for role_id in ticket_roles:
        role = interaction.guild.get_role(int(role_id))
        if role:
          await channel.set_permissions(role, read_messages=True, send_messages=True)

    ping_msg = await channel.send(f"{interaction.user.mention}")
    await ping_msg.delete()

    if ticket_roles:
      for role_id in ticket_roles:
        role = interaction.guild.get_role(int(role_id))
        if role:
          ping = await channel.send(f"{role.mention}")
          await ping.delete()

    description = message_entry.get("ticket_message")
    if not description:
      description = f"```Here lies the start of the ticket of {interaction.user}!```"

    ticket_embed = discord.Embed(
        title=f"{interaction.user}'s Ticket - Equinox",
        description=description,
        color=0xffffff
    )
    await channel.send(embed=ticket_embed, view=TicketChannelView())

    await interaction.followup.send(
        content=f"Your ticket has been successfully created!\n Navigate to {channel.mention}!",
        ephemeral=True
    )

  @discord.ui.button(label="Set Max Ticket", style=discord.ButtonStyle.blurple, custom_id="setmaxticket")
  async def setmaxticket(self, interaction: discord.Interaction, Button: discord.Button):
      guild_id = interaction.guild.id
      message_entry, config = find_message_entry(guild_id, interaction.message.id)
      if not message_entry:
          await interaction.response.send_message("Ticket system not found.", ephemeral=True)
          return

      is_admin = interaction.user.guild_permissions.administrator
      has_required_role = False
      required_roles = message_entry.get("ticket_role", [])
      if required_roles:
          user_roles = [role.id for role in interaction.user.roles]
          has_required_role = any(role_id in user_roles for role_id in required_roles)

      if not is_admin and not has_required_role:
          await interaction.response.send_message("You are not authorized to set max tickets.", ephemeral=True)
          return

      await interaction.response.send_modal(setMaxTicketModal())

  @discord.ui.button(label="Toggle", style=discord.ButtonStyle.red, custom_id="toggleticket")
  async def toggleticket(self, interaction: discord.Interaction, Button: discord.Button):
      await interaction.response.defer()
      guild_id = interaction.guild.id
      config = get_ticket_config(guild_id)
      message_entry = next((msg for msg in config.get("message", []) if msg["messageid"] == interaction.message.id), None)

      if not message_entry:
          await interaction.followup.send("Ticket message not found.", ephemeral=True)
          return

      is_admin = interaction.user.guild_permissions.administrator
      has_required_role = False
      required_roles = message_entry.get("ticket_role", [])
      if required_roles:
          user_roles = [role.id for role in interaction.user.roles]
          has_required_role = any(role_id in user_roles for role_id in required_roles)

      if not is_admin and not has_required_role:
          await interaction.followup.send("You are not authorized to toggle tickets.", ephemeral=True)
          return

      message_entry["disabled"] = not message_entry.get("disabled", False)
      status = "Disabled" if message_entry["disabled"] else "Enabled"
      save_ticket_config(guild_id, config)
      await interaction.followup.send(f"Successfully toggled ticket: **{status}**.", ephemeral=True)

      try:
          msg = await interaction.channel.fetch_message(interaction.message.id)
          embed = msg.embeds[0]
          num = message_entry.get("max_ticket") or "Limitless"
          embed.set_footer(text=f"Ticket status: {status} | Max Ticket Per User: {num}")
          ticket_button = discord.utils.get(self.children, label="Make a Ticket")
          if ticket_button:
              ticket_button.disabled = message_entry["disabled"]
          await msg.edit(embed=embed, view=self)
      except discord.NotFound:
          await interaction.followup.send("Could not update the ticket message (message not found).", ephemeral=True)

  @discord.ui.button(label="Delete Ticket System", style=discord.ButtonStyle.red, custom_id="deleteticketsystem2")
  async def deleteticketsystem2(self, interaction: discord.Interaction, Button: discord.Button):
      await interaction.response.defer()
      guild_id = interaction.guild.id
      config = get_ticket_config(guild_id)
      message_entry = next((msg for msg in config.get("message", []) if msg["messageid"] == interaction.message.id), None)

      if not message_entry:
          await interaction.followup.send("Ticket message not found.", ephemeral=True)
          return

      is_admin = interaction.user.guild_permissions.administrator
      has_required_role = False
      required_roles = message_entry.get("ticket_role", [])
      if required_roles:
          user_roles = [role.id for role in interaction.user.roles]
          has_required_role = any(role_id in user_roles for role_id in required_roles)

      if not is_admin and not has_required_role:
          await interaction.followup.send("You are not authorized to delete this ticket system.", ephemeral=True)
          return

      confirm_embed = discord.Embed(
          title="Confirm Deletion",
          description="Are you sure you want to delete this ticket system? This action cannot be undone.",
          color=0xff4444
      )
      await interaction.followup.send(embed=confirm_embed, view=DeleteSystemConfirmView(message_entry, guild_id, config), ephemeral=True)
