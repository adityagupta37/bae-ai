from __future__ import annotations
import json
from qna_stylist import ResponseStyleEnhancer, StylistTone
from qna_stylist.settings import Settings


def main() -> None:
    cfg = Settings()
    enhancer = ResponseStyleEnhancer(cfg=cfg)
    question = "Can I get reimbursed if my airport lounge guest pass doesn’t work?"
    answer = "Yes, submit the original receipt within 30 days through our claims portal and note the card number used; refunds show up in 5–7 business days."

    print(f"Active provider: {cfg.provider} ({cfg.active_model()})")
    first = enhancer.enhance(question=question, plain_answer=answer, tone=StylistTone.WITTY)
    print("First call:", json.dumps(first, indent=2, default=str))

    second = enhancer.enhance(question=question, plain_answer=answer, tone=StylistTone.WITTY)
    print("Second call:", json.dumps(second, indent=2, default=str))
    print(f"Cache hit on second call? {'yes' if second.get('cache_hit') else 'no'}")


if __name__ == "__main__":
    main()
