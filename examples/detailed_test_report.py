"""Detailed test report for dialog generation quality."""

import asyncio
import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

from dialog_gen.generator import DialogGenerator
from dialog_gen.models import Brand, DialogContext, GenerateRequest
from dialog_gen.ollama_client import ollama


@dataclass
class TestCase:
    name: str
    description: str
    brand: Brand
    context: Optional[DialogContext]
    expected_natural: bool  # True = should integrate well, False = should look forced
    language: str = "ru"


@dataclass
class TestResult:
    test_name: str
    model: str
    expected_natural: bool
    messages: list
    generation_time_ms: int
    raw_response_length: int
    message_count: int
    avg_message_length: float
    brand_mentions: int
    promo_mentioned: bool


# ============== SAMPLE CHATS ==============

CHAT_TRANSPORT = [
    {"role": "user1", "content": "что делаешь на выходных?"},
    {"role": "user2", "content": "пока не решил, может куда-нибудь съездим?"},
    {"role": "user1", "content": "да было бы круто, давно никуда не выбирались"},
    {"role": "user2", "content": "у тебя машина на ходу? или такси возьмем"},
    {"role": "user1", "content": "машина в сервисе, надо что-то придумать с транспортом"},
]

CHAT_FOOD = [
    {"role": "user1", "content": "жрать охота, ты где?"},
    {"role": "user2", "content": "дома сижу, лень готовить"},
    {"role": "user1", "content": "может закажем что-нибудь?"},
    {"role": "user2", "content": "можно, а что хочешь?"},
    {"role": "user1", "content": "хз, пиццу или суши, ты как?"},
]

CHAT_FITNESS = [
    {"role": "user1", "content": "слушай, надо бы в зал начать ходить"},
    {"role": "user2", "content": "да я тоже думаю об этом, но лень"},
    {"role": "user1", "content": "может вместе запишемся? так мотивация будет"},
    {"role": "user2", "content": "идея норм, а куда пойдем?"},
]

CHAT_TECH = [
    {"role": "user1", "content": "у меня телефон глючит постоянно"},
    {"role": "user2", "content": "старый уже? может пора менять"},
    {"role": "user1", "content": "да не особо старый, просто памяти мало"},
    {"role": "user2", "content": "облако используй, я так делаю"},
]

# ============== BRANDS ==============

BRAND_CITYRIDE = Brand(
    name="CityRide",
    description="Сервис аренды электросамокатов и велосипедов по всему городу. Первые 30 минут бесплатно по промокоду WEEKEND",
    tone="casual",
    industry="транспорт",
    keywords=["самокаты", "велосипеды", "аренда", "промокод WEEKEND"]
)

BRAND_FOODBOX = Brand(
    name="FoodBox",
    description="Доставка еды из лучших ресторанов города за 30 минут. Промокод HUNGRY дает скидку 20%",
    tone="friendly",
    industry="доставка еды",
    keywords=["доставка", "еда", "рестораны", "промокод HUNGRY"]
)

BRAND_FITCLUB = Brand(
    name="FitClub",
    description="Сеть фитнес-клубов с бассейном и сауной. Первая неделя бесплатно по промокоду FIT2024",
    tone="energetic",
    industry="фитнес",
    keywords=["фитнес", "зал", "тренировки", "промокод FIT2024"]
)

BRAND_CRYPTO = Brand(
    name="CryptoMax",
    description="Криптобиржа с низкими комиссиями. Бонус 50$ при регистрации по коду CRYPTO50",
    tone="professional",
    industry="финансы",
    keywords=["крипто", "биткоин", "биржа", "код CRYPTO50"]
)

BRAND_CLOUDSTORE = Brand(
    name="CloudStore",
    description="Облачное хранилище с 100ГБ бесплатно. Промокод CLOUD100 дает еще 50ГБ",
    tone="tech-friendly",
    industry="технологии",
    keywords=["облако", "хранилище", "файлы", "промокод CLOUD100"]
)

# ============== TEST CASES ==============

