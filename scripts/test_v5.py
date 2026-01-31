"""Generate comprehensive test report v5 with new Brand/Campaign models."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dialog_gen.generator import DialogGenerator, _get_random_real_dialogs
from dialog_gen.models import Brand, Campaign, DialogContext, GenerateRequest


# Test scenarios
TEST_BRANDS = {
    "FoodBox": Brand(
        name="FoodBox",
        what_is_it="сервис доставки еды из ресторанов",
        topic="food",  # Will use food-related real dialogs
        features=["доставка за 30 минут", "много ресторанов", "отслеживание курьера"],
        promo_code="HUNGRY",
        promo_benefit="скидка 20%",
        do_not_mention=["цены конкурентов", "задержки доставки"]
    ),
    "CityRide": Brand(
        name="CityRide",
        what_is_it="аренда электросамокатов и велосипедов",
        topic="transport",  # Will use transport-related real dialogs
        features=["электросамокаты", "велосипеды", "по всему городу", "поминутная оплата"],
        promo_code="RIDE20",
        promo_benefit="20 минут бесплатно",
        do_not_mention=["аварии", "штрафы"]
    ),
    "FitClub": Brand(
        name="FitClub",
        what_is_it="сеть фитнес-клубов",
        topic="fitness",  # Will use fitness-related real dialogs
        features=["тренажерный зал", "бассейн", "сауна", "персональные тренеры"],
        promo_code="FIT2024",
        promo_benefit="первый месяц за полцены",
        do_not_mention=["очереди", "переполненность"]
    ),
}

# Contexts for different topics
CONTEXTS = {
    "food": DialogContext(
        topic="планы на вечер, хочется поесть",
        messages=[
            {"role": "sender", "content": "жрать охота"},
            {"role": "responder", "content": "да и мне, лень готовить"},
            {"role": "sender", "content": "может закажем чо нить"},
        ]
    ),
    "transport": DialogContext(
        topic="выходные без машины",
        messages=[
            {"role": "sender", "content": "че делаешь на выходных"},
            {"role": "responder", "content": "хз пока не решил"},
            {"role": "sender", "content": "может куда съездим"},
            {"role": "responder", "content": "у тебя машина есть"},
            {"role": "sender", "content": "неа в сервисе блин"},
        ]
    ),
    "fitness": DialogContext(
        topic="хотят начать заниматься спортом",
        messages=[
            {"role": "sender", "content": "слушай надо бы в зал начать ходить"},
            {"role": "responder", "content": "да я тоже думаю об этом"},
            {"role": "sender", "content": "может вместе запишемся"},
        ]
    ),
    "weekend": DialogContext(
        topic="планы на выходные",
        messages=[
            {"role": "sender", "content": "чем займемся в субботу"},
            {"role": "responder", "content": "можно погулять, погода норм"},
            {"role": "sender", "content": "да неохота просто шляться"},
        ]
    ),
}

# Campaign styles to test
CAMPAIGNS = {
    "awareness": Campaign(
        goal="знакомство с брендом",
        style="casual",
        brand_mention_type="личный опыт",
        include_promo=False
    ),
    "trial_promo": Campaign(
        goal="первая покупка",
        style="enthusiastic",
        brand_mention_type="рекомендация",
        include_promo=True
    ),
    "skeptical": Campaign(
        goal="преодоление сомнений",
        style="skeptical",
        brand_mention_type="вопрос",
        include_promo=False
    ),
}

# Test matrix: (brand, context, campaign)
TESTS = [
    # Natural fit tests
    ("FoodBox", "food", "awareness"),
    ("FoodBox", "food", "trial_promo"),
    ("CityRide", "transport", "awareness"),
    ("CityRide", "weekend", "trial_promo"),
    ("FitClub", "fitness", "awareness"),
    ("FitClub", "fitness", "skeptical"),
    # Harder tests - forcing brand into unrelated context
    ("FoodBox", "fitness", "awareness"),
    ("CityRide", "food", "trial_promo"),
    ("FitClub", "transport", "awareness"),
]

MODELS = ["hermes3:8b", "dolphin3:latest", "nous-hermes2:10.7b"]


async def run_test(generator, brand, context, campaign, model):
    """Run a single test."""
    # Capture topic-matched real examples that will be used
    real_examples = _get_random_real_dialogs(3, topic=brand.topic)

    request = GenerateRequest(
        brand=brand,
        campaign=campaign,
        context=context,
        num_turns=8,
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
            "real_examples": real_examples
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "messages": [],
            "time_ms": 0,
            "brand_mentioned": False,
            "real_examples": real_examples
        }


def format_context(context):
    """Format context for report."""
    lines = []
    for m in context.messages:
        lines.append(f"{m['role']}: {m['content']}")
    return "\n".join(lines)


def format_messages(messages):
    """Format messages for report."""
    lines = []
    for m in messages:
        role = m["role"].upper()
        text = m["text"].replace("\n", " ").strip()
        lines.append(f"{role}: {text}")
    return "\n".join(lines)


async def main():
    generator = DialogGenerator()

    print("Starting comprehensive test v5...")
    print(f"Models: {', '.join(MODELS)}")
    print(f"Total tests: {len(TESTS) * len(MODELS)}")
    print()

    results = {}

    for model in MODELS:
        print(f"\n=== Testing {model} ===")
        results[model] = []

        for brand_name, context_name, campaign_name in TESTS:
            brand = TEST_BRANDS[brand_name]
            context = CONTEXTS[context_name]
            campaign = CAMPAIGNS[campaign_name]

            test_id = f"{brand_name}+{context_name}+{campaign_name}"
            print(f"  {test_id}...", end=" ", flush=True)

            result = await run_test(generator, brand, context, campaign, model)
            result["brand_name"] = brand_name
            result["context_name"] = context_name
            result["campaign_name"] = campaign_name
            result["brand"] = brand
            result["context"] = context
            result["campaign"] = campaign

            results[model].append(result)

            status = "✓" if result["brand_mentioned"] else "✗"
            msgs = len(result["messages"])
            print(f"{status} ({msgs} msgs, {result['time_ms']}ms)")

    # Generate report
    report = []
    report.append("# Dialog Generation Report v5")
    report.append("")
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Models:** {', '.join(MODELS)}")
    report.append(f"**Real dialogs loaded:** 208 examples from public Telegram channels")
    report.append("")
    report.append("---")
    report.append("")

    # Summary table
    report.append("## Summary")
    report.append("")
    report.append("| Model | Avg Msgs | Brand Mention % | Natural Context % | Forced Context % |")
    report.append("|-------|----------|-----------------|-------------------|------------------|")

    for model in MODELS:
        model_results = results[model]

        avg_msgs = sum(len(r["messages"]) for r in model_results) / len(model_results)
        brand_pct = sum(1 for r in model_results if r["brand_mentioned"]) / len(model_results) * 100

        # Natural: first 6 tests, Forced: last 3
        natural = model_results[:6]
        forced = model_results[6:]

        natural_pct = sum(1 for r in natural if r["brand_mentioned"]) / len(natural) * 100
        forced_pct = sum(1 for r in forced if r["brand_mentioned"]) / len(forced) * 100

        report.append(f"| {model} | {avg_msgs:.1f} | {brand_pct:.0f}% | {natural_pct:.0f}% | {forced_pct:.0f}% |")

    report.append("")
    report.append("---")
    report.append("")

    # Detailed results by model
    for model in MODELS:
        report.append(f"## {model}")
        report.append("")

        for result in results[model]:
            test_type = "Natural" if results[model].index(result) < 6 else "Forced"
            brand_status = "✓" if result["brand_mentioned"] else "✗"

            report.append(f"### {result['brand_name']} + {result['context_name']} ({result['campaign_name']}) [{test_type}]")
            report.append(f"**Msgs:** {len(result['messages'])} | **Brand:** {brand_status} | **Time:** {result['time_ms']}ms")
            report.append("")
            report.append("**Campaign Goal:** " + result["campaign"].goal)
            report.append("**Brand Mention Type:** " + result["campaign"].brand_mention_type)
            if result["campaign"].include_promo:
                report.append(f"**Promo:** {result['brand'].promo_code} ({result['brand'].promo_benefit})")
            report.append("")
            report.append("**Context:**")
            report.append("```")
            report.append(format_context(result["context"]))
            report.append("```")
            if result.get("real_examples"):
                report.append("**Real Dialog Examples Used:**")
                report.append("```")
                for i, ex in enumerate(result["real_examples"], 1):
                    report.append(f"--- Example {i} ---")
                    report.append(ex)
                report.append("```")
            report.append("**Output:**")
            report.append("```")
            if result["messages"]:
                report.append(format_messages(result["messages"]))
            else:
                report.append(f"ERROR: {result.get('error', 'No messages generated')}")
            report.append("```")
            report.append("---")
            report.append("")

        report.append("")

    # Write report
    output_file = Path(__file__).parent.parent / "REPORT_v5.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"\n\nReport saved to {output_file}")

    # Print summary
    print("\n=== SUMMARY ===")
    for model in MODELS:
        model_results = results[model]
        brand_pct = sum(1 for r in model_results if r["brand_mentioned"]) / len(model_results) * 100
        avg_msgs = sum(len(r["messages"]) for r in model_results) / len(model_results)
        print(f"{model}: {brand_pct:.0f}% brand mention, {avg_msgs:.1f} avg msgs")


if __name__ == "__main__":
    asyncio.run(main())
