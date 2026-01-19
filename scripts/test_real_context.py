"""Test dialog generation using REAL dialogs as context."""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dialog_gen.generator import DialogGenerator
from dialog_gen.models import Brand, Campaign, DialogContext, GenerateRequest


# Brands to test - NO promo codes, natural mentions only
BRANDS = {
    "FoodBox": Brand(
        name="FoodBox",
        what_is_it="сервис доставки еды из ресторанов",
        topic="food",
        features=["быстрая доставка", "много ресторанов"],
    ),
    "CityRide": Brand(
        name="CityRide",
        what_is_it="аренда электросамокатов и велосипедов",
        topic="transport",
        features=["электросамокаты", "велосипеды", "по всему городу"],
    ),
    "FitClub": Brand(
        name="FitClub",
        what_is_it="сеть фитнес-клубов",
        topic="fitness",
        features=["тренажерный зал", "бассейн", "персональные тренеры"],
    ),
}

# Natural awareness campaign - no promos, no discounts
CAMPAIGN = Campaign(
    goal="знакомство с брендом",
    style="casual",
    brand_mention_type="личный опыт",
    include_promo=False,
)

# Bad words filter
BAD_WORDS = ['хуй', 'пидор', 'ебат', 'блядь', 'сука', 'нахуй', 'пизд', 'хуе', 'ёб', 'жоп', 'бля']

MODELS = ["hermes3:8b", "dolphin3:latest", "nous-hermes2:10.7b"]


def load_clean_dialogs(min_messages: int = 10):
    """Load and filter clean real dialogs with at least min_messages."""
    dialogs_file = Path(__file__).parent.parent / "data" / "real_dialogs.json"
    dialogs = json.load(open(dialogs_file))

    good = []
    for d in dialogs:
        msgs = d.get("messages", [])
        if len(msgs) < min_messages:
            continue

        # Check messages for bad content
        clean = True
        clean_msgs = []
        for m in msgs:
            text = m.get("text", "").lower()
            if len(text) < 3:
                continue
            if any(bad in text for bad in BAD_WORDS):
                clean = False
                break
            clean_msgs.append(m)

        if clean and len(clean_msgs) >= min_messages:
            d["messages"] = clean_msgs[:15]  # Cap at 15 messages for context
            good.append(d)

    return good


async def run_test(generator, brand, campaign, real_dialog, model):
    """Run a single test with real dialog as context."""
    # Normalize roles to person1, person2, etc.
    normalized_messages = []
    role_map = {}
    for m in real_dialog["messages"]:
        role = m["role"]
        # Map old sender/responder to person format
        if role == "sender":
            role = "person1"
        elif role == "responder":
            role = "person2"
        # If role is not already in person format, assign dynamically
        if not role.startswith("person"):
            if role not in role_map:
                role_map[role] = f"person{len(role_map) + 1}"
            role = role_map[role]
        normalized_messages.append({"role": role, "content": m["text"]})

    context = DialogContext(
        topic=real_dialog.get("topic", "casual"),
        messages=normalized_messages
    )

    request = GenerateRequest(
        brand=brand,
        campaign=campaign,
        context=context,
        num_turns=4,
        model=model,
        language="ru"
    )

    try:
        result = await generator.generate_dialog(request)
        return {
            "success": True,
            "messages": [{"role": m.role, "text": m.content} for m in result.messages],
            "time_ms": result.generation_params.get("generation_time_ms", 0),
            "brand_mentioned": any(brand.name.lower() in m.content.lower() for m in result.messages),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "messages": [],
            "time_ms": 0,
            "brand_mentioned": False,
        }


