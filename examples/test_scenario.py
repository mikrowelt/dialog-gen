"""Test scenario: Generate dialogs that integrate naturally into existing chat."""

import asyncio
from dialog_gen.generator import DialogGenerator
from dialog_gen.models import Brand, DialogContext, GenerateRequest
from dialog_gen.ollama_client import ollama

# Sample existing chat - friends discussing weekend plans
SAMPLE_CHAT = [
    {"role": "user1", "content": "что делаешь на выходных?"},
    {"role": "user2", "content": "пока не решил, может куда-нибудь съездим?"},
    {"role": "user1", "content": "да было бы круто, давно никуда не выбирались"},
    {"role": "user2", "content": "у тебя машина на ходу? или такси возьмем"},
    {"role": "user1", "content": "машина в сервисе, надо что-то придумать с транспортом"},
]

# Brand to promote
BRAND = Brand(
    name="CityRide",
    description="Сервис аренды электросамокатов и велосипедов по всему городу. Первые 30 минут бесплатно по промокоду WEEKEND",
    tone="casual",
    industry="транспорт/мобильность",
    target_audience="молодежь 18-35",
    keywords=["самокаты", "велосипеды", "аренда", "город", "экология"]
)

# Alternative brand for comparison
BRAND_CRYPTO = Brand(
    name="CryptoMax",
    description="Криптобиржа с низкими комиссиями и мгновенными переводами",
    tone="professional",
    industry="финансы",
    keywords=["крипто", "биткоин", "инвестиции"]
)


async def test_natural_integration():
    """Test dialog that should integrate naturally (transport topic matches)."""
    print("=" * 60)
    print("TEST 1: NATURAL INTEGRATION (CityRide - transport context)")
    print("=" * 60)
    print("\n📱 Existing chat:")
    for msg in SAMPLE_CHAT:
        print(f"  {msg['role']}: {msg['content']}")

    print(f"\n🏷️  Brand: {BRAND.name} - {BRAND.description[:50]}...")

    context = DialogContext(
        messages=SAMPLE_CHAT,
        topic="weekend transportation",
        goal="naturally suggest the brand as solution to their problem"
    )

    request = GenerateRequest(
        brand=BRAND,
        context=context,
        num_turns=3,
        model="hermes3:8b",
        language="ru",
        temperature=0.9
    )

    generator = DialogGenerator(model="hermes3:8b")
    result = await generator.generate_dialog(request)

    print("\n✅ Generated continuation:")
    for msg in result.messages:
        print(f"  {msg.role.upper()}: {msg.content}")
    print(f"\n⏱️  Generated in {result.generation_params.get('generation_time_ms')}ms")

    return result


async def test_forced_integration():
    """Test dialog that would look forced (crypto in transport context)."""
    print("\n" + "=" * 60)
    print("TEST 2: FORCED INTEGRATION (CryptoMax - wrong context)")
    print("=" * 60)
    print("\n📱 Same chat about weekend/transport...")
    print(f"🏷️  Brand: {BRAND_CRYPTO.name} - {BRAND_CRYPTO.description[:50]}...")

    context = DialogContext(
        messages=SAMPLE_CHAT,
        topic="weekend transportation",
        goal="naturally suggest the brand"
    )

    request = GenerateRequest(
        brand=BRAND_CRYPTO,
        context=context,
        num_turns=3,
        model="hermes3:8b",
        language="ru",
        temperature=0.9
    )

    generator = DialogGenerator(model="hermes3:8b")
    result = await generator.generate_dialog(request)

    print("\n❌ Generated (likely looks forced):")
    for msg in result.messages:
        print(f"  {msg.role.upper()}: {msg.content}")
    print(f"\n⏱️  Generated in {result.generation_params.get('generation_time_ms')}ms")

    return result


async def test_no_context():
    """Test dialog generation without existing context."""
    print("\n" + "=" * 60)
    print("TEST 3: NO CONTEXT (fresh conversation start)")
    print("=" * 60)
    print(f"🏷️  Brand: {BRAND.name}")

    request = GenerateRequest(
        brand=BRAND,
        context=None,
        num_turns=4,
        model="hermes3:8b",
        language="ru",
        temperature=0.8
    )

    generator = DialogGenerator(model="hermes3:8b")
    result = await generator.generate_dialog(request)

    print("\n🆕 Generated fresh dialog:")
    for msg in result.messages:
        print(f"  {msg.role.upper()}: {msg.content}")
    print(f"\n⏱️  Generated in {result.generation_params.get('generation_time_ms')}ms")

    return result


async def test_model_comparison():
    """Compare how different models handle the same scenario."""
    print("\n" + "=" * 60)
    print("TEST 4: MODEL COMPARISON")
    print("=" * 60)

    models = ["dolphin3", "hermes3:8b"]

    context = DialogContext(
        messages=SAMPLE_CHAT,
        topic="weekend plans",
        goal="suggest CityRide naturally"
    )

    for model in models:
        print(f"\n🤖 Model: {model}")

        request = GenerateRequest(
            brand=BRAND,
            context=context,
            num_turns=2,
            model=model,
            language="ru",
            temperature=0.8
        )

        generator = DialogGenerator(model=model)
        result = await generator.generate_dialog(request)

        for msg in result.messages:
            print(f"  {msg.role.upper()}: {msg.content}")
        print(f"  ⏱️  {result.generation_params.get('generation_time_ms')}ms")


async def main():
    print("🧪 DIALOG INTEGRATION TEST SUITE")
    print("Testing natural vs forced brand integration\n")

    await test_natural_integration()
    await test_forced_integration()
    await test_no_context()
    await test_model_comparison()

    await ollama.close()
    print("\n✅ All tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
