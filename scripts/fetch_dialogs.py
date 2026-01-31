"""Fetch real dialogs from public Telegram channels."""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon.tl.types import Message, PeerUser

# Topic-specific channels matching our test brands
TOPIC_CHATS = {
    "food": [
        # Food / cooking / delivery discussions
        "povarchatok",         # Cooking chat
        "kulinariya_chat",     # Culinary chat
        "gotovka_chat",        # Cooking chat
        "recept_chat",         # Recipe chat
        "eda_chat",            # Food chat
        "vkusnaya_eda",        # Tasty food
    ],
    "transport": [
        # Scooters / bikes / transport
        "samokat_chat",        # Scooter chat
        "elektrosamokat_chat", # Electric scooters
        "velobike_chat",       # Bike chat
        "esamokat_chat",       # E-scooter chat
        "kick_chat",           # Kick scooter chat
    ],
    "fitness": [
        # Fitness / gym / health
        "zozh_chat",           # Healthy lifestyle
        "fitnes_chat",         # Fitness chat
        "sport_chat_ru",       # Sport chat
        "trener_chat",         # Trainer chat
        "beg_chat",            # Running chat
    ],
}

# Flatten for fetching
PUBLIC_CHATS = []
for topic, chats in TOPIC_CHATS.items():
    PUBLIC_CHATS.extend(chats)


def get_topic_for_channel(channel: str) -> str:
    """Get topic category for a channel."""
    for topic, chats in TOPIC_CHATS.items():
        if channel in chats:
            return topic
    return "general"


async def fetch_dialogs_from_channel(client: TelegramClient, channel: str, limit: int = 500):
    """Fetch message sequences that look like dialogs."""
    dialogs = []
    topic = get_topic_for_channel(channel)

    try:
        entity = await client.get_entity(channel)
        messages = await client.get_messages(entity, limit=limit)

        # Build a dict of all messages by ID
        msg_by_id = {}
        for msg in messages:
            if isinstance(msg, Message) and msg.text:
                if 5 <= len(msg.text) <= 300:
                    msg_by_id[msg.id] = {
                        "id": msg.id,
                        "text": msg.text,
                        "from_id": msg.from_id.user_id if isinstance(msg.from_id, PeerUser) else None,
                        "reply_to": msg.reply_to.reply_to_msg_id if msg.reply_to else None,
                        "date": msg.date
                    }

        # Build conversation threads by following reply chains
        used_ids = set()

        for msg_id, msg in msg_by_id.items():
            if msg_id in used_ids:
                continue

            # Find the root of this thread
            root_id = msg_id
            while msg_by_id.get(root_id, {}).get("reply_to") in msg_by_id:
                root_id = msg_by_id[root_id]["reply_to"]

            # Build thread from root
            thread = []
            current_id = root_id

            # Add root
            if current_id in msg_by_id:
                thread.append(msg_by_id[current_id])
                used_ids.add(current_id)

            # Find all replies to this thread (breadth-first)
            to_process = [current_id]
            while to_process:
                parent_id = to_process.pop(0)
                # Find messages replying to parent
                replies = [(mid, m) for mid, m in msg_by_id.items()
                          if m.get("reply_to") == parent_id and mid not in used_ids]
                replies.sort(key=lambda x: x[1]["date"])

                for mid, m in replies:
                    thread.append(m)
                    used_ids.add(mid)
                    to_process.append(mid)

            # Only keep threads with enough messages
            if len(thread) >= 4:
                # Assign person1, person2, person3, etc. based on user IDs
                users = list(set(m.get("from_id") for m in thread if m.get("from_id")))
                user_roles = {uid: f"person{i + 1}" for i, uid in enumerate(users)}

                dialog = {
                    "source": channel,
                    "topic": topic,
                    "messages": [
                        {
                            "role": user_roles.get(m.get("from_id"), f"person{(i % 3) + 1}"),
                            "text": m["text"]
                        }
                        for i, m in enumerate(thread)
                    ]
                }
                dialogs.append(dialog)

        print(f"  {channel}: found {len(dialogs)} dialog chains [{topic}]")

    except Exception as e:
        print(f"  {channel}: error - {e}")

    return dialogs


async def main():
    # Find first profile with session file and load credentials
    profiles_dir = Path(__file__).parent.parent.parent / "ca-bot" / "profiles"

    session_file = None
    profile_json = None

    for profile_path in profiles_dir.iterdir():
        if not profile_path.is_dir():
            continue
        possible_session = profile_path / f"{profile_path.name}.session"
        possible_json = profile_path / f"{profile_path.name}.json"
        if possible_session.exists() and possible_json.exists():
            session_file = possible_session
            profile_json = possible_json
            break

    if not session_file or not profile_json:
        print("No profile with session and JSON found")
        return

    # Load credentials from profile JSON
    with open(profile_json) as f:
        profile_data = json.load(f)

    api_id = profile_data.get("app_id")
    api_hash = profile_data.get("app_hash")

    if not api_id or not api_hash:
        print("Missing app_id or app_hash in profile JSON")
        return

    print(f"Using session: {session_file}")

    client = TelegramClient(
        str(session_file).replace(".session", ""),
        api_id,
        api_hash
    )

    await client.connect()

    if not await client.is_user_authorized():
        print("Client not authorized")
        return

    print("Fetching dialogs from public channels...")

    all_dialogs = []
    for channel in PUBLIC_CHATS:
        dialogs = await fetch_dialogs_from_channel(client, channel, limit=200)
        all_dialogs.extend(dialogs)

    await client.disconnect()

    # Save dialogs
    output_file = Path(__file__).parent.parent / "data" / "real_dialogs.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_dialogs, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(all_dialogs)} dialogs to {output_file}")

    # Show samples
    print("\n=== SAMPLE DIALOGS ===")
    for d in all_dialogs[:3]:
        print(f"\nFrom {d['source']}:")
        for m in d["messages"][:4]:
            print(f"  {m['role']}: {m['text'][:80]}...")


if __name__ == "__main__":
    asyncio.run(main())