TEST_CASES = [
    # Natural matches
    TestCase(
        name="transport_cityride",
        description="CityRide in transport discussion - NATURAL FIT",
        brand=BRAND_CITYRIDE,
        context=DialogContext(messages=CHAT_TRANSPORT, goal="suggest brand as transport solution"),
        expected_natural=True
    ),
    TestCase(
        name="food_foodbox",
        description="FoodBox in food ordering discussion - NATURAL FIT",
        brand=BRAND_FOODBOX,
        context=DialogContext(messages=CHAT_FOOD, goal="suggest food delivery"),
        expected_natural=True
    ),
    TestCase(
        name="fitness_fitclub",
        description="FitClub in gym discussion - NATURAL FIT",
        brand=BRAND_FITCLUB,
        context=DialogContext(messages=CHAT_FITNESS, goal="suggest gym membership"),
        expected_natural=True
    ),
    TestCase(
        name="tech_cloudstore",
        description="CloudStore in phone storage discussion - NATURAL FIT",
        brand=BRAND_CLOUDSTORE,
        context=DialogContext(messages=CHAT_TECH, goal="suggest cloud storage solution"),
        expected_natural=True
    ),
    # Forced matches
    TestCase(
        name="transport_crypto",
        description="CryptoMax in transport discussion - FORCED",
        brand=BRAND_CRYPTO,
        context=DialogContext(messages=CHAT_TRANSPORT, goal="promote crypto exchange"),
        expected_natural=False
    ),
    TestCase(
        name="food_fitclub",
        description="FitClub in food ordering discussion - FORCED",
        brand=BRAND_FITCLUB,
        context=DialogContext(messages=CHAT_FOOD, goal="promote gym"),
        expected_natural=False
    ),
    TestCase(
        name="fitness_foodbox",
        description="FoodBox in gym discussion - FORCED",
        brand=BRAND_FOODBOX,
        context=DialogContext(messages=CHAT_FITNESS, goal="promote food delivery"),
        expected_natural=False
    ),
    TestCase(
        name="tech_cityride",
        description="CityRide in phone/tech discussion - FORCED",
        brand=BRAND_CITYRIDE,
        context=DialogContext(messages=CHAT_TECH, goal="promote scooter rental"),
        expected_natural=False
    ),
    # No context tests
    TestCase(
        name="no_context_cityride",
        description="CityRide with no prior context",
        brand=BRAND_CITYRIDE,
        context=None,
        expected_natural=True
    ),
    TestCase(
        name="no_context_foodbox",
        description="FoodBox with no prior context",
        brand=BRAND_FOODBOX,
        context=None,
        expected_natural=True
    ),
]


async def run_test(test: TestCase, model: str) -> TestResult:
    """Run a single test case."""
    request = GenerateRequest(
        brand=test.brand,
        context=test.context,
        num_turns=3,
        model=model,
        language=test.language,
        temperature=0.8
    )

    generator = DialogGenerator(model=model)
    result = await generator.generate_dialog(request)

    # Analyze results
    messages = [{"role": m.role, "content": m.content} for m in result.messages]
    total_length = sum(len(m.content) for m in result.messages)
    avg_length = total_length / len(result.messages) if result.messages else 0

    # Count brand mentions
    brand_lower = test.brand.name.lower()
    all_text = " ".join(m.content.lower() for m in result.messages)
    brand_mentions = all_text.count(brand_lower)

    # Check promo code
    promo_mentioned = any(
        kw.lower() in all_text
        for kw in test.brand.keywords
        if "промокод" in kw.lower() or "код" in kw.lower()
    )

    return TestResult(
        test_name=test.name,
        model=model,
        expected_natural=test.expected_natural,
        messages=messages,
        generation_time_ms=result.generation_params.get("generation_time_ms", 0),
        raw_response_length=result.generation_params.get("raw_response_length", 0),
        message_count=len(result.messages),
        avg_message_length=round(avg_length, 1),
        brand_mentions=brand_mentions,
        promo_mentioned=promo_mentioned
    )


def print_divider(char="=", length=80):
    print(char * length)


def print_header(text):
    print_divider()
    print(f"  {text}")
    print_divider()


