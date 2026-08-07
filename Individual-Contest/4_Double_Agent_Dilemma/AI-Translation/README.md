# AI translations — Double Agent Dilemma (Day 2)

These are the **machine-translated** versions of this task's statement, produced with large language models and used during **IOAI 2026**. They cover **44 languages**, plus the English source.

> **⚠️ These translations are not authoritative and may contain errors.**
> They were generated automatically under time pressure and were *not* verified by a human translator. Mistakes in technical terms, numbers, limits, and edge-case wording are possible.

## Use the reviewed versions instead

For statements that were **read, corrected, and signed off by the delegation team leaders**, see the [`../Translations`](../Translations) folder. Those are the versions that were actually handed to contestants, and they take precedence over anything here whenever the two disagree.

The authoritative source text for this task is [`../statement.md`](../statement.md) (English), with a rendered copy at [`../statement.pdf`](../statement.pdf).

## Layout

```
AI-Translation/
  <Language name> [<code>]/
    statement.md        translated statement
    <image files>       figures referenced by the statement, if any
```

Every statement is named `statement.md` inside its language folder, so paths differ only by language. Folder names follow the language naming used by the translation pipeline: an English language name plus its BCP-47 code in brackets.

## Languages (44 + English)

| Language | Code |
|---|---|
| Albanian | `sq` |
| Amharic | `am` |
| Arabic | `ar` |
| Armenian | `hy` |
| Azerbaijani | `az` |
| Bengali | `bn` |
| Bosnian | `bs` |
| Bulgarian | `bg` |
| Chinese (Simplified) | `zh` |
| Chinese (Traditional) | `zh-Hant` |
| Croatian | `hr` |
| Czech | `cs` |
| Dutch | `nl` |
| English | `en` |
| French | `fr` |
| Georgian | `ka` |
| Greek | `el` |
| Hungarian | `hu` |
| Indonesian | `id` |
| Italian | `it` |
| Japanese | `ja` |
| Kazakh | `kk` |
| Korean | `ko` |
| Kyrgyz | `ky` |
| Latvian | `lv` |
| Malay | `ms` |
| Mongolian | `mn` |
| Montenegrin | `cnr` |
| Nepali | `ne` |
| Persian | `fa` |
| Polish | `pl` |
| Portuguese (Brazilian) | `pt-BR` |
| Portuguese (European) | `pt-PT` |
| Romanian | `ro` |
| Russian | `ru` |
| Serbian | `sr` |
| Slovak | `sk` |
| Spanish | `es` |
| Swedish | `sv` |
| Thai | `th` |
| Turkish | `tr` |
| Ukrainian | `uk` |
| Uzbek | `uz` |
| Vietnamese | `vi` |
| Wolof | `wo` |

**English `[en]`** is not a translation — it is the original source text, byte-identical to `../statement.md`, included so the set is complete. The other 44 entries are the machine translations.

## Provenance

Translations were produced with a mix of frontier models (`openai/gpt-5.6-sol` as primary, with `google/gemini-3.6-flash` and `anthropic/claude-opus-5` as fallbacks) and passed through an automated consistency checker.