async def main():
    generator = DialogGenerator()

    # Load real dialogs
    dialogs = load_clean_dialogs()
    print(f"Loaded {len(dialogs)} clean real dialogs")

    # Group by topic
    by_topic = {}
    for d in dialogs:
        topic = d.get("topic", "general")
        if topic not in by_topic:
            by_topic[topic] = []
        by_topic[topic].append(d)

    print(f"Topics: {', '.join(f'{k}({len(v)})' for k, v in by_topic.items())}")
    print()

    # Test matrix: for each brand, test with matching topic dialogs
    tests = []
    for brand_name, brand in BRANDS.items():
        # Get dialogs matching brand topic, or any if none match
        topic_dialogs = by_topic.get(brand.topic, dialogs)
        if not topic_dialogs:
            topic_dialogs = dialogs

        # Pick 3 random dialogs for this brand
        sample = random.sample(topic_dialogs, min(3, len(topic_dialogs)))
        for dialog in sample:
            tests.append((brand_name, brand, dialog))

    print(f"Running {len(tests)} tests...")
    print("=" * 60)

    results = []
    for model in MODELS:
        print(f"\n=== Model: {model} ===")

        for brand_name, brand, dialog in tests:
            test_id = f"{brand_name}+{dialog.get('topic', 'general')}"

            print(f"  {test_id}...", end=" ", flush=True)

            result = await run_test(generator, brand, CAMPAIGN, dialog, model)
            result["brand_name"] = brand_name
            result["brand"] = brand
            result["dialog"] = dialog
            result["campaign"] = CAMPAIGN
            result["model"] = model

            results.append(result)

            status = "✓" if result["brand_mentioned"] else "✗"
            print(f"{status} ({len(result['messages'])} msgs, {result['time_ms']}ms)")

    # Generate report - grouped by model
    report = []
    report.append("# Real Context Dialog Test Report")
    report.append("")
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Total tests:** {len(results)}")
    report.append("")

    # Summary table by model
    report.append("## Summary by Model")
    report.append("")
    report.append("| Model | Brand Mention | Avg Time |")
    report.append("|-------|---------------|----------|")

    for model in MODELS:
        model_results = [r for r in results if r["model"] == model]
        mentioned = sum(1 for r in model_results if r["brand_mentioned"])
        avg_time = sum(r["time_ms"] for r in model_results) // len(model_results) if model_results else 0
        report.append(f"| {model} | {mentioned}/{len(model_results)} ({100*mentioned//len(model_results) if model_results else 0}%) | {avg_time}ms |")

    total_mentioned = sum(1 for r in results if r["brand_mentioned"])
    report.append(f"| **Total** | **{total_mentioned}/{len(results)} ({100*total_mentioned//len(results)}%)** | |")
    report.append("")
    report.append("---")
    report.append("")

    # Detailed results by model
    for model in MODELS:
        model_results = [r for r in results if r["model"] == model]
        mentioned = sum(1 for r in model_results if r["brand_mentioned"])

        report.append(f"## {model}")
        report.append(f"**Results:** {mentioned}/{len(model_results)} ({100*mentioned//len(model_results) if model_results else 0}%)")
        report.append("")

        for result in model_results:
            brand_status = "✓" if result["brand_mentioned"] else "✗"
            report.append(f"### {result['brand_name']} [{brand_status}] - {result['time_ms']}ms")
            report.append("")
            report.append(f"**Topic:** {result['dialog'].get('topic', 'general')}")
            report.append("")

            report.append("**Real Dialog (input):**")
            report.append("```")
            for m in result["dialog"]["messages"][:8]:  # Show first 8 messages
                text = m['text'].replace('\n', ' ')[:80]
                report.append(f"{m['role']}: {text}")
            if len(result["dialog"]["messages"]) > 8:
                report.append(f"... ({len(result['dialog']['messages']) - 8} more messages)")
            report.append("```")
            report.append("")

            report.append("**Generated Continuation:**")
            report.append("```")
            if result["messages"]:
                for m in result["messages"]:
                    text = m["text"].replace("\n", " ")[:100]
                    report.append(f"{m['role'].upper()}: {text}")
            else:
                report.append(f"ERROR: {result.get('error', 'No messages')}")
            report.append("```")
            report.append("")
            report.append("---")
            report.append("")

        report.append("")

    # Write report
    output_file = Path(__file__).parent.parent / "REPORT_real_context.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"\n\nReport saved to {output_file}")

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Brand mention: {mentioned}/{len(results)} ({100*mentioned//len(results)}%)")


if __name__ == "__main__":
    asyncio.run(main())