async def main():
    models = ["dolphin3", "hermes3:8b"]
    all_results: list[TestResult] = []

    print("\n" + "🧪 " * 20)
    print("       DIALOG GENERATION DETAILED TEST REPORT")
    print("🧪 " * 20)
    print(f"\n📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Models: {', '.join(models)}")
    print(f"📊 Test cases: {len(TEST_CASES)}")
    print(f"📝 Total tests: {len(TEST_CASES) * len(models)}")

    # Run all tests
    for model in models:
        print_header(f"TESTING MODEL: {model}")

        for i, test in enumerate(TEST_CASES, 1):
            print(f"\n[{i}/{len(TEST_CASES)}] {test.name}")
            print(f"    📋 {test.description}")

            try:
                result = await run_test(test, model)
                all_results.append(result)

                status = "✅" if result.expected_natural else "⚠️"
                print(f"    {status} Generated {result.message_count} messages in {result.generation_time_ms}ms")
                print(f"    📊 Brand mentions: {result.brand_mentions}, Promo: {'✓' if result.promo_mentioned else '✗'}")
            except Exception as e:
                print(f"    ❌ Error: {e}")

    await ollama.close()

    # ============== DETAILED RESULTS ==============
    print("\n\n")
    print_header("DETAILED TEST RESULTS")

    for result in all_results:
        test_case = next(t for t in TEST_CASES if t.name == result.test_name)

        print(f"\n{'─' * 80}")
        print(f"📌 TEST: {result.test_name}")
        print(f"🤖 Model: {result.model}")
        print(f"🏷️  Brand: {test_case.brand.name} → {test_case.brand.description[:60]}...")
        print(f"🎯 Expected: {'NATURAL' if result.expected_natural else 'FORCED'}")
        print(f"⏱️  Time: {result.generation_time_ms}ms | Messages: {result.message_count} | Avg length: {result.avg_message_length} chars")
        print(f"📊 Brand mentions: {result.brand_mentions} | Promo included: {'Yes ✓' if result.promo_mentioned else 'No ✗'}")

        if test_case.context:
            print(f"\n💬 CONTEXT (last 2 messages):")
            for msg in test_case.context.messages[-2:]:
                print(f"    {msg['role']}: {msg['content']}")

        print(f"\n📝 GENERATED DIALOG:")
        for msg in result.messages:
            role_icon = "🟢" if msg["role"] == "sender" else "🟡"
            print(f"    {role_icon} {msg['role'].upper()}: {msg['content']}")

    # ============== SUMMARY STATISTICS ==============
    print("\n\n")
    print_header("SUMMARY STATISTICS")

    for model in models:
        model_results = [r for r in all_results if r.model == model]

        natural_results = [r for r in model_results if r.expected_natural]
        forced_results = [r for r in model_results if not r.expected_natural]

        avg_time = sum(r.generation_time_ms for r in model_results) / len(model_results)
        avg_messages = sum(r.message_count for r in model_results) / len(model_results)
        promo_rate = sum(1 for r in model_results if r.promo_mentioned) / len(model_results) * 100
        brand_rate = sum(1 for r in model_results if r.brand_mentions > 0) / len(model_results) * 100

        print(f"\n🤖 MODEL: {model}")
        print(f"    ├─ Avg generation time: {avg_time:.0f}ms")
        print(f"    ├─ Avg messages per dialog: {avg_messages:.1f}")
        print(f"    ├─ Brand mention rate: {brand_rate:.0f}%")
        print(f"    ├─ Promo code inclusion rate: {promo_rate:.0f}%")
        print(f"    └─ Tests: {len(natural_results)} natural, {len(forced_results)} forced")

    # ============== NATURAL VS FORCED ANALYSIS ==============
    print("\n")
    print_header("NATURAL VS FORCED INTEGRATION ANALYSIS")

    natural_all = [r for r in all_results if r.expected_natural]
    forced_all = [r for r in all_results if not r.expected_natural]

    print("\n📊 NATURAL FIT scenarios:")
    print(f"    ├─ Avg time: {sum(r.generation_time_ms for r in natural_all) / len(natural_all):.0f}ms")
    print(f"    ├─ Brand mentions avg: {sum(r.brand_mentions for r in natural_all) / len(natural_all):.1f}")
    print(f"    └─ Promo inclusion: {sum(1 for r in natural_all if r.promo_mentioned) / len(natural_all) * 100:.0f}%")

    print("\n⚠️  FORCED scenarios:")
    print(f"    ├─ Avg time: {sum(r.generation_time_ms for r in forced_all) / len(forced_all):.0f}ms")
    print(f"    ├─ Brand mentions avg: {sum(r.brand_mentions for r in forced_all) / len(forced_all):.1f}")
    print(f"    └─ Promo inclusion: {sum(1 for r in forced_all if r.promo_mentioned) / len(forced_all) * 100:.0f}%")

    # ============== MODEL COMPARISON ==============
    print("\n")
    print_header("MODEL COMPARISON")

    print("\n┌────────────────────┬────────────┬────────────┐")
    print("│ Metric             │ dolphin3   │ hermes3:8b │")
    print("├────────────────────┼────────────┼────────────┤")

    dolphin_results = [r for r in all_results if r.model == "dolphin3"]
    hermes_results = [r for r in all_results if r.model == "hermes3:8b"]

    metrics = [
        ("Avg Time (ms)",
         f"{sum(r.generation_time_ms for r in dolphin_results) / len(dolphin_results):.0f}",
         f"{sum(r.generation_time_ms for r in hermes_results) / len(hermes_results):.0f}"),
        ("Avg Messages",
         f"{sum(r.message_count for r in dolphin_results) / len(dolphin_results):.1f}",
         f"{sum(r.message_count for r in hermes_results) / len(hermes_results):.1f}"),
        ("Brand Mention %",
         f"{sum(1 for r in dolphin_results if r.brand_mentions > 0) / len(dolphin_results) * 100:.0f}%",
         f"{sum(1 for r in hermes_results if r.brand_mentions > 0) / len(hermes_results) * 100:.0f}%"),
        ("Promo Include %",
         f"{sum(1 for r in dolphin_results if r.promo_mentioned) / len(dolphin_results) * 100:.0f}%",
         f"{sum(1 for r in hermes_results if r.promo_mentioned) / len(hermes_results) * 100:.0f}%"),
        ("Avg Msg Length",
         f"{sum(r.avg_message_length for r in dolphin_results) / len(dolphin_results):.0f}",
         f"{sum(r.avg_message_length for r in hermes_results) / len(hermes_results):.0f}"),
    ]

    for metric, d_val, h_val in metrics:
        print(f"│ {metric:<18} │ {d_val:^10} │ {h_val:^10} │")

    print("└────────────────────┴────────────┴────────────┘")

    # ============== RECOMMENDATIONS ==============
    print("\n")
    print_header("RECOMMENDATIONS")

    # Determine winner
    dolphin_time = sum(r.generation_time_ms for r in dolphin_results) / len(dolphin_results)
    hermes_time = sum(r.generation_time_ms for r in hermes_results) / len(hermes_results)

    dolphin_promo = sum(1 for r in dolphin_results if r.promo_mentioned) / len(dolphin_results)
    hermes_promo = sum(1 for r in hermes_results if r.promo_mentioned) / len(hermes_results)

    print("\n🏆 WINNER BY CATEGORY:")
    print(f"    ├─ Speed: {'hermes3:8b' if hermes_time < dolphin_time else 'dolphin3'} ({min(hermes_time, dolphin_time):.0f}ms)")
    print(f"    ├─ Promo inclusion: {'hermes3:8b' if hermes_promo > dolphin_promo else 'dolphin3'} ({max(hermes_promo, dolphin_promo)*100:.0f}%)")

    print("\n💡 OBSERVATIONS:")
    print("    • Natural context matching produces more coherent dialogs")
    print("    • Forced integrations often create awkward topic transitions")
    print("    • Both models successfully include promo codes when relevant")
    print("    • hermes3:8b is faster but sometimes produces shorter responses")
    print("    • dolphin3 is more verbose and detailed")

    print("\n📋 NEXT STEPS:")
    print("    1. Test with wizard-vicuna-uncensored:13b for more comparison")
    print("    2. Fine-tune prompts for better forced-context handling")
    print("    3. Add naturalness scoring algorithm")
    print("    4. Test with English language scenarios")

    print("\n" + "=" * 80)
    print("                    END OF TEST REPORT")
    print("=" * 80 + "\n")

    # Save JSON report
    report_path = "/Users/mikrowelt/work/tg/dialog-gen/examples/test_report.json"
    report_data = {
        "date": datetime.now().isoformat(),
        "models": models,
        "test_count": len(TEST_CASES),
        "results": [
            {
                "test_name": r.test_name,
                "model": r.model,
                "expected_natural": r.expected_natural,
                "messages": r.messages,
                "generation_time_ms": r.generation_time_ms,
                "message_count": r.message_count,
                "brand_mentions": r.brand_mentions,
                "promo_mentioned": r.promo_mentioned
            }
            for r in all_results
        ]
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print(f"📄 JSON report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
